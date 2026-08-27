import asyncio
import time
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Awaitable, Callable
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
from relaydesk_agent.core.paths import validated_path

class EventDeduplicator:
    def __init__(self, ttl: float = 5): self.ttl, self._seen = ttl, {}
    def accept(self, path: str, now: float | None = None) -> bool:
        now = now if now is not None else time.monotonic()
        self._seen = {p: t for p, t in self._seen.items() if now - t < self.ttl}
        if path in self._seen: return False
        self._seen[path] = now
        return True

async def wait_until_stable(path: Path, interval: float = 0.5, checks: int = 2) -> bool:
    previous = -1
    for _ in range(checks):
        if not path.is_file(): return False
        size = path.stat().st_size
        if size == previous: return True
        previous = size
        await asyncio.sleep(interval)
    return path.is_file() and path.stat().st_size == previous

class BaseTrigger(ABC):
    type: str
    @abstractmethod
    async def start(self): ...
    @abstractmethod
    async def stop(self): ...

class _Handler(FileSystemEventHandler):
    def __init__(self, callback: Callable[[str], None]): self.callback = callback
    def on_created(self, event):
        if not event.is_directory: self.callback(event.src_path)

class FileCreatedTrigger(BaseTrigger):
    type = "file_created"
    def __init__(self, path: str, callback: Callable[[Path], Awaitable[None]]):
        self.path, self.callback = validated_path(path, directory=True), callback
        self.observer, self.loop, self.dedupe = Observer(), None, EventDeduplicator()
    async def start(self):
        self.loop = asyncio.get_running_loop()
        def dispatch(path: str):
            if self.dedupe.accept(path): asyncio.run_coroutine_threadsafe(self._dispatch(Path(path)), self.loop)
        self.observer.schedule(_Handler(dispatch), str(self.path), recursive=False)
        self.observer.start()
    async def _dispatch(self, path: Path):
        if await wait_until_stable(path): await self.callback(path)
    async def stop(self):
        self.observer.stop(); self.observer.join(timeout=5)
