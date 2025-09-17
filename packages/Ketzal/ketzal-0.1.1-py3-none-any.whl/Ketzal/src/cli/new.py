import click
import os
from ..util.structure import structure

@click.command("new")
@click.argument("name")
def new(name):
    """
    Create a new Ketzal project with the given NAME.
    """
    # Determine base directory and project name
    if name == ".":
        base = os.getcwd()
        project_name = os.path.basename(base)
        click.echo(f"📂 Initializing Ketzal project in current directory: {base}")
    else:
        base = os.path.abspath(name)
        project_name = name
        if os.path.exists(base):
            click.echo(f"📂 Directory '{base}' already exists. Initializing Ketzal project inside it...")
        else:
            os.makedirs(base, exist_ok=True)
            click.echo(f"📂 Created base directory: {base}")

    # Create project structure directories
    for path in structure:
        dir_path = os.path.join(base, path)
        os.makedirs(dir_path, exist_ok=True)
        click.echo(f"📂 Created directory: {dir_path}")

    # Create initial files
    files = {
        "routes/web.py": (
            "from Ketzal import Router\n\n"
            "Router.get(\"/\", lambda : \"Hello World!\")\n"
        ),
        ".env": (
            "DEBUG=True\n"
            "HOST=127.0.0.1\n"
            "PORT=5002\n"
        ),
    }

    for rel_path, content in files.items():
        file_path = os.path.join(base, rel_path)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        click.echo(f"📝 Created file: {file_path}")

    click.echo(f"\n✅ Project {project_name} created successfully at {base}")
