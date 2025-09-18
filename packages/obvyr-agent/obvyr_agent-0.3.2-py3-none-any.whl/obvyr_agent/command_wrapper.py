import logging
import os
import subprocess
import time
from typing import Callable, List, Optional

from obvyr_agent.schemas import RunCommandResponse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_obvyr_agent_user() -> str:
    """
    Retrieves the user running the agent based on the OBVYR_AGENT_USER environment variable.
    This allows for maximum configurability and control by the customer.
    """
    user = os.getenv("OBVYR_AGENT_USER")
    if user:
        logger.info(f"Using user specified by OBVYR_AGENT_USER: {user}")
        return user

    # Default if the user hasn't specified anything
    logger.warning("OBVYR_AGENT_USER not set. Using default: 'unknown_user'")
    return "unknown_user"


def run_command(
    command: List[str],
    stream_callback: Optional[Callable[[str], None]] = None,
) -> RunCommandResponse:
    """
    Executes a system command and returns the output with color preservation and streaming.
    :param command: List of command arguments.
    :param stream_callback: Optional callback for real-time output streaming.
    :return: RunCommandResponse object.
    """
    user = get_obvyr_agent_user()
    start_time = time.time()

    try:
        # Set up environment to encourage colored output
        env = os.environ.copy()
        env["FORCE_COLOR"] = "1"

        # Use bytes mode to preserve ANSI color codes
        process = subprocess.Popen(  # noqa: S603
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            env=env,
        )
        logger.info(f"Executed command: {' '.join(command)}")

        # Stream output while collecting it
        output_lines = []
        if process.stdout:  # Type guard to satisfy mypy
            while True:
                line = process.stdout.readline()
                if not line and process.poll() is not None:
                    break

                if line:
                    # Decode bytes to string, preserving ANSI codes
                    decoded_line = line.decode("utf-8", errors="replace")
                    output_lines.append(decoded_line)

                    # Call streaming callback if provided
                    if stream_callback:
                        stream_callback(decoded_line.rstrip("\n\r"))

        returncode = process.returncode
        output = "".join(output_lines).rstrip()

    except Exception as e:
        exception_type = e.__class__.__name__
        exception_string = f"{exception_type}: {e}"
        logger.error(
            f"Failed to execute command: {command}. {exception_string}"
        )
        output = exception_string
        returncode = -1

    end_time = time.time()
    execution_time = end_time - start_time

    return RunCommandResponse(
        command=command,
        output=output,
        returncode=returncode,
        user=user,
        execution_time=execution_time,
    )
