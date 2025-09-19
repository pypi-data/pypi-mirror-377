import click
from solve_ps.subs.run import run
from solve_ps.subs.get import get
from solve_ps.subs.diff import diff
from solve_ps.subs.tc import tc


@click.group()
@click.version_option()
def cli():
    ...


cli.add_command(run)
cli.add_command(get)
cli.add_command(diff)
cli.add_command(tc)
cli()
