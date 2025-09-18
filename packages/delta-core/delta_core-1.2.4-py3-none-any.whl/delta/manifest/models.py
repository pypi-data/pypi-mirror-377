from typing import Any

from pydantic import BaseModel, Field


class Copyright(BaseModel):
    company: str = ""
    years: list[int] = [2024]


class License(BaseModel):
    name: str = "LGPLv3"
    url: str = "https://www.gnu.org/licenses/gpl-3.0.txt"
    description: str = ""
    copyrights: list[Copyright] = Field(default_factory=list)


class Parameter(BaseModel):
    name: str
    type: str
    description: str | None = None


class Resource(Parameter):
    value: Any


class Input(Parameter):
    value: Any | None = None


class InputModel(Input):
    prefix: str | None = None


class Output(Parameter):
    pass


class OutputModel(Output):
    glob: str


class Model(BaseModel):
    path: str
    type: str
    parameters: dict[str, Any] | None = None
    inputs: dict[str, InputModel] | None = None
    outputs: dict[str, OutputModel] | None = None


class Dependency(BaseModel):
    id: str
    version: str


class Manifest(BaseModel):
    name: str
    description: str = ""
    license: License = Field(default_factory=License)
    short_description: str | None = None
    owner: str
    resources: dict[str, Resource] | None = None
    inputs: dict[str, Input] | None = None
    outputs: dict[str, Output] | None = None
    models: dict[str, Model] | None = None
    dependencies: dict[str, Dependency] | None = None
