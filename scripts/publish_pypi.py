#!/usr/bin/env python3
"""
Build and publish the package using Astral's uv.

Usage:
  uv run -m scripts.publish_pypi --repo pypi
  uv run -m scripts.publish_pypi --repo testpypi

Auth (pick one):
  - Set UV_PUBLISH_TOKEN in env (recommended)
      Windows: set UV_PUBLISH_TOKEN=pypi-***
      Unix:    export UV_PUBLISH_TOKEN=pypi-***
  - Or rely on keyring/interactive if available (may prompt)
"""

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path


def run(cmd: list[str]) -> None:
    print("$", " ".join(cmd))
    subprocess.check_call(cmd)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default="pypi", choices=["pypi", "testpypi"])
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parents[1]
    dist_dir = project_root / "dist"
    if dist_dir.exists():
        shutil.rmtree(dist_dir)

    # Build with uv
    run(["uv", "build"])  # produces dist/

    # Publish with uv
    token = os.getenv("UV_PUBLISH_TOKEN")
    cmd = ["uv", "publish"]
    if args.repo == "testpypi":
        cmd += ["--index", "https://test.pypi.org/legacy/"]
    if token:
        cmd += ["--token", token]
    run(cmd)


if __name__ == "__main__":
    main()


