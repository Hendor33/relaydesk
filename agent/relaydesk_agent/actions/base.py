from abc import ABC, abstractmethod
from typing import Any

class BaseAction(ABC):
    type: str
    @abstractmethod
    async def execute(self, context: dict[str, Any], config: dict[str, Any]) -> dict[str, Any]: ...
