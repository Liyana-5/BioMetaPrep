import typer

app = typer.Typer(help="BioMetaPrep: normalize and validate public genomics metadata.")

@app.callback()
def main():
    """
    BioMetaPrep CLI entry point.
    """
    pass


@app.command()
def hello(name: str = "world") -> None:
    """Sanity check command."""
    typer.echo(f"BioMetaPrep says hello, {name}!")


if __name__ == "__main__":
    app()
