import docker
import tempfile
import os

class CodeSandbox:
    def __init__(self):
        self.client = docker.from_env()
        # Pre-pull lightweight image
        try:
            self.client.images.get("python:3.11-slim")
        except:
            print("Pulling sandbox image (one-time)...")
            self.client.images.pull("python:3.11-slim")

    def run(self, code: str, timeout: int = 30) -> Dict[str, str]:
        with tempfile.TemporaryDirectory() as tmpdir:
            script_path = os.path.join(tmpdir, "script.py")
            with open(script_path, "w") as f:
                f.write(code)
            
            try:
                container = self.client.containers.run(
                    "python:3.11-slim",
                    command=["timeout", str(timeout), "python", "/script.py"],
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
                return {"stdout": stdout, "stderr": stderr, "exit_code": result["StatusCode"]}
            except Exception as e:
                return {"stdout": "", "stderr": str(e), "exit_code": -1}
