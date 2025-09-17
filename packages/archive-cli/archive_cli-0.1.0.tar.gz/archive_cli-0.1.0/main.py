import os
import tarfile
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Literal

import typer
from prompt_toolkit import prompt
from prompt_toolkit.completion import PathCompleter
from prompt_toolkit.shortcuts import confirm

app = typer.Typer(help="Archive CLI - A tool for creating and extracting archives")

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

@app.command()
def archive():
    """Create an archive from a directory."""
    # Get directory to archive
    source_dir = get_directory_path("Enter path to directory to archive: ")

    # Get archive format
    format_choice = get_archive_format()

    # Generate archive name
    dir_name = source_dir.name
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    if format_choice == "tar":
        archive_name = f"{dir_name}_{timestamp}.tar.gz"
        archive_path = Path.cwd() / archive_name

        typer.echo(f"Creating tarball: {archive_path}")
        with tarfile.open(archive_path, "w:gz") as tar:
            tar.add(source_dir, arcname=dir_name)

    elif format_choice == "zip":
        archive_name = f"{dir_name}_{timestamp}.zip"
        archive_path = Path.cwd() / archive_name

        typer.echo(f"Creating zip archive: {archive_path}")
        with zipfile.ZipFile(archive_path, "w", zipfile.ZIP_DEFLATED) as zip_file:
            for file_path in source_dir.rglob("*"):
                if file_path.is_file():
                    arcname = file_path.relative_to(source_dir.parent)
                    zip_file.write(file_path, arcname)

    typer.echo(f"✅ Archive created successfully: {archive_path}")

@app.command()
def unarchive():
    """Extract an archive to a directory."""
    # Get archive file
    archive_file = get_file_path("Enter path to archive file: ")

    # Determine archive type
    if archive_file.suffix.lower() in ['.tar', '.gz', '.tgz'] or '.tar.' in archive_file.name.lower():
        archive_type = "tar"
    elif archive_file.suffix.lower() == '.zip':
        archive_type = "zip"
    else:
        typer.echo(f"Unsupported archive format: {archive_file.suffix}")
        raise typer.Exit(1)

    # Generate extraction directory name
    archive_name = archive_file.stem
    if archive_name.endswith('.tar'):
        archive_name = archive_name[:-4]  # Remove .tar from .tar.gz

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    extract_dir = Path.cwd() / f"{archive_name}_{timestamp}"

    # Create extraction directory
    extract_dir.mkdir(exist_ok=True)

    typer.echo(f"Extracting {archive_type} archive to: {extract_dir}")

    try:
        if archive_type == "tar":
            with tarfile.open(archive_file, "r:*") as tar:
                tar.extractall(extract_dir)

        elif archive_type == "zip":
            with zipfile.ZipFile(archive_file, "r") as zip_file:
                zip_file.extractall(extract_dir)

        typer.echo(f"✅ Archive extracted successfully to: {extract_dir}")

    except Exception as e:
        typer.echo(f"❌ Error extracting archive: {e}")
        raise typer.Exit(1)

if __name__ == "__main__":
    app()
