from pathlib import Path

import click

from odoo_openupgrade_wizard.cli.cli_options import (
    database_option_required,
    get_migration_step_from_options,
    step_option,
)
from odoo_openupgrade_wizard.tools.tools_odoo import (
    execute_click_odoo_python_files,
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
    help="""List of Python files to execute, with either an absolute path
    or path relative to the project directory. With either method, the
    path must be located inside the project directory so that the
    Docker container can access it.

    Files will be executed in
    the order listed. If no files are specified, all Python (.py) files
    in the `step` directory will be sorted alphabetically and then
    executed in order.

    See README.md for more information and examples.""",
)
@click.pass_context
def execute_script_python(ctx, step, database, script_file_path):
    """Execute Python scripts for a migration step.

    Executes one or more custom Python scripts in the context of a specific
    migration step, using the Odoo shell (with full ORM access). This command
    allows you to manually run Python logic outside of the default
    post-migration.py file for a given step. It allows fine-tuning
    of migration behavior by manually specifying logic.
    """

    migration_step = get_migration_step_from_options(ctx, step)

    execute_click_odoo_python_files(
        ctx, database, migration_step, [Path(x) for x in script_file_path]
    )
