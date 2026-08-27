import json, os
from pathlib import Path
from pydantic import BaseModel, HttpUrl
from platformdirs import user_config_path, user_log_path

class AgentConfig(BaseModel):
    api_url: HttpUrl
    device_id: str
    token: str
    sync_interval: float = 30
    heartbeat_interval: float = 30

def config_path() -> Path: return user_config_path("RelayDesk", appauthor=False) / "config.json"
def log_path() -> Path: return user_log_path("RelayDesk", appauthor=False) / "agent.log"
def load_config() -> AgentConfig:
    path = config_path()
    if not path.exists(): raise FileNotFoundError("Agent is not paired. Run relaydesk-agent pair.")
    return AgentConfig.model_validate_json(path.read_text())
def save_config(config: AgentConfig):
    path = config_path(); path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(config.model_dump_json(indent=2)); os.chmod(path, 0o600)
