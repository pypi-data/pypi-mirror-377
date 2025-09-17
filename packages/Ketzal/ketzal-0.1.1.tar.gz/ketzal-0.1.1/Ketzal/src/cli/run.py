import click
from ..server.server import Server 

@click.command("run")
def run():
    """
    Run the Ketzal server.
    """
    server = Server(auto_reload=True)
    server.start()
