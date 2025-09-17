import armonik_cli_core as akcc
from rich.table import Table

from importlib.metadata import entry_points


@akcc.group(name="extension")
def extensions(**kwargs):
    """Discover and manage installed CLI extensions."""
    pass


@extensions.command("list")
def list_extensions():
    """List all discoverable extensions."""
    try:
        eps = entry_points(group=akcc.groups.ENTRY_POINT_GROUP)
    except Exception as e:
        akcc.console.print(f"[red]Error discovering entry points: {e}[/red]")
        raise akcc.Exit(1)

    if not eps:
        akcc.console.print("[yellow]No extensions found.[/yellow]")
        return

    table = Table(title="Installed ArmoniK CLI Extensions")
    table.add_column("Command Name", style="cyan", no_wrap=True)
    table.add_column("Providing Package", style="magenta")
    table.add_column("Version", style="green")
    table.add_column("Status", style="green")

    for ep in eps:
        package_name = "Unknown"
        version = "N/A"
        if ep.dist:
            package_name = ep.dist.name
            version = ep.dist.version

        # Try to load the extension to check its status
        try:
            ep.load()
            status = "[green]OK[/green]"
        except Exception:
            status = "[red]Broken[/red]"

        table.add_row(ep.name, package_name, version, status)

    akcc.console.print(table)
