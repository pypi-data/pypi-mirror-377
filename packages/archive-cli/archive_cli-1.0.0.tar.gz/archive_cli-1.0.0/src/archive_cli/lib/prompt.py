from pathlib import Path
from typing import Literal

import typer
from prompt_toolkit import prompt
from prompt_toolkit.completion import PathCompleter


def get_directory_path(message: str) -> Path:
    """Get a directory path from user with path completion."""
    completer = PathCompleter(only_directories=True)
    while True:
        path_str = prompt(message, completer=completer).strip()
        if not path_str:
            typer.echo("Please enter a valid path.")
            continue

        path = Path(path_str).expanduser().resolve()
        if not path.exists():
            typer.echo(f"Path does not exist: {path}")
            continue
        if not path.is_dir():
            typer.echo(f"Path is not a directory: {path}")
            continue
        return path


def get_file_path(message: str) -> Path:
    """Get a file path from user with path completion."""
    completer = PathCompleter()
    while True:
        path_str = prompt(message, completer=completer).strip()
        if not path_str:
            typer.echo("Please enter a valid path.")
            continue

        path = Path(path_str).expanduser().resolve()
        if not path.exists():
            typer.echo(f"File does not exist: {path}")
            continue
        if not path.is_file():
            typer.echo(f"Path is not a file: {path}")
            continue
        return path


def get_archive_format() -> Literal["tar", "zip"]:
    """Get archive format from user."""
    while True:
        format_choice = prompt("Choose archive format (tar/zip): ").strip().lower()
        if format_choice in ["tar", "zip"]:
            return format_choice
        typer.echo("Please choose 'tar' or 'zip'.")