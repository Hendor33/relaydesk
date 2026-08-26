from pathlib import Path
import pytest
from relaydesk_agent.actions.files import MoveFileAction, RenameFileAction
from relaydesk_agent.conditions.evaluator import ConditionEvaluator
from relaydesk_agent.core.engine import AutomationEngine
from relaydesk_agent.core.paths import validated_path
from relaydesk_agent.models.automation import Automation
from relaydesk_agent.triggers.file_created import EventDeduplicator

def context(path: Path): return {"file":{"path":str(path), "name":path.name, "extension":path.suffix, "size":path.stat().st_size}}

def test_extension_condition_is_case_insensitive(tmp_path):
    path=tmp_path/"file.PDF"; path.write_text("x")
    assert ConditionEvaluator().evaluate("file_extension", {"operator":"equals", "value":".pdf"}, context(path))

@pytest.mark.asyncio
async def test_move_file(tmp_path):
    source=tmp_path/"a.txt"; destination=tmp_path/"out"; destination.mkdir(); source.write_text("hello")
    result=await MoveFileAction().execute(context(source), {"destination":str(destination)})
    assert Path(result["file"]["path"]) == destination/"a.txt" and not source.exists()

@pytest.mark.asyncio
async def test_rename_file(tmp_path):
    source=tmp_path/"a.txt"; source.write_text("hello")
    result=await RenameFileAction().execute(context(source), {"name":"b.pdf"})
    assert Path(result["file"]["path"]).name == "b.pdf" and result["file"]["extension"] == ".pdf"

@pytest.mark.asyncio
async def test_execution_order_updates_context(tmp_path):
    source=tmp_path/"a.txt"; out=tmp_path/"out"; out.mkdir(); source.write_text("x")
    automation=Automation(id="1", name="test", trigger={"type":"file_created","config":{"path":str(tmp_path)}}, actions=[{"type":"move_file","position":2,"config":{"destination":str(out)}},{"type":"rename_file","position":1,"config":{"name":"renamed.txt"}}])
    assert await AutomationEngine().execute(automation, context(source))
    assert (out/"renamed.txt").exists()

@pytest.mark.asyncio
async def test_failed_action_is_reported_and_does_not_raise(tmp_path):
    source=tmp_path/"a"; source.write_text("x"); reports=[]
    async def report(status, payload): reports.append((status,payload))
    automation=Automation(id="1",name="x",trigger={"type":"file_created","config":{"path":str(tmp_path)}},actions=[{"type":"move_file","config":{"destination":str(tmp_path/"missing")}}])
    assert not await AutomationEngine(report).execute(automation, context(source))
    assert reports[-1][0] == "failed" and "does not exist" in reports[-1][1]["error"]

def test_path_validation_rejects_relative_and_traversal(tmp_path):
    with pytest.raises(ValueError, match="absolute"): validated_path("relative/file")
    with pytest.raises(ValueError, match="traversal"): validated_path(str(tmp_path/".."/"escape"), must_exist=False)

def test_event_deduplication():
    dedupe=EventDeduplicator(ttl=5)
    assert dedupe.accept("a", 10) and not dedupe.accept("a", 11) and dedupe.accept("a", 16)
