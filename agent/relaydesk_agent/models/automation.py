from __future__ import annotations
from typing import Any, Literal
from pydantic import BaseModel, Field

class TriggerDefinition(BaseModel):
    type: Literal["file_created"]
    config: dict[str, Any]

class ConditionDefinition(BaseModel):
    type: Literal["file_extension"]
    position: int = 0
    config: dict[str, Any]

class ActionDefinition(BaseModel):
    type: Literal["move_file", "copy_file", "rename_file"]
    position: int = 0
    config: dict[str, Any]

class Automation(BaseModel):
    id: str
    name: str
    trigger: TriggerDefinition
    conditions: list[ConditionDefinition] = Field(default_factory=list)
    actions: list[ActionDefinition] = Field(default_factory=list)
