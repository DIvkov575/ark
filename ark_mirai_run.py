#!/usr/bin/env python

import os
import platform
import socket
import subprocess
import sys

import api.config
from api.config import PROJECT_DIR


def find_free_port(start_port: int = 5000, end_port: int = 5020):
    """
    Scans for a free TCP port in a given range.

    Args:
        start_port: The first port to check.
        end_port: The last port to check.

    Returns:
        The first available port number, or None if no port is free.
    """
    print(f"Scanning for an available port from {start_port} to {end_port}...")
    for port in range(start_port, end_port + 1):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(("127.0.0.1", port))
                return port
        except OSError:
            print(f"Port {port} is in use, trying next...")
            continue
    return None


def cli_entrypoint(model_name="auto"):

    if len(sys.argv) > 1:
        model_name = sys.argv[1]

    api.config.set_config_by_name(model_name)

    port = find_free_port()
    if port is None:
        print(
            "Error: Could not find an available port in the range 5000-5020.",
            file=sys.stderr,
        )
        sys.exit(1)

    print(f"Found available port. Launching server on port {port}...")

    LOGLEVEL_KEY = "LOG_LEVEL"
    loglevel = os.environ.get(LOGLEVEL_KEY, "INFO")
    threads = os.environ.get("ARK_THREADS", "4")
    if platform.system() == "Windows":
        args = [
            "waitress-serve",
            "--channel-timeout",
            "3600",
            "--threads",
            threads,
            "--port",
            str(port),
            "--call",
            "main:create_app",
        ]

    else:
        args = [
            "gunicorn",
            "--bind",
            f"0.0.0.0:{port}",
            "--timeout",
            "0",
            "--threads",
            threads,
            "--log-level",
            loglevel,
            "--access-logfile",
            "-",
            "main:create_app()",
        ]

    _ = subprocess.run(args, stdout=None, stderr=None, text=True, cwd=PROJECT_DIR)


def cli_entrypoint_mirai():
    cli_entrypoint("mirai")


if __name__ == "__main__":
    cli_entrypoint_mirai()
