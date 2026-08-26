import asyncio
from typing import Any
import httpx
from relaydesk_agent.core.config import AgentConfig
from relaydesk_agent.models.automation import Automation

class RelayDeskClient:
    def __init__(self, config: AgentConfig):
        self.config = config
        self.client = httpx.AsyncClient(base_url=str(config.api_url).rstrip('/'), timeout=15, headers={"Authorization": f"Bearer {config.token}", "X-Device-ID": config.device_id})
    async def _request(self, method: str, path: str, **kwargs) -> Any:
        error = None
        for delay in (0, 1, 2, 4):
            if delay: await asyncio.sleep(delay)
            try:
                response = await self.client.request(method, path, **kwargs); response.raise_for_status()
                return response.json() if response.content else None
            except (httpx.TransportError, httpx.HTTPStatusError) as exc: error = exc
        raise RuntimeError(f"RelayDesk request failed: {error}")
    async def automations(self) -> list[Automation]:
        return [Automation.model_validate(item) for item in await self._request("GET", "/api/agent/automations")]
    async def heartbeat(self): await self._request("POST", "/api/agent/heartbeat")
    async def execution(self, automation_id: str, status: str, payload: dict[str, Any], execution_id: str | None = None) -> str:
        data = await self._request("POST", "/api/agent/executions", json={"automation_id": automation_id, "execution_id": execution_id, "status": status, "payload": payload})
        return data["id"]
    async def close(self): await self.client.aclose()
