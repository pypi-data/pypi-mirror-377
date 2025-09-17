"""
Archive builder for creating artifacts.tar.zst files.

This module creates compressed tar archives containing command execution data
and optional attachments in the format required by the /collect API endpoint.
"""

import io
import json
import os
import pathlib
import tarfile
import tempfile
from datetime import UTC, datetime
from typing import Dict, Optional

import zstandard as zstd
from pydantic import BaseModel

from obvyr_agent.schemas import RunCommandResponse


class ArchiveSummary(BaseModel):
    """Summary of archive contents and sizes."""

    archive_bytes: int
    members: Dict[str, Dict[str, int]]


def build_artifacts_tar_zst(
    run_command_response: RunCommandResponse,
    attachment_paths: Optional[list[pathlib.Path]] = None,
    tmp_dir: Optional[pathlib.Path] = None,
    tags: Optional[list[str]] = None,
) -> pathlib.Path:
    """
    Build artifacts.tar.zst archive from command execution data.

    Creates a compressed tar archive containing:
    - /command.json (required)
    - /output.txt (optional; UTF-8 mixed stdout/stderr)
    - /attachment/<filename> (optional)

    Args:
        run_command_response: Command execution response containing metadata and output
        attachment_paths: Optional list of attachment files to include
        tmp_dir: Optional temporary directory for output file
        tags: Optional list of tags to include in command.json

    Returns:
        Path to the created artifacts.tar.zst file
    """
    if tmp_dir is None:
        tmp_dir = pathlib.Path(tempfile.gettempdir())

    # Create output file path
    output_path = tmp_dir / "artifacts.tar.zst"

    # Prepare command.json data exactly as specified in the doc
    command_data = {
        "command": run_command_response.command,
        "user": run_command_response.user,
        "return_code": run_command_response.returncode,
        "execution_time_ms": round(run_command_response.execution_time * 1000),
        "executed": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "env": dict(os.environ),
        "tags": tags or [],
    }

    # Create tar archive in memory first
    tar_buffer = io.BytesIO()

    with tarfile.open(fileobj=tar_buffer, mode="w") as tar:
        # Add command.json (required)
        command_json_bytes = json.dumps(
            command_data, separators=(",", ":")
        ).encode("utf-8")
        command_info = tarfile.TarInfo("command.json")
        command_info.size = len(command_json_bytes)
        tar.addfile(command_info, io.BytesIO(command_json_bytes))

        # Add output.txt if present (optional; mixed stdout/stderr)
        if run_command_response.output:
            output_bytes = run_command_response.output.encode("utf-8")
            output_info = tarfile.TarInfo("output.txt")
            output_info.size = len(output_bytes)
            tar.addfile(output_info, io.BytesIO(output_bytes))

        # Add attachments if provided (optional)
        if attachment_paths:
            for attachment_path in attachment_paths:
                if not attachment_path.exists():
                    continue

                # Use attachment/<filename> structure as specified
                arcname = f"attachment/{attachment_path.name}"

                # Stream file without loading into memory
                with open(attachment_path, "rb") as f:
                    attachment_info = tarfile.TarInfo(arcname)
                    attachment_info.size = attachment_path.stat().st_size
                    tar.addfile(attachment_info, f)

    # Compress tar with zstd
    tar_buffer.seek(0)
    tar_data = tar_buffer.read()

    compressor = zstd.ZstdCompressor(write_content_size=True)
    compressed_data = compressor.compress(tar_data)

    with open(output_path, "wb") as output_file:
        output_file.write(compressed_data)

    return output_path


def summarize_archive(archive_path: pathlib.Path) -> ArchiveSummary:
    """
    Summarise contents of an artifacts.tar.zst archive.

    Args:
        archive_path: Path to the artifacts.tar.zst file

    Returns:
        ArchiveSummary containing archive size and member information

    Raises:
        FileNotFoundError: If archive file doesn't exist
    """
    if not archive_path.exists():
        raise FileNotFoundError(f"Archive not found: {archive_path}")

    # Get archive size
    archive_bytes = archive_path.stat().st_size

    # Extract and examine tar contents
    decompressor = zstd.ZstdDecompressor()
    members: Dict[str, Dict[str, int]] = {}

    with open(archive_path, "rb") as archive_file:
        with decompressor.stream_reader(archive_file) as reader:
            with tarfile.open(fileobj=reader, mode="r|") as tar:
                for member in tar:
                    if member.isfile():
                        members[member.name] = {"bytes": member.size}

    return ArchiveSummary(archive_bytes=archive_bytes, members=members)
