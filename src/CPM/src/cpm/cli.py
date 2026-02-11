import typer

from .cpm import cpm


app = typer.Typer()
app.command()(cpm)


if __name__ == "__main__":
    app()