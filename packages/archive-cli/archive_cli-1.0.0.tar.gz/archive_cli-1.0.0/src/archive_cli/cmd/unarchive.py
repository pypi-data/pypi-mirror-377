import tarfile
import zipfile
from datetime import datetime
from pathlib import Path

import typer

from ..lib.prompt import get_file_path


def unarchive_command():
    """Extract an archive to a directory."""
    archive_file = get_file_path("Enter path to archive file: ")

    if archive_file.suffix.lower() in ['.tar', '.gz', '.tgz'] or '.tar.' in archive_file.name.lower():
        archive_type = "tar"
    elif archive_file.suffix.lower() == '.zip':
        archive_type = "zip"
    else:
        typer.echo(f"Unsupported archive format: {archive_file.suffix}")
        raise typer.Exit(1)

    archive_name = archive_file.stem
    if archive_name.endswith('.tar'):
        archive_name = archive_name[:-4]

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    extract_dir = Path.cwd() / f"{archive_name}_{timestamp}"

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