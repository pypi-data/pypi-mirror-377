from operaton.tasks import operaton_session
from operaton.tasks import settings as operaton_settings
from operaton.tasks import stream_handler
from operaton.tasks.types import CompleteExternalTaskDto
from operaton.tasks.types import ExternalTaskBpmnError
from operaton.tasks.types import ExternalTaskComplete
from operaton.tasks.types import ExternalTaskFailure
from operaton.tasks.types import ExternalTaskFailureDto
from operaton.tasks.types import LockedExternalTaskDto
from operaton.tasks.types import PatchVariablesDto
from operaton.tasks.types import VariableValueDto
from operaton.tasks.types import VariableValueType
from pathlib import Path
from purjo.config import OnFail
from purjo.config import settings
from purjo.utils import inline_screenshots
from purjo.utils import json_serializer
from purjo.utils import lazydecode
from purjo.utils import operaton_from_py
from purjo.utils import py_from_operaton
from pydantic import BaseModel
from pydantic import DirectoryPath
from pydantic import Field
from pydantic import FilePath
from tempfile import TemporaryDirectory
from typing import Callable
from typing import Coroutine
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple
from typing import Union
from zipfile import ZipFile
import asyncio
import base64
import importlib.resources
import json
import logging
import os
import re
import shutil


logger = logging.getLogger(__name__)
logger.addHandler(stream_handler)
logger.setLevel(operaton_settings.LOG_LEVEL)


async def run(
    program: str, args: List[str], cwd: Path, env: Dict[str, str]
) -> Tuple[int, bytes, bytes]:
    proc = await asyncio.create_subprocess_exec(
        program,
        *args,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        cwd=cwd,
        env=os.environ | env | {"PYTHONPATH": ""},
    )

    stdout, stderr = await proc.communicate()
    stdout = stdout.strip() or b""
    stderr = stderr.strip() or b""

    if stderr:
        logger.debug("%s", lazydecode(stderr))
    if stdout:
        logger.debug("%s", lazydecode(stdout))

    logger.debug(f"exit code {proc.returncode}")

    return proc.returncode or 0, stdout, stderr


def fail_reason(path: Path) -> str:
    """Extract the reason for the failure from the output.xml file."""
    xml = path.read_text()
    reason = ""
    for match in re.findall(r'status="FAIL"[^>]*.([^<]*)', xml, re.M):
        match = match.strip()
        reason = match if match else reason
    return reason


class Task(BaseModel):
    name: Optional[str] = None
    include: Optional[str] = None
    exclude: Optional[str] = None
    on_fail: Optional[OnFail] = Field(default=None, alias="on-fail")
    process_variables: bool = Field(default=False, alias="process-variables")


def is_python_fqfn(value: str) -> bool:
    """Check if a string looks like a fully qualified function name (fqfn)."""
    return bool(re.match(r"^[a-zA-Z_][\w\.]*\.[a-zA-Z_][\w]*$", value))


def build_run(
    config: Task,
    robot_dir: str,
    working_dir: str,
    task_variables_file: Path,
    process_variables_file: Path,
) -> Coroutine[None, None, Tuple[int, bytes, bytes]]:
    is_python = config.name and is_python_fqfn(config.name)
    return run(
        settings.UV_EXECUTABLE,
        [
            "run",
            "--link-mode",
            "copy",
            "--project",
            robot_dir,
        ]
        + (
            [
                "--offline",
                "--cache-dir",
                str(Path(working_dir) / ".cache"),
            ]
            if (Path(working_dir) / ".cache").is_dir()
            else []
        )
        + [
            "--",
            "robot",
        ]
        + (
            [
                "-t",
                config.name,
            ]
            if config.name
            else []
        )
        + (
            [
                "-i",
                config.include,
            ]
            if config.include
            else []
        )
        + (
            [
                "-e",
                config.exclude,
            ]
            if config.exclude
            else []
        )
        + [
            "--pythonpath",
            working_dir,
            "--pythonpath",
            robot_dir,
            "--parser",
            (
                "RobotParser"
                if not is_python
                else f"RobotParser.PythonParser:{config.name}"
            ),
            "--variablefile",
            "variables.json",
            "--outputdir",
            working_dir,
            robot_dir,
        ],
        Path(working_dir),
        {
            "BPMN_PROCESS_SCOPE": str(process_variables_file),
            "BPMN_TASK_SCOPE": str(task_variables_file),
            "UV_NO_SYNC": "0",
            "VIRTUAL_ENV": "",
        },
    )


def create_task(
    config: Task,
    robot: Union[FilePath, DirectoryPath],
    on_fail: OnFail,
    semaphore: asyncio.Semaphore,
) -> Callable[
    [LockedExternalTaskDto],
    Coroutine[None, None, Union[ExternalTaskComplete, ExternalTaskFailure]],
]:
    async def execute_task(
        task: LockedExternalTaskDto,
    ) -> Union[ExternalTaskComplete, ExternalTaskFailure]:
        async with semaphore:
            robot_parser = (
                importlib.resources.files("purjo.data") / "RobotParser.py"
            ).read_text()
            with TemporaryDirectory() as robot_dir, TemporaryDirectory() as working_dir:
                variables = await py_from_operaton(
                    task.variables, task, Path(working_dir)
                ) | {
                    "BPMN:PROCESS": "BPMN:PROCESS",
                    "BPMN:TASK": "BPMN:TASK",
                }
                if robot.is_dir():
                    shutil.copytree(robot, robot_dir, dirs_exist_ok=True)
                else:
                    with ZipFile(robot, "r") as fp:
                        fp.extractall(robot_dir)
                        if (Path(robot_dir) / ".cache").is_dir():
                            shutil.move(Path(robot_dir) / ".cache", working_dir)
                (Path(working_dir) / "variables.json").write_text(
                    json.dumps(variables, default=json_serializer)
                )
                (Path(working_dir) / "RobotParser.py").write_text(robot_parser)
                task_variables_file = Path(working_dir) / "task_variables.json"
                task_variables_file.write_text("{}")
                process_variables_file = Path(working_dir) / "process_variables.json"
                process_variables_file.write_text("{}")
                return_code, stdout, stderr = await build_run(
                    config,
                    robot_dir,
                    working_dir,
                    task_variables_file,
                    process_variables_file,
                )
                task_variables = operaton_from_py(
                    json.loads(task_variables_file.read_text()),
                    [Path(robot_dir), Path(working_dir)],
                )
                process_variables = operaton_from_py(
                    json.loads(process_variables_file.read_text()),
                    [Path(robot_dir), Path(working_dir)],
                )
                for name_, variable in (task.variables or {}).items():
                    if name_ in task_variables and task_variables[name_].value is None:
                        task_variables[name_].type = variable.type
                    if name_ in process_variables:
                        process_variables[name_].type = variable.type
                log_html_path = Path(working_dir) / "log.html"
                if log_html_path.exists():
                    inline_screenshots(log_html_path)
                    task_variables["log.html"] = VariableValueDto(
                        value=base64.b64encode(log_html_path.read_bytes()),
                        type=VariableValueType.File,
                        valueInfo={
                            "filename": "log.html",
                            "mimetype": "text/html",
                            "mimeType": "text/html",
                            "encoding": "utf-8",
                        },
                    )
                output_xml_path = Path(working_dir) / "output.xml"
                if output_xml_path.exists():
                    inline_screenshots(output_xml_path)
                    task_variables["output.xml"] = VariableValueDto(
                        value=base64.b64encode(output_xml_path.read_bytes()),
                        type=VariableValueType.File,
                        valueInfo={
                            "filename": "output.xml",
                            "mimetype": "text/xml",
                            "mimeType": "text/xml",
                            "encoding": "utf-8",
                        },
                    )
                if return_code == 0 or on_fail == OnFail.COMPLETE:
                    if return_code != 0:
                        fail_reason_ = (
                            fail_reason(output_xml_path)
                            if output_xml_path.exists()
                            else ""
                        )
                        task_variables.update(
                            {
                                "errorCode": VariableValueDto(
                                    value=fail_reason_.split("\n", 1)[0].strip(),
                                    type=VariableValueType.String,
                                ),
                                "errorMessage": VariableValueDto(
                                    value=fail_reason_.split("\n", 1)[-1].strip(),
                                    type=VariableValueType.String,
                                ),
                            }
                        )
                    elif on_fail == OnFail.COMPLETE:
                        task_variables.update(
                            {
                                "errorCode": VariableValueDto(
                                    value=None,
                                    type=VariableValueType.Null,
                                ),
                                "errorMessage": VariableValueDto(
                                    value=None,
                                    type=VariableValueType.Null,
                                ),
                            }
                        )
                    return ExternalTaskComplete(
                        task=task,
                        response=CompleteExternalTaskDto(
                            workerId=task.workerId,
                            localVariables=task_variables,
                            variables=process_variables,
                        ),
                    )
                else:
                    async with operaton_session() as session:
                        resp = await session.post(
                            f"{operaton_settings.ENGINE_REST_BASE_URL}/execution/{task.executionId}/localVariables",
                            data=PatchVariablesDto(
                                modifications={
                                    "log.html": task_variables["log.html"],
                                    "output.xml": task_variables["output.xml"],
                                }
                            ).model_dump_json(),
                        )
                        resp.raise_for_status()
                    fail_reason_ = (
                        fail_reason(output_xml_path) if output_xml_path.exists() else ""
                    )
                    return (
                        ExternalTaskComplete(
                            task=task,
                            response=ExternalTaskBpmnError(
                                workerId=task.workerId,
                                errorCode=fail_reason_.split("\n", 1)[0].strip(),
                                errorMessage=fail_reason_.split("\n", 1)[-1].strip(),
                                variables=process_variables,
                            ),
                        )
                        if on_fail == OnFail.ERROR
                        else ExternalTaskFailure(
                            task=task,
                            response=ExternalTaskFailureDto(
                                workerId=task.workerId,
                                errorMessage=fail_reason_,
                                errorDetails=(stdout + stderr).decode("utf-8"),
                                retries=0,
                                retryTimeout=0,
                            ),
                        )
                    )

    return execute_task
