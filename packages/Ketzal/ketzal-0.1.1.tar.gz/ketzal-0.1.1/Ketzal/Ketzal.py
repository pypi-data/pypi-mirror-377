import click

from .src.cli.new import new
from .src.cli.run import run

@click.group()
def cli():
    """Ketzal CLI """

# add commands
cli.add_command(new) # new project 
cli.add_command(run) # run server

