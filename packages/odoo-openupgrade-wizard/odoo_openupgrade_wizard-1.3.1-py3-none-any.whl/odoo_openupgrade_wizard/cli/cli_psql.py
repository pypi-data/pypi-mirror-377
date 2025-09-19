import click

from odoo_openupgrade_wizard.cli.cli_options import database_option_required
from odoo_openupgrade_wizard.tools.tools_postgres import execute_psql_command


@click.command(context_settings={"ignore_unknown_options": True})
@database_option_required
@click.option(
    "-c",
    "--command",
    "request",
    help="SQL command to execute inside the container.",
)
@click.option(
    "--pager/--no-pager",
    default=True,
    help="Enable or disable pager when displaying output.",
)
@click.argument("psql_args", nargs=-1, type=click.UNPROCESSED)
@click.pass_context
def psql(ctx, request, database, pager, psql_args):
    """Run a SQL command in the PostgreSQL container.

    This command executes the provided SQL command using `psql`
    within the database container. Use --command for inline SQL
    or pass additional arguments directly to psql via PSQLARGS.

    See the README.md for more information.
    """

    result = execute_psql_command(ctx, request, database, psql_args)
    if pager:
        click.echo_via_pager(result)
    else:
        click.echo(result)
