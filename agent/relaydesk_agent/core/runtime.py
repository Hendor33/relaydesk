import asyncio, logging
from pathlib import Path
from relaydesk_agent.api.client import RelayDeskClient
from relaydesk_agent.core.engine import AutomationEngine
from relaydesk_agent.models.automation import Automation
from relaydesk_agent.triggers.file_created import FileCreatedTrigger

log = logging.getLogger("relaydesk")
class Runtime:
    def __init__(self, client: RelayDeskClient, sync_interval=30, heartbeat_interval=30):
        self.client, self.sync_interval, self.heartbeat_interval = client, sync_interval, heartbeat_interval
        self.triggers, self.signature, self.running = [], "", True
    async def reconcile(self):
        automations = await self.client.automations()
        signature = repr([a.model_dump() for a in automations])
        if signature == self.signature: return
        for trigger in self.triggers: await trigger.stop()
        self.triggers = []
        for automation in automations:
            path = str(automation.trigger.config.get("path", ""))
            trigger = FileCreatedTrigger(path, lambda file, a=automation: self.handle(a, file))
            await trigger.start(); self.triggers.append(trigger)
        self.signature = signature
        log.info("automations_loaded", extra={"count": len(automations)})
    async def handle(self, automation: Automation, file: Path):
        context = {"event":"file_created", "device_id": self.client.config.device_id, "file":{"path":str(file), "name":file.name, "extension":file.suffix, "size":file.stat().st_size}}
        execution_id = await self.client.execution(automation.id, "running", context)
        async def report(status, payload): await self.client.execution(automation.id, status, payload, execution_id)
        await AutomationEngine(report).execute(automation, context)
    async def run(self):
        async def heartbeat():
            while self.running:
                try: await self.client.heartbeat()
                except Exception: log.exception("heartbeat_failed")
                await asyncio.sleep(self.heartbeat_interval)
        task = asyncio.create_task(heartbeat())
        try:
            while self.running:
                try: await self.reconcile()
                except Exception: log.exception("reconciliation_failed")
                await asyncio.sleep(self.sync_interval)
        finally:
            self.running=False; task.cancel()
            for trigger in self.triggers: await trigger.stop()
            await self.client.close()
