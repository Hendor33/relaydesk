import asyncio, logging, platform, socket
from getpass import getpass
import httpx, typer
from rich.console import Console
from rich.table import Table
from relaydesk_agent.api.client import RelayDeskClient
from relaydesk_agent.core.config import AgentConfig, config_path, load_config, log_path, save_config
from relaydesk_agent.core.runtime import Runtime
app = typer.Typer(help="RelayDesk local automation agent")
console = Console()

def setup_logging():
    path=log_path(); path.parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(level=logging.INFO, handlers=[logging.FileHandler(path), logging.StreamHandler()], format="%(asctime)s %(levelname)s %(message)s")

@app.command()
def pair(api_url: str = typer.Option(..., prompt="RelayDesk URL"), code: str = typer.Option(None)):
    """Pair this computer using a short-lived code from Devices."""
    code = code or getpass("Pairing code: ")
    response = httpx.post(f"{api_url.rstrip('/')}/api/agent/pair", json={"code":code, "name":socket.gethostname(), "hostname":socket.gethostname(), "platform":platform.platform(), "agent_version":"0.1.0"}, timeout=15)
    if response.is_error: console.print(f"[red]Pairing failed:[/] {response.text}"); raise typer.Exit(1)
    data=response.json(); save_config(AgentConfig(api_url=api_url, device_id=data["device_id"], token=data["token"]))
    console.print(f"[green]✓ RelayDesk Agent paired[/]\n\nDevice: {socket.gethostname()}\nRelayDesk: Connected")

@app.command()
def start():
    """Start synchronization, heartbeat, and file watchers."""
    setup_logging(); config=load_config(); console.print("[bold]RelayDesk Agent[/]\n\n[green]✓[/] Starting…")
    try: asyncio.run(Runtime(RelayDeskClient(config), config.sync_interval, config.heartbeat_interval).run())
    except KeyboardInterrupt: console.print("\nAgent stopped")

@app.command()
def status():
    try: c=load_config(); console.print(f"[green]Paired[/]\nDevice: {c.device_id}\nServer: {c.api_url}")
    except FileNotFoundError as exc: console.print(f"[yellow]{exc}[/]")

@app.command()
def doctor():
    table=Table(title="RelayDesk Doctor"); table.add_column("Check"); table.add_column("Result")
    try:
        c=load_config(); table.add_row("Configuration", f"[green]✓[/] {config_path()}")
        async def check():
            client=RelayDeskClient(c)
            try: items=await client.automations(); return f"[green]✓[/] authenticated; {len(items)} automations"
            finally: await client.close()
        table.add_row("RelayDesk", asyncio.run(check()))
    except Exception as exc: table.add_row("Configuration / RelayDesk", f"[red]✕[/] {exc}")
    console.print(table)
