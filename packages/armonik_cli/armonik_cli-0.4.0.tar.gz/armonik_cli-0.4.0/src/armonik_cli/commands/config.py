from pydantic_core import PydanticUndefined
import armonik_cli_core as akcc

from rich.table import Table
from rich.syntax import Syntax
from rich.console import Group
from rich.panel import Panel

from armonik_cli_core.configuration import CliConfig
from armonik_cli.utils import pretty_type

akcc.rich_click.USE_RICH_MARKUP = True
akcc.rich_click.USE_MARKDOWN = True


@akcc.group(name="config")
def config(**kwargs) -> None:
    """Manage CLI configuration."""
    pass


@config.command(name="get", pass_config=True)
@akcc.argument(
    "field",
    type=str,
    required=True,
)
def config_get(config: CliConfig, field: str, **kwargs) -> None:
    """Get the current CLI configuration."""
    if field in CliConfig.ConfigModel.model_fields.keys():
        akcc.console.print(CliConfig().get(field))
    else:
        raise akcc.ClickException(
            f"Field {field} is not part of the configuration. Call `armonik config list` to see all available fields."
        )


@config.command(name="set", pass_config=True)
@akcc.argument(
    "field",
    type=str,
    required=True,
)
@akcc.argument("value", type=str, required=True)
def config_set(config: CliConfig, field: str, value: str, **kwargs) -> None:
    """Set a field in the CLI configuration."""
    if field in CliConfig.ConfigModel.model_fields.keys():
        CliConfig().set(**{field: value})
        akcc.console.print(f"Set {field} to {value}")
    else:
        raise akcc.ClickException(
            f"Field {field} is not part of the configuration. Call `armonik config list` to see all available fields."
        )


@config.command(name="show", pass_config=True)
def config_show(config: CliConfig, output, **kwargs) -> None:
    """Show the current CLI configuration."""
    config = CliConfig()
    config_dump = config._config.model_dump()
    if config.output == "table":
        # Decided to do it like this so I can have different tables per field group
        table = Table(title="CLI Configuration")
        table.add_column("Field", justify="left")
        table.add_column("Value", justify="left")
        for field, value in config_dump.items():
            table.add_row(field, str(value))
        akcc.console.print(table)
    else:
        akcc.console.formatted_print(config_dump, print_format=output)


@config.command(name="list", pass_config=True)
def config_list(config, **kwargs) -> None:
    """List all available configuration fields."""
    if config.output == "table":
        # Decided to do it like this so I can have different tables per field group (refactor will include grouping for yamls too)
        available_config_fields_table = Table(title="Available configuration fields")
        available_config_fields_table.add_column("Field", justify="left")
        available_config_fields_table.add_column("Type", justify="left")
        available_config_fields_table.add_column("Default", justify="left")
        available_config_fields_table.add_column("Description", justify="left")
        for field_name, details in CliConfig.ConfigModel.model_fields.items():
            available_config_fields_table.add_row(
                field_name,
                pretty_type(CliConfig.ConfigModel.__annotations__[field_name]),
                str(details.default) if details.default != PydanticUndefined else "-",
                details.description,
            )
        akcc.console.print(available_config_fields_table)
    else:
        available_config_fields = []
        for field_name, details in CliConfig.ConfigModel.model_fields.items():
            available_config_fields.append(
                {
                    "Field": field_name,
                    "Type": pretty_type(CliConfig.ConfigModel.__annotations__[field_name]),
                    "Default": str(details.default) if details.default != PydanticUndefined else "",
                    "Description": details.description,
                }
            )
        akcc.console.formatted_print(available_config_fields, print_format=config.output)


@config.command(name="completions")
@akcc.argument(
    "shell",
    type=akcc.Choice(["zsh", "bash", "fish"], case_sensitive=True),
    required=True,
)
def config_completions(shell, **kwargs) -> None:
    """Generate auto-completions for the ArmoniK cli"""
    if shell == "zsh":
        akcc.console.print(
            Panel(
                Group(
                    "Add this to your [blue]~/.zshrc[/]\n",
                    Syntax(
                        'eval "$(_ARMONIK_COMPLETE=zsh_source armonik)"', "bash", theme="monokai"
                    ),
                ),
                border_style="blue",
            )
        )
    elif shell == "bash":
        akcc.console.print(
            Panel(
                Group(
                    "Add this to your [blue]~/.bashrc[/]\n",
                    Syntax(
                        'eval "$(_ARMONIK_COMPLETE=bash_source armonik)"', "bash", theme="monokai"
                    ),
                ),
                border_style="blue",
            )
        )
    elif shell == "fish":
        akcc.console.print(
            Panel(
                Group(
                    "Add this to your [blue]~/.config/fish/completions/foo-bar.fish[/]\n",
                    Syntax(
                        "_ARMONIK_COMPLETE=fish_source armonik | source", "bash", theme="monokai"
                    ),
                ),
                border_style="blue",
            )
        )
