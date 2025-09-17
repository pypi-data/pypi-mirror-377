import tarfile
import zipfile
from datetime import datetime
from pathlib import Path

import typer

from ..lib.prompt import get_archive_format, get_directory_path


def archive_command():
    """Create an archive from a directory."""
    source_dir = get_directory_path("Enter path to directory to archive: ")
    format_choice = get_archive_format()

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