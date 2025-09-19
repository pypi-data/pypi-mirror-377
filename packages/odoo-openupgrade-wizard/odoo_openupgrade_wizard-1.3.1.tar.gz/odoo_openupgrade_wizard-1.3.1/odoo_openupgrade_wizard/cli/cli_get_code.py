import click

from odoo_openupgrade_wizard.cli.cli_options import (
    get_odoo_versions_from_options,
    versions_options,
)
from odoo_openupgrade_wizard.tools.tools_odoo import (
    get_odoo_env_path,
    get_repo_file_path,
)
from odoo_openupgrade_wizard.tools.tools_system import git_aggregate


@click.command()
@versions_options
@click.option(
    "-j",
    "--jobs",
    type=int,
    default=10,
    help="Jobs used to call the git-aggregate command."
    " Reasonably set to 10 by default.",
)
@click.pass_context
def get_code(ctx, versions, jobs):
    """Get all required source code for each version.

    Downloads all required Odoo source code and dependencies for each version
    defined in your migration (uses the `gitaggregate` tools internally).
    """

    for odoo_version in get_odoo_versions_from_options(ctx, versions):
        folder_path = get_odoo_env_path(ctx, odoo_version)
        repo_file_path = get_repo_file_path(ctx, odoo_version)
        git_aggregate(folder_path, repo_file_path, jobs)
