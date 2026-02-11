import typer

from .cpm import greet


app = typer.Typer()
app.command()(cpm)


if __name__ == "__main__":
    app()