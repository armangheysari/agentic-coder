from pathlib import Path
import shutil
import subprocess

from agents import function_tool


SANDBOX_DIR = Path(__file__).parents[2] / "sandbox"
SANDBOX_DIR.mkdir(parents=True, exist_ok=True)


def reset_sandbox() -> None:
    if SANDBOX_DIR.exists():
        shutil.rmtree(SANDBOX_DIR)
    SANDBOX_DIR.mkdir(parents=True)
    print("[sandbox] initializing uv project with gradio...")
    subprocess.run(["uv", "init", "--bare", "--python", "3.13"], cwd=SANDBOX_DIR, check=True)
    subprocess.run(["uv", "add", "gradio"], cwd=SANDBOX_DIR, check=True)
    print("[sandbox] ready")


@function_tool
def list_sandbox_files() -> str:
    """List the filenames currently in the sandbox directory."""
    names = sorted(p.name for p in SANDBOX_DIR.iterdir())
    print(f"  [tool] list_sandbox_files -> {len(names)} files")
    return "\n".join(names) if names else "The sandbox is empty."


@function_tool
def read_sandbox_file(filename: str) -> str:
    """Read and return the text contents of a file in the sandbox directory."""
    path = SANDBOX_DIR / filename
    if not path.is_file():
        print(f"  [tool] read_sandbox_file({filename}) -> not found")
        return f"No such file in the sandbox: {filename}"
    print(f"  [tool] read_sandbox_file({filename}) -> {path.stat().st_size} bytes")
    return path.read_text()


@function_tool
def write_sandbox_file(filename: str, content: str) -> str:
    """Write text to a file in the sandbox directory, replacing any existing file."""
    path = SANDBOX_DIR / filename
    path.write_text(content)
    print(f"  [tool] write_sandbox_file({filename}) <- {len(content)} chars")
    return f"Wrote {len(content)} characters to {filename}."


@function_tool
def run_sandbox_python(filename: str) -> str:
    """Execute a Python file from the sandbox directory inside an ephemeral Docker container."""
    print(f"  [tool] run_sandbox_python({filename}) ...")
    try:
        result = subprocess.run(
            [
                "docker", "run", "--rm",
                "-v", f"{SANDBOX_DIR}:/workspace",
                "-w", "/workspace",
                "ghcr.io/astral-sh/uv:python3.13-bookworm-slim",
                "uv", "run", filename,
            ],
            capture_output=True,
            text=True,
            timeout=300,
        )
        status = "ok" if result.returncode == 0 else f"exit {result.returncode}"
        print(f"  [tool] run_sandbox_python({filename}) -> {status}")
        return (
            f"Exit code: {result.returncode}\n\n"
            f"--- stdout ---\n{result.stdout or '(empty)'}\n\n"
            f"--- stderr ---\n{result.stderr or '(empty)'}"
        )
    except subprocess.TimeoutExpired as e:
        stdout = e.stdout.decode() if isinstance(e.stdout, bytes) else (e.stdout or "")
        stderr = e.stderr.decode() if isinstance(e.stderr, bytes) else (e.stderr or "")
        print(f"  [tool] run_sandbox_python({filename}) -> timeout")
        return (
            "The script timed out after 300 seconds.\n\n"
            f"--- stdout so far ---\n{stdout or '(empty)'}\n\n"
            f"--- stderr so far ---\n{stderr or '(empty)'}"
        )


sandbox_tools = [list_sandbox_files, read_sandbox_file, write_sandbox_file, run_sandbox_python]
