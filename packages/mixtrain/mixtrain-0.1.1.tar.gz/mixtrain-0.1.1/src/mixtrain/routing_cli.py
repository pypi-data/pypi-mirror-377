"""CLI commands for routing engine functionality."""

import json
import sys
from pathlib import Path
from typing import Optional, Dict, Any, List

import typer
from rich import print as rprint
from rich.console import Console
from rich.table import Table
from rich.syntax import Syntax
from rich.panel import Panel

from .routing import (
    RoutingEngine,
    RoutingEngineFactory,
    RoutingValidator,
    RoutingStrategy,
    ConfigBuilder,
    ValidationError,
    ConfigurationLinter,
)


app = typer.Typer(help="Routing engine commands", invoke_without_command=True)
console = Console()


@app.callback()
def routing_main(ctx: typer.Context):
    """Routing engine commands for local testing and configuration management."""
    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())
        raise typer.Exit()


@app.command()
def create(
    name: str = typer.Argument(help="Configuration name"),
    output: Optional[str] = typer.Option(None, "-o", "--output", help="Output file path"),
    interactive: bool = typer.Option(False, "-i", "--interactive", help="Interactive configuration builder")
):
    """Create a new routing configuration."""
    try:
        if interactive:
            config = _interactive_config_builder(name)
        else:
            # Create a simple default configuration
            endpoint = typer.prompt("Default endpoint URL")
            config = ConfigBuilder(name, "Default routing configuration").add_rule(
                "default", description="Route all requests to default endpoint"
            ).add_target("custom", "default", endpoint).build()

        config_json = config.to_json()

        if output:
            with open(output, 'w') as f:
                json.dump(config_json, f, indent=2)
            rprint(f"[green]✓[/green] Configuration saved to {output}")
        else:
            rprint("[bold]Generated Configuration:[/bold]")
            syntax = Syntax(json.dumps(config_json, indent=2), "json", theme="monokai")
            console.print(syntax)

    except Exception as e:
        rprint(f"[red]Error:[/red] {str(e)}")
        raise typer.Exit(1)


@app.command()
def validate(
    config_file: str = typer.Argument(help="Configuration file to validate"),
    verbose: bool = typer.Option(False, "-v", "--verbose", help="Show detailed validation results")
):
    """Validate a routing configuration file."""
    try:
        config_path = Path(config_file)
        if not config_path.exists():
            rprint(f"[red]Error:[/red] Configuration file '{config_file}' not found")
            raise typer.Exit(1)

        with open(config_path) as f:
            config_data = json.load(f)

        # Handle different config formats
        config_data = _normalize_config_format(config_data)

        # Validate configuration
        errors = RoutingValidator.validate_config_dict(config_data)

        if verbose:
            # Run linter for comprehensive analysis
            try:
                from .routing.models import RoutingConfig
                config = RoutingConfig.from_json(config_data)
                lint_results = ConfigurationLinter.lint_config(config)

                _display_lint_results(lint_results)
            except Exception as e:
                rprint(f"[yellow]Warning:[/yellow] Could not run linter: {e}")

        if errors:
            rprint(f"[red]✗ Validation failed with {len(errors)} errors:[/red]")
            for i, error in enumerate(errors, 1):
                rprint(f"  {i}. {error}")
            raise typer.Exit(1)
        else:
            rprint("[green]✓ Configuration is valid![/green]")

    except json.JSONDecodeError as e:
        rprint(f"[red]Error:[/red] Invalid JSON in configuration file: {e}")
        raise typer.Exit(1)
    except Exception as e:
        _handle_config_error(e, config_file)
        raise typer.Exit(1)


@app.command()
def test(
    config_file: str = typer.Argument(help="Configuration file to test"),
    request_file: Optional[str] = typer.Option(None, "-r", "--request", help="JSON file containing request data"),
    request_data: Optional[str] = typer.Option(None, "-d", "--data", help="JSON string with request data"),
    expected_rule: Optional[str] = typer.Option(None, "-e", "--expected", help="Expected rule name"),
    verbose: bool = typer.Option(False, "-v", "--verbose", help="Show detailed results")
):
    """Test routing against sample request data."""
    try:
        # Load configuration
        config_path = Path(config_file)
        if not config_path.exists():
            rprint(f"[red]Error:[/red] Configuration file '{config_file}' not found")
            raise typer.Exit(1)

        # Load and normalize config
        with open(config_path) as f:
            config_data = json.load(f)
        config_data = _normalize_config_format(config_data)
        engine = RoutingEngineFactory.from_json(config_data)

        # Get request data
        if request_file:
            with open(request_file) as f:
                request_data_dict = json.load(f)
        elif request_data:
            request_data_dict = json.loads(request_data)
        else:
            # Interactive input
            request_data_dict = _interactive_request_builder()

        # Route the request
        result = engine.test_request(request_data_dict, expected_rule)

        # Display results
        _display_routing_result(result, verbose)

        # Exit with error code if test failed expectation
        if expected_rule and result.metadata.get("matched_expected") is False:
            raise typer.Exit(1)

    except json.JSONDecodeError as e:
        rprint(f"[red]Error:[/red] Invalid JSON: {e}")
        raise typer.Exit(1)
    except Exception as e:
        _handle_config_error(e, config_file)
        raise typer.Exit(1)


@app.command()
def coverage(
    config_file: str = typer.Argument(help="Configuration file to analyze"),
    test_requests: str = typer.Argument(help="JSON file containing array of test requests")
):
    """Analyze rule coverage for a set of test requests."""
    try:
        # Load configuration and test data
        with open(config_file) as f:
            config_data = json.load(f)
        config_data = _normalize_config_format(config_data)
        engine = RoutingEngineFactory.from_json(config_data)

        with open(test_requests) as f:
            requests_data = json.load(f)

        if not isinstance(requests_data, list):
            rprint("[red]Error:[/red] Test requests file must contain an array of request objects")
            raise typer.Exit(1)

        # Analyze coverage
        coverage_results = engine.get_rule_coverage(requests_data)

        # Display results
        _display_coverage_results(coverage_results)

        # Exit with error if coverage is poor
        if coverage_results["coverage_percentage"] < 80:
            rprint(f"\n[yellow]Warning:[/yellow] Rule coverage is below 80% ({coverage_results['coverage_percentage']:.1f}%)")
            raise typer.Exit(1)

    except Exception as e:
        _handle_config_error(e, config_file)
        raise typer.Exit(1)


@app.command()
def explain(
    config_file: str = typer.Argument(help="Configuration file to explain"),
    format: str = typer.Option("table", "-f", "--format", help="Output format: table, json, markdown")
):
    """Explain the routing configuration in human-readable format."""
    try:
        with open(config_file) as f:
            config_data = json.load(f)

        # Handle different config formats
        config_data = _normalize_config_format(config_data)

        from .routing.models import RoutingConfig
        config = RoutingConfig.from_json(config_data)

        if format == "json":
            rprint(json.dumps(config.to_json(), indent=2))
        elif format == "markdown":
            _display_config_markdown(config)
        else:
            _display_config_table(config)

    except FileNotFoundError:
        rprint(f"[red]Error:[/red] Configuration file '{config_file}' not found")
        raise typer.Exit(1)
    except json.JSONDecodeError as e:
        rprint(f"[red]Error:[/red] Invalid JSON in configuration file: {e}")
        raise typer.Exit(1)
    except Exception as e:
        _handle_config_error(e, config_file)
        raise typer.Exit(1)


def _interactive_config_builder(name: str) -> "RoutingConfig":
    """Interactive configuration builder."""
    description = typer.prompt("Configuration description", default="")
    builder = ConfigBuilder(name, description)

    while True:
        rule_name = typer.prompt("\nRule name")
        rule_priority = typer.prompt("Rule priority", default=0, type=int)
        rule_description = typer.prompt("Rule description", default="")

        rule_builder = builder.add_rule(rule_name, rule_priority, rule_description)

        # Add conditions
        rprint("\n[bold]Add conditions (press Enter with empty field to finish):[/bold]")
        while True:
            field = typer.prompt("Condition field", default="")
            if not field.strip():
                break

            operator = typer.prompt("Operator (equals, in, greater_than, etc.)", default="equals")
            value = typer.prompt("Value (or JSON for arrays)")

            try:
                # Try to parse as JSON first
                parsed_value = json.loads(value)
            except json.JSONDecodeError:
                # Use as string if not valid JSON
                parsed_value = value

            rule_builder = rule_builder.with_condition(field, operator, parsed_value)

        # Set strategy
        strategy = typer.prompt("Strategy", default=RoutingStrategy.SINGLE, type=RoutingStrategy)

        if strategy == RoutingStrategy.SPLIT:
            rule_builder = rule_builder.use_split_strategy()
        elif strategy == RoutingStrategy.SHADOW:
            rule_builder = rule_builder.use_shadow_strategy()
        elif strategy == RoutingStrategy.FALLBACK:
            rule_builder = rule_builder.use_fallback_strategy()

        # Add targets
        rprint("\n[bold]Add targets:[/bold]")
        while True:
            provider = typer.prompt("Target provider", default="")
            if not provider.strip():
                break

            model_name = typer.prompt("Model name")
            endpoint = typer.prompt("Endpoint URL")
            weight = typer.prompt("Weight", default=1.0, type=float)

            rule_builder = rule_builder.add_target(provider, model_name, endpoint, weight)

        # Ask if user wants to add another rule
        add_another = typer.confirm("\nAdd another rule?")
        if add_another:
            rule_builder = rule_builder.and_rule("", 0, "")
        else:
            break

    return rule_builder.build()


def _interactive_request_builder() -> Dict[str, Any]:
    """Interactive request data builder."""
    rprint("[bold]Enter request data (JSON format):[/bold]")
    rprint("Example: {\"user\": {\"tier\": \"premium\"}, \"request\": {\"type\": \"image\"}}")

    while True:
        request_input = typer.prompt("Request data")
        try:
            return json.loads(request_input)
        except json.JSONDecodeError as e:
            rprint(f"[red]Invalid JSON:[/red] {e}")
            rprint("Please enter valid JSON data.")


def _display_routing_result(result, verbose: bool = False):
    """Display routing test results."""
    if result.matched_rule:
        rprint(f"[green]✓ Matched Rule:[/green] {result.matched_rule.name}")
        rprint(f"[blue]Strategy:[/blue] {result.matched_rule.strategy}")
        rprint(f"[blue]Selected Targets:[/blue] {len(result.selected_targets)}")

        if verbose:
            # Show matched rule details
            table = Table(title="Matched Rule Details")
            table.add_column("Property", style="cyan")
            table.add_column("Value")

            table.add_row("Name", result.matched_rule.name)
            table.add_row("Description", result.matched_rule.description or "")
            table.add_row("Priority", str(result.matched_rule.priority))
            table.add_row("Strategy", result.matched_rule.strategy)
            table.add_row("Conditions", str(len(result.matched_rule.conditions)))

            console.print(table)

            # Show selected targets
            if result.selected_targets:
                targets_table = Table(title="Selected Targets")
                targets_table.add_column("Provider")
                targets_table.add_column("Model")
                targets_table.add_column("Endpoint")
                targets_table.add_column("Weight")
                targets_table.add_column("Shadow")

                for target in result.selected_targets:
                    targets_table.add_row(
                        target.provider,
                        target.model_name,
                        target.endpoint,
                        str(target.weight),
                        "Yes" if target.is_shadow else "No"
                    )

                console.print(targets_table)

    else:
        rprint("[red]✗ No rules matched[/red]")

    rprint(f"\n[dim]Explanation:[/dim] {result.explanation}")

    if result.execution_time_ms:
        rprint(f"[dim]Execution time:[/dim] {result.execution_time_ms:.2f}ms")


def _display_coverage_results(results: Dict[str, Any]):
    """Display coverage analysis results."""
    table = Table(title="Rule Coverage Analysis")
    table.add_column("Metric", style="cyan")
    table.add_column("Value")

    table.add_row("Total Requests", str(results["total_requests"]))
    table.add_row("Total Rules", str(results["total_rules"]))
    table.add_row("Covered Rules", str(results["covered_rules"]))
    table.add_row("Coverage Percentage", f"{results['coverage_percentage']:.1f}%")
    table.add_row("Unmatched Requests", str(results["unmatched_requests"]))

    console.print(table)

    # Show rule hits
    if results["rule_hits"]:
        hits_table = Table(title="Rule Hit Counts")
        hits_table.add_column("Rule Name")
        hits_table.add_column("Hits", justify="right")

        for rule_name, hits in results["rule_hits"].items():
            style = "green" if hits > 0 else "red"
            hits_table.add_row(rule_name, str(hits), style=style)

        console.print(hits_table)

    # Show uncovered rules
    if results["uncovered_rules"]:
        rprint(f"\n[yellow]Uncovered Rules ({len(results['uncovered_rules'])}):[/yellow]")
        for rule in results["uncovered_rules"]:
            rprint(f"  • {rule}")


def _display_lint_results(lint_results: Dict[str, List[str]]):
    """Display linting results."""
    errors = lint_results.get("errors", [])
    warnings = lint_results.get("warnings", [])
    suggestions = lint_results.get("suggestions", [])

    if errors:
        rprint(f"\n[red]Errors ({len(errors)}):[/red]")
        for error in errors:
            rprint(f"  ✗ {error}")

    if warnings:
        rprint(f"\n[yellow]Warnings ({len(warnings)}):[/yellow]")
        for warning in warnings:
            rprint(f"  ⚠ {warning}")

    if suggestions:
        rprint(f"\n[blue]Suggestions ({len(suggestions)}):[/blue]")
        for suggestion in suggestions:
            rprint(f"  💡 {suggestion}")


def _display_config_table(config):
    """Display configuration as a table."""
    # Main config info
    info_table = Table(title="Configuration Overview")
    info_table.add_column("Property", style="cyan")
    info_table.add_column("Value")

    info_table.add_row("Name", config.name)
    info_table.add_row("Description", config.description or "")
    info_table.add_row("Total Rules", str(len(config.rules)))
    info_table.add_row("Enabled Rules", str(sum(1 for r in config.rules if r.is_enabled)))

    console.print(info_table)

    # Rules table
    rules_table = Table(title="Routing Rules")
    rules_table.add_column("Name")
    rules_table.add_column("Priority", justify="right")
    rules_table.add_column("Strategy")
    rules_table.add_column("Conditions", justify="right")
    rules_table.add_column("Targets", justify="right")
    rules_table.add_column("Status")

    for rule in sorted(config.rules, key=lambda r: r.priority, reverse=True):
        status = "[green]Enabled[/green]" if rule.is_enabled else "[red]Disabled[/red]"
        rules_table.add_row(
            rule.name,
            str(rule.priority),
            rule.strategy,
            str(len(rule.conditions)),
            str(len(rule.targets)),
            status
        )

    console.print(rules_table)


def _normalize_config_format(config_data: dict) -> dict:
    """Normalize different configuration file formats to the expected structure."""
    # Handle frontend export format: {metadata: {...}, config: {name, rules, ...}}
    if isinstance(config_data, dict) and 'config' in config_data and 'metadata' in config_data:
        rprint("[dim]Detected frontend export format, extracting config...[/dim]")
        return config_data['config']

    # Handle direct config format: {name, rules, ...}
    elif isinstance(config_data, dict) and ('name' in config_data or 'rules' in config_data):
        return config_data

    # Handle array of rules: [{name, targets, ...}, ...]
    elif isinstance(config_data, list):
        rprint("[dim]Detected rules array format, wrapping with config structure...[/dim]")
        return {
            "name": "Imported Configuration",
            "description": "Configuration imported from rules array",
            "rules": config_data
        }

    # Handle wrapped config: {config_data: {rules: ...}} (from backend)
    elif isinstance(config_data, dict) and 'config_data' in config_data:
        inner_config = config_data['config_data']
        if isinstance(inner_config, dict) and 'rules' in inner_config:
            return {
                "name": config_data.get('name', 'Backend Configuration'),
                "description": config_data.get('description', ''),
                "rules": inner_config['rules']
            }

    # Return as-is if we can't detect the format
    return config_data


def _handle_config_error(error: Exception, config_file: str = None):
    """Handle and display user-friendly configuration errors."""
    from pydantic import ValidationError

    # Handle Pydantic validation errors specifically
    if isinstance(error, ValidationError):
        rprint("[red]Configuration Validation Error:[/red]")
        rprint("Your configuration file has the following issues:\n")

        for error_detail in error.errors():
            field_name = ".".join(str(loc) for loc in error_detail.get('loc', []))
            error_type = error_detail.get('type', '')
            error_msg = error_detail.get('msg', '')

            if error_type == 'missing':
                if field_name == 'name':
                    rprint("  • [red]Missing required field:[/red] [yellow]'name'[/yellow]")
                    rprint("    Your configuration needs a name at the top level.")
                    rprint("    [dim]Add: \"name\": \"My Configuration\"[/dim]")
                elif field_name == 'rules':
                    rprint("  • [red]Missing required field:[/red] [yellow]'rules'[/yellow]")
                    rprint("    Your configuration needs an array of routing rules.")
                    rprint("    [dim]Add: \"rules\": [...][/dim]")
                else:
                    rprint(f"  • [red]Missing required field:[/red] [yellow]'{field_name}'[/yellow]")
            elif error_type == 'value_error':
                if "at least one target must be specified" in error_msg:
                    rprint(f"  • [red]Rule validation error:[/red] Rule at {field_name} has no targets")
                    rprint("    Each routing rule must have at least one target model.")
                elif "at least one routing rule must be specified" in error_msg:
                    rprint("  • [red]Configuration error:[/red] Rules array is empty")
                    rprint("    Your configuration needs at least one routing rule.")
                else:
                    rprint(f"  • [red]Validation error in {field_name}:[/red] {error_msg}")
            else:
                rprint(f"  • [red]Error in {field_name}:[/red] {error_msg}")

        rprint("\n[blue]Supported file formats:[/blue]")

        rprint("\n[dim]1. Direct configuration:[/dim]")
        rprint("[cyan]{[/cyan]")
        rprint("[cyan]  \"name\": \"Configuration Name\",[/cyan]")
        rprint("[cyan]  \"description\": \"Optional description\",[/cyan]")
        rprint("[cyan]  \"rules\": [[/cyan]")
        rprint("[cyan]    {\"name\": \"rule_name\", \"conditions\": [...], \"targets\": [...]}[/cyan]")
        rprint("[cyan]  ][/cyan]")
        rprint("[cyan]}[/cyan]")

        rprint("\n[dim]2. Frontend export (Claude Code):[/dim]")
        rprint("[cyan]{[/cyan]")
        rprint("[cyan]  \"metadata\": {\"exportedBy\": \"Claude Code\", ...},[/cyan]")
        rprint("[cyan]  \"config\": {\"name\": \"...\", \"rules\": [...]}[/cyan]")
        rprint("[cyan]}[/cyan]")

        rprint("\n[dim]3. Rules array:[/dim]")
        rprint("[cyan][[/cyan]")
        rprint("[cyan]  {\"name\": \"rule_name\", \"conditions\": [...], \"targets\": [...]}[/cyan]")
        rprint("[cyan]][/cyan]")

        if config_file:
            rprint(f"\n[blue]💡 Helpful commands:[/blue]")
            rprint(f"  • [yellow]mixtrain routing create \"My Config\"[/yellow] - Create a new configuration")
            rprint(f"  • [yellow]mixtrain routing validate {config_file}[/yellow] - Get detailed validation info")

    else:
        # Handle other types of errors
        error_str = str(error).lower()

        # Try to detect common issues from string patterns
        if "validation error" in error_str or "field required" in error_str:
            rprint("[red]Configuration Validation Error:[/red]")

            if "name" in error_str and ("field required" in error_str or "missing" in error_str):
                rprint("  • [red]Missing required field:[/red] [yellow]'name'[/yellow]")
                rprint("    The configuration must have a name at the top level.")

            if "rules" in error_str and ("field required" in error_str or "missing" in error_str):
                rprint("  • [red]Missing required field:[/red] [yellow]'rules'[/yellow]")
                rprint("    The configuration must have an array of routing rules.")

            rprint(f"\n[dim]Original error: {str(error)}[/dim]")
        else:
            rprint(f"[red]Error:[/red] {str(error)}")


def _display_config_markdown(config):
    """Display configuration in Markdown format."""
    markdown = f"""# Routing Configuration: {config.name}

{config.description}

## Overview
- **Total Rules**: {len(config.rules)}
- **Enabled Rules**: {sum(1 for r in config.rules if r.is_enabled)}

## Rules

"""

    for rule in sorted(config.rules, key=lambda r: r.priority, reverse=True):
        status = "✅ Enabled" if rule.is_enabled else "❌ Disabled"
        markdown += f"""### {rule.name} (Priority: {rule.priority})

**Status**: {status}
**Strategy**: {rule.strategy}
**Description**: {rule.description or "None"}

**Conditions** ({len(rule.conditions)}):
"""
        for i, condition in enumerate(rule.conditions, 1):
            markdown += f"{i}. `{condition.field}` {condition.operator} `{condition.value}`\n"

        markdown += f"""
**Targets** ({len(rule.targets)}):
"""
        for i, target in enumerate(rule.targets, 1):
            markdown += f"{i}. **{target.provider}**/{target.model_name} - {target.endpoint} (weight: {target.weight})\n"

        markdown += "\n"

    syntax = Syntax(markdown, "markdown", theme="monokai")
    console.print(syntax)