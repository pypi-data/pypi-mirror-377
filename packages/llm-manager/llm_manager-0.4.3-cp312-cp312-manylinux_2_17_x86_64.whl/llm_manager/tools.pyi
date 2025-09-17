import pathlib
from abc import abstractmethod, ABC
from docker.models.containers import Container
from fastmcp.tools import FunctionTool
from llm_manager.message import Message
from llm_manager.cython import CythonBaseModel
from pydantic import BaseModel, Field
from typing import Any, Literal

class ToolModel(CythonBaseModel, ABC):
    @classmethod
    def to_schema(cls) -> dict[str, Any]: ...
    @classmethod
    def to_json_schema(cls) -> str: ...
    @classmethod
    def to_mcp_tool(cls) -> list[FunctionTool]: ...
    @abstractmethod
    def __call__(self, *args, **kwargs) -> Any: ...

class MCPToolModel(ToolModel, ABC):
    type: Literal["sse", "streamable-http"] = "streamable-http"
    server_url: str
    auth: str | None = None
    allowed_tools: list[str] | None = None
    tool_name: str
    @classmethod
    def to_schema(cls) -> list[dict[str, Any]]: ...
    def __call__(self, *args, **kwargs) -> str: ...

class LocalCodeInterpreter(ToolModel):
    code: str = Field(description="Please provide the Python code to be executed")
    requirements: list[str] = Field(default_factory=list, description="List of dependencies to be installed via pip")
    timeout: int = Field(default=300, description="The maximum execution timeout in seconds")
    def _install_requirements(self, work_dir: pathlib.Path, result: dict[str, Any]) -> bool: ...
    def __call__(self) -> str: ...

class ContainerManager(CythonBaseModel):
    image: str = Field(default="python:3.11-slim", description="Docker image used to create the container (default: python:3.11-slim).")
    mem_limit: str = Field(default="512m", description="Maximum memory allocated to the container, e.g., '512m', '1g'.")
    cpus: float = Field(default=1.0, description="Number of CPUs allocated to the container (fractional values allowed).")
    pids_limit: int = Field(default=256, description="Maximum number of process IDs (PIDs) allowed in the container.")
    id: str | None = Field(default=None, description="Container ID. If None, a new container will be created.")
    def _start(self) -> Container: ...
    def start(self) -> str: ...
    def stop(self) -> None: ...
    def remove(self) -> None: ...
    def read_file(self, path: str) -> bytes | None: ...

class BaseResult(BaseModel):
    return_code: int
    stdout: str
    stderr: str

class ExecutionResult(BaseResult):
    duration: float
    container_id: str
    image: str
    files: list[str]

class CodeInterpreter(ToolModel):
    code: str = Field(description="Please provide the Python code to be executed")
    requirements: list[str] = Field(default_factory=list, description="List of dependencies to be installed via pip")
    timeout: int = Field(default=300, description="The maximum execution timeout in seconds")
    image: str = Field(default="python:3.11-slim", description="Docker image used to create the container (default: python:3.11-slim).")
    mem_limit: str = Field(default="512m", description="Maximum memory allocated to the container, e.g., '512m', '1g'.")
    cpus: float = Field(default=1.0, description="Number of CPUs allocated to the container (fractional values allowed).")
    pids_limit: int = Field(default=256, description="Maximum number of process IDs (PIDs) allowed in the container.")
    id: str | None = Field(default=None, description="Container ID. If None, a new container will be created.")
    def __init__(self, **data: Any): ...
    @property
    def container(self) -> ContainerManager: ...
    @staticmethod
    def _make_tar(path: pathlib.Path) -> bytes: ...
    @staticmethod
    def _output_parse(exec_id: dict[str, str]) -> BaseResult: ...
    def _install_requirements(self) -> None: ...
    def __call__(self) -> dict[str, Any]: ...

class Tools(CythonBaseModel):
    models: list[type[ToolModel]]
    schemas: list[dict[str, Any]] = Field(default_factory=list)
    namespace: dict[str, type[ToolModel]] = Field(default_factory=dict)
    def __init__(self, *models: type[ToolModel]) -> None: ...
    def fresh(self) -> None: ...
    def __call__(self, tool_calls: list[dict[str, Any]]) -> list[Message]: ...
    def __add__(self, other: "Tools") -> "Tools": ...
    def __bool__(self) -> bool: ...
