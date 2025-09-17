import typer

from .cmd.archive import archive_command
from .cmd.unarchive import unarchive_command

app = typer.Typer(help="Archive CLI - A tool for creating and extracting archives")


@app.command("archive")
def archive():
    """Create an archive from a directory."""
    archive_command()


@app.command("unarchive")
def unarchive():
    """Extract an archive to a directory."""
    unarchive_command()


def main():
    """Main entry point for the CLI application."""
    app()


if __name__ == "__main__":
    main()