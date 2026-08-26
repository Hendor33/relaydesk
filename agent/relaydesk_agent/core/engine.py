from typing import Any, Awaitable, Callable
from relaydesk_agent.actions.files import ACTIONS
from relaydesk_agent.conditions.evaluator import ConditionEvaluator
from relaydesk_agent.models.automation import Automation

Reporter = Callable[[str, dict[str, Any]], Awaitable[None]]

class AutomationEngine:
    def __init__(self, reporter: Reporter | None = None):
        self.conditions = ConditionEvaluator()
        self.reporter = reporter

    async def execute(self, automation: Automation, context: dict[str, Any]) -> bool:
        try:
            if self.reporter:
                await self.reporter("running", {"context": context})
            for condition in sorted(automation.conditions, key=lambda item: item.position):
                if not self.conditions.evaluate(condition.type, condition.config, context):
                    if self.reporter:
                        await self.reporter("success", {"message": "Conditions did not match"})
                    return False
            for definition in sorted(automation.actions, key=lambda item: item.position):
                action = ACTIONS.get(definition.type)
                if action is None:
                    raise ValueError(f"Unsupported action: {definition.type}")
                context = await action.execute(context, definition.config)
            if self.reporter:
                await self.reporter("success", {"context": context})
            return True
        except Exception as exc:
            if self.reporter:
                await self.reporter("failed", {"error": str(exc), "context": context})
            return False
