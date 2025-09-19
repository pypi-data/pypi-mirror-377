from pathlib import Path

import click

from odoo_openupgrade_wizard.cli.cli_options import (
    database_option_required,
    get_migration_step_from_options,
    step_option,
)
from odoo_openupgrade_wizard.tools.tools_postgres import (
    execute_sql_files_pre_migration,
)


@click.command()
@step_option
@database_option_required
@click.option(
    "--script-file-path",
    multiple=True,
    type=click.Path(
        exists=True,
        dir_okay=False,
    ),
    help="List of SQL files to execute. Files will be executed in the order "
    "listed. If no files are specified, all SQL files (.sql) in the "
    "step's directory will be sorted alphabetically and then executed "
    "in order.",
)
@click.pass_context
def execute_script_sql(ctx, step, database, script_file_path):
    """Execute SQL scripts for a migration step.

    Executes one or more custom SQL scripts against the specified database,
    using the PostgreSQL Docker container. This command allows you to manually
    run SQL logic, allowing you to test or apply SQL changes in the context
    of a specific migration step — outside the automatic oow upgrade process.
    """

    migration_step = get_migration_step_from_options(ctx, step)

    execute_sql_files_pre_migration(
        ctx, database, migration_step, [Path(x) for x in script_file_path]
    )
