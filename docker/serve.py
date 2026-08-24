"""Run the web and API processes together inside the production container."""

from __future__ import annotations

import os
from pathlib import Path
import signal
import subprocess
import sys
import time

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa


def ensure_jwt_keys() -> None:
    private_path = Path(os.environ["JWT_PRIVATE_KEY_PATH"])
    public_path = Path(os.environ["JWT_PUBLIC_KEY_PATH"])

    if private_path.exists() and public_path.exists():
        return
    if private_path.exists() != public_path.exists():
        raise RuntimeError(
            "Only one JWT key exists; restore the missing matching key or remove both."
        )

    private_path.parent.mkdir(parents=True, exist_ok=True)
    public_path.parent.mkdir(parents=True, exist_ok=True)

    private_key = rsa.generate_private_key(public_exponent=65537, key_size=4096)
    private_path.write_bytes(
        private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption(),
        )
    )
    public_path.write_bytes(
        private_key.public_key().public_bytes(
            encoding=serialization.Encoding.OpenSSH,
            format=serialization.PublicFormat.OpenSSH,
        )
    )
    private_path.chmod(0o600)
    public_path.chmod(0o644)
    print(f"Generated persistent JWT keys in {private_path.parent}", flush=True)


def stop_processes(processes: list[subprocess.Popen[bytes]]) -> None:
    for process in processes:
        if process.poll() is None:
            process.terminate()

    deadline = time.monotonic() + 10
    while time.monotonic() < deadline and any(
        process.poll() is None for process in processes
    ):
        time.sleep(0.1)

    for process in processes:
        if process.poll() is None:
            process.kill()


def main() -> int:
    ensure_jwt_keys()

    processes = [
        subprocess.Popen(
            [
                sys.executable,
                "-m",
                "uvicorn",
                "main:create_app",
                "--factory",
                "--host",
                "127.0.0.1",
                "--port",
                "8000",
            ]
        ),
        subprocess.Popen(["node", "build/index.js"]),
    ]
    stopping = False

    def handle_signal(_signum: int, _frame: object) -> None:
        nonlocal stopping
        stopping = True

    signal.signal(signal.SIGTERM, handle_signal)
    signal.signal(signal.SIGINT, handle_signal)

    try:
        while not stopping:
            for process in processes:
                return_code = process.poll()
                if return_code is not None:
                    return return_code or 1
            time.sleep(0.2)
        return 0
    finally:
        stop_processes(processes)


if __name__ == "__main__":
    raise SystemExit(main())
