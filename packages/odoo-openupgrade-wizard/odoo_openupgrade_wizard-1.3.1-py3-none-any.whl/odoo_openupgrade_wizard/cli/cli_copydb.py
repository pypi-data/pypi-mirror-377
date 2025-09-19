import click

from odoo_openupgrade_wizard.tools import (
    tools_click_odoo_contrib as click_odoo_contrib,
)


@click.command()
@click.option(
    "-s",
    "--source",
    type=str,
    help="Name of the source database to copy.",
)
@click.option(
    "-d",
    "--dest",
    type=str,
    help="Name of the destination database to create.",
)
@click.pass_context
def copydb(ctx, source, dest):
    """Create a new Odoo database by copying another.

    This command duplicates both the PostgreSQL database and its associated
    filestore.

    """
    click_odoo_contrib.copydb(ctx, source, dest)
