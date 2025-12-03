# agents/tools/shell_tool.py
"""
Shell Tool — Executes shell commands in a Docker sandbox
- No network access
- No sudo
- Limited file system access
- Timeout enforced
"""

import docker
import tempfile
import os
import json

class ShellTool:
    name = "shell"

    def __init__(self, sandboxed: bool = True):
        self.sandboxed = sandboxed
        self.client = docker.from_env()

        # Pull base image once
        try:
            self.client.images.get("python:3.11-slim")
        except docker.errors.ImageNotFound:
            print("Pulling sandbox image...")
            self.client.images.pull("python:3.11-slim")

    def run(self, command: str, timeout: int = 30) -> Dict[str, Any]:
        """Run shell command safely"""
        if not self.sandboxed:
            # Unsafe mode — only for local dev
            import subprocess
            try:
                result = subprocess.run(
                    command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=timeout
                )
                return {
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "exit_code": result.returncode
                }
            except Exception as e:
                return {"error": str(e)}

        # Sandboxed mode (Docker)
        with tempfile.TemporaryDirectory() as tmpdir:
            script_path = os.path.join(tmpdir, "run.sh")
            with open(script_path, "w") as f:
                f.write(f"#!/bin/bash\n{command}\n")
            os.chmod(script_path, 0o755)

            try:
                container = self.client.containers.run(
                    "python:3.11-slim",
                    command=["timeout", str(timeout), "/run.sh"],
                    volumes={tmpdir: {"bind": "/workspace", "mode": "rw"}},
                    working_dir="/workspace",
                    mem_limit="512m",
                    network_disabled=True,  # 🔒 No internet
                    detach=True,
                )
                result = container.wait()
                stdout = container.logs(stdout=True, stderr=False).decode()
                stderr = container.logs(stdout=False, stderr=True).decode()
                container.remove()
                return {
                    "stdout": stdout,
                    "stderr": stderr,
                    "exit_code": result["StatusCode"]
                }
            except Exception as e:
                return {"error": str(e)}
