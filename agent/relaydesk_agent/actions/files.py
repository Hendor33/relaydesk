import shutil
from pathlib import Path
from typing import Any
from .base import BaseAction
from relaydesk_agent.core.paths import destination_for, validated_path

def _updated(context: dict[str, Any], path: Path) -> dict[str, Any]:
    context["file"].update(path=str(path), name=path.name, extension=path.suffix, size=path.stat().st_size)
    return context

class MoveFileAction(BaseAction):
    type = "move_file"
    async def execute(self, context: dict[str, Any], config: dict[str, Any]) -> dict[str, Any]:
        source = validated_path(context["file"]["path"], directory=False)
        target = destination_for(str(config.get("destination", "")), source)
        return _updated(context, Path(shutil.move(str(source), str(target))))

class CopyFileAction(BaseAction):
    type = "copy_file"
    async def execute(self, context: dict[str, Any], config: dict[str, Any]) -> dict[str, Any]:
        source = validated_path(context["file"]["path"], directory=False)
        target = destination_for(str(config.get("destination", "")), source)
        return _updated(context, Path(shutil.copy2(source, target)))

class RenameFileAction(BaseAction):
    type = "rename_file"
    async def execute(self, context: dict[str, Any], config: dict[str, Any]) -> dict[str, Any]:
        source = validated_path(context["file"]["path"], directory=False)
        name = str(config.get("name", ""))
        if not name or Path(name).name != name or name in {".", ".."}:
            raise ValueError("Rename target must be a safe file name.")
        target = destination_for(str(source.parent), source, name)
        source.rename(target)
        return _updated(context, target)

ACTIONS = {a.type: a for a in (MoveFileAction(), CopyFileAction(), RenameFileAction())}
