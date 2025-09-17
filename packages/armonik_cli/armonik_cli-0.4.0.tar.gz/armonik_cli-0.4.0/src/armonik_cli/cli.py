from armonik_cli import commands, __version__

import armonik_cli_core as akcc
from armonik_cli_core.utils import populate_option_groups_incremental

akcc.rich_click.USE_RICH_MARKUP = True
akcc.rich_click.USE_MARKDOWN = True
akcc.rich_click.STYLE_ERRORS_SUGGESTION = "magenta italic"
akcc.rich_click.ERRORS_SUGGESTION = "Try running the '--help' flag for more information."
akcc.rich_click.ERRORS_EPILOGUE = (
    "To find out more, visit [link=https://github.com/aneoconsulting/ArmoniK.CLI]our repo[/link]."
)


@akcc.group(
    cls=akcc.groups.ExtendableGroup,
    entry_point_group=akcc.groups.ENTRY_POINT_GROUP,
    name="armonik",
    context_settings={"help_option_names": ["-h", "--help"], "auto_envvar_prefix": "AK"},
)
@akcc.version_option(version=__version__, prog_name="armonik")
def cli(**kwargs) -> None:
    """
    ArmoniK CLI is a tool to monitor and manage ArmoniK clusters.
    """
    pass


cli.add_command(commands.extensions)
cli.add_command(commands.sessions)
cli.add_command(commands.tasks)
cli.add_command(commands.partitions)
cli.add_command(commands.results)
cli.add_command(commands.cluster)
cli.add_command(commands.config)

akcc.groups.setup_command_groups()
populate_option_groups_incremental(
    cli
)  # Note: This won't be used by plugins, just by the main CLI, should probably be brought into the main CLI later.
