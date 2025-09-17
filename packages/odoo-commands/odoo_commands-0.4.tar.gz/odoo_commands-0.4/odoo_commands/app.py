import typer
from odoo_commands.createdb import create_database_command
from odoo_commands.nighly import download_odoo

app = typer.Typer()

app.command(name='createdb')(create_database_command)
app.command(name='nightly')(download_odoo)

@app.command()
def hello(name: str):
    print(f"Hello {name}")


if __name__ == "__main__":
    app()
