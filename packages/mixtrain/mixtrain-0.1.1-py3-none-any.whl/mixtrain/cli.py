import typer
from rich import print as rprint
from rich.table import Table

from mixtrain import client as mixtrain_client

from . import dataset, secret, provider, routing_cli
from .client import (
    create_workspace,
    delete_workspace,
    list_workspaces,
)

app = typer.Typer(invoke_without_command=True)


@app.callback()
def cli_main(ctx: typer.Context):
    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())
        raise typer.Exit()


@app.command()
def login():
    """Authenticate against the Mixtrain server. Will open a browser window for login."""
    try:
        mixtrain_client.authenticate_browser()
        rprint("[green]✓[/green] Authenticated successfully!")

        # Show new configuration
        show_config()

    except Exception as e:
        rprint(f"[red]Login failed:[/red] {str(e)}")
        rprint("Your previous authentication and workspace settings remain unchanged.")
        raise typer.Exit(1)


workspace_app = typer.Typer(
    help="Manage workspaces", invoke_without_command=True
)


@workspace_app.callback()
def workspace_main(ctx: typer.Context):
    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())
        raise typer.Exit()


@workspace_app.command(name="list")
def list_user_workspaces():
    """List all workspaces you have access to."""
    try:
        data = list_workspaces()
        workspaces = data.get("data", [])
        
        if not workspaces:
            rprint("[yellow]No workspaces found.[/yellow]")
            rprint("Use 'mixtrain workspace create <name>' to create one.")
            return

        # Show workspaces
        rprint("[bold]Your Workspaces:[/bold]")
        table = Table("Name", "Description", "Role", "Members", "Created At")
        for workspace in workspaces:
            table.add_row(
                workspace.get("name", ""),
                workspace.get("description", "")[:50] + "..."
                if len(workspace.get("description", "")) > 50
                else workspace.get("description", ""),
                workspace.get("role", ""),
                str(workspace.get("totalMembers", 0)),
                workspace.get("created_at", ""),
            )
        rprint(table)

    except Exception as e:
        rprint(f"[red]Error:[/red] {str(e)}")
        raise typer.Exit(1)


@workspace_app.command(name="create")
def create_workspace_cmd(
    name: str,
    description: str = typer.Option("", "--description", "-d", help="Workspace description")
):
    """Create a new workspace."""
    try:
        result = create_workspace(name, description)
        workspace_data = result.get("data", {})
        rprint(f"[green]✓[/green] Successfully created workspace '{workspace_data.get('name')}'!")
        
        # Automatically switch to the new workspace
        mixtrain_client.set_workspace(name)
        rprint(f"Switched to workspace: [bold]{name}[/bold]")

    except Exception as e:
        rprint(f"[red]Error:[/red] {str(e)}")
        raise typer.Exit(1)


@workspace_app.command(name="delete")
def delete_workspace_cmd(
    workspace_name: str,
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation prompt")
):
    """Delete a workspace. This will delete all datasets and configurations."""
    try:
        # Confirm deletion unless --yes flag is used
        if not yes:
            confirm = typer.confirm(
                f"Delete workspace '{workspace_name}'? This will permanently delete all datasets, providers, and configurations."
            )
            if not confirm:
                rprint("Deletion cancelled.")
                return

        delete_workspace(workspace_name)
        rprint(f"[green]✓[/green] Successfully deleted workspace '{workspace_name}'!")

    except Exception as e:
        rprint(f"[red]Error:[/red] {str(e)}")
        raise typer.Exit(1)

@app.command()
def config(
    workspace: str = typer.Option(
        None, "--workspace", "-w", help="Set the current workspace"
    ),
    show: bool = typer.Option(False, "--show", help="Show current configuration"),
):
    """Show or modify CLI configuration."""
    if workspace:
        try:
            mixtrain_client.set_workspace(workspace)
            rprint(f"Switched to workspace: [bold]{workspace}[/bold]")
            rprint("\nUpdated configuration:")
            show_config()
        except Exception as e:
            rprint(f"[red]Error:[/red] {str(e)}")
            raise typer.Exit(1)
    else:
        show_config()


def show_config():
    """Show current configuration in a table format"""
    config = mixtrain_client.get_config()

    if not config.workspaces:
        rprint(
            "[yellow]No workspaces configured. Please run 'mixtrain login' first.[/yellow]"
        )
        return

    # Create workspaces table
    table = Table()
    table.add_column("Workspace", style="cyan")
    table.add_column("Status", style="green")

    for workspace in config.workspaces:
        status = "[green]✓ Current[/green]" if workspace.active else ""
        table.add_row(workspace.name, status)

    rprint(table)


app.add_typer(dataset.app, name="dataset")
app.add_typer(workspace_app, name="workspace")
app.add_typer(provider.app, name="provider")
app.add_typer(secret.app, name="secret")
app.add_typer(routing_cli.app, name="routing")
# app.add_typer(train.app, name="train")
# app.add_typer(eval.app, name="eval")


def main():
    app()


if __name__ == "__main__":
    main()
