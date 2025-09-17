"""Release automation script for dpd-client.

Steps:
1. Ensure git working tree is clean.
2. Run linters and tests (ruff, mypy, pytest).
3. Build distributions via ``uv build``.
4. Optionally publish to PyPI using ``uv publish`` when the ``--publish`` flag is provided.

Usage examples:
    uv run python scripts/release.py --version 0.2.0
    uv run python scripts/release.py --version 0.2.0 --publish
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path
from types import ModuleType

if sys.version_info >= (3, 11):
    import tomllib as toml_reader
else:  # Python < 3.11
    import tomli as toml_reader

from dotenv import load_dotenv

_toml_writer_module: ModuleType | None
try:
    import tomli_w as _toml_writer_module
except ModuleNotFoundError:
    _toml_writer_module = None

toml_writer: ModuleType | None = _toml_writer_module

REPO_ROOT = Path(__file__).resolve().parent.parent


class ReleaseError(RuntimeError):
    pass


def run(
    cmd: list[str], *, check: bool = True, capture_output: bool = False
) -> subprocess.CompletedProcess[str]:
    print(f":: {' '.join(cmd)}")
    return subprocess.run(
        cmd,
        cwd=REPO_ROOT,
        check=check,
        text=True,
        stdout=subprocess.PIPE if capture_output else None,
        stderr=subprocess.PIPE if capture_output else None,
    )


def ensure_clean_git() -> None:
    result = run(["git", "status", "--short"], check=False, capture_output=True)
    if result.stdout and result.stdout.strip():
        raise ReleaseError("Working tree is dirty; commit or stash changes before releasing.")


def read_version() -> str:
    data = toml_reader.loads((REPO_ROOT / "pyproject.toml").read_text())
    return data["project"]["version"]


def update_version(version: str) -> None:
    if toml_writer is None:
        raise ReleaseError(
            "tomli-w is not installed; add it to dev dependencies (uv add tomli-w --group dev)."
        )

    path = REPO_ROOT / "pyproject.toml"
    data = toml_reader.loads(path.read_text())
    data["project"]["version"] = version
    path.write_text(toml_writer.dumps(data))


def run_checks() -> None:
    run(["uv", "run", "ruff", "check", "."])
    run(["uv", "run", "mypy", "."])
    run(["uv", "run", "pytest"])


def build_dist() -> None:
    run(["uv", "build"])


def publish_dist() -> None:
    run(["uv", "publish"])


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Release helper for dpd-client")
    parser.add_argument("--version", help="New version to set in pyproject.toml")
    parser.add_argument(
        "--publish",
        action="store_true",
        help="Publish artifacts to PyPI after building",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        load_dotenv()
        ensure_clean_git()
        current_version = read_version()
        if args.version:
            update_version(args.version)
            print(f"Version updated from {current_version} to {args.version}")
        else:
            print(f"Using existing version: {current_version}")
        run_checks()
        build_dist()
        if args.publish:
            publish_dist()
            print("Published artifacts to PyPI via uv publish")
        else:
            print("Build complete (publishing skipped). Use --publish to upload.")
    except subprocess.CalledProcessError as exc:  # noqa: PERF203 - release script
        print(f"Command failed: {exc}", file=sys.stderr)
        return exc.returncode
    except ReleaseError as exc:  # noqa: PERF203
        print(f"Release aborted: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
