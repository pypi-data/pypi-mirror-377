import click
import os
from ..util.structure import structure

@click.command("new")
@click.argument("name")
def new(name):
    """
    Create a new Ketzal project with the given NAME.
    """
    base = os.path.abspath(name)

  
    for path in structure:
        dir_path = os.path.join(base, path)
        os.makedirs(dir_path, exist_ok=True)
        click.echo(f"📂 Created directory: {dir_path}")
    files = {
        "routes/web.py": """from Ketzal import Router

Router.get("/", lambda : "Hello World!")
""",
        ".env": """DEBUG=True
HOST=127.0.0.1
PORT=5002
"""
    }

    for rel_path, content in files.items():
        file_path = os.path.join(base, rel_path)
        os.makedirs(os.path.dirname(file_path), exist_ok=True) 
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content.strip() + "\n")
        click.echo(f"📝 Created file: {file_path}")

    click.echo(f"\n✅ Project {name} created successfully at {base}")
