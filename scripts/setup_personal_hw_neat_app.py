#!/usr/bin/env python3
"""
One-time setup so each person can deploy their own hw-neat Streamlit app alongside the default.

Use in training when many people deploy from their own clone: each person gets a unique app
in CDF (e.g. hw-neat-jag, hw-neat-alice). The default app (hw-neat) is left unchanged in
the repo so it stays under source control.

Usage (from repo root):
  python scripts/setup_personal_hw_neat_app.py <suffix>

Examples:
  python scripts/setup_personal_hw_neat_app.py jag
  python scripts/setup_personal_hw_neat_app.py alice

What it does:
  1. Copies modules/hw-neat/streamlit/hw-neat/ to streamlit/hw-neat-<suffix>/
  2. Creates streamlit/hw-neat-<suffix>.Streamlit.yaml with externalId hw-neat-<suffix>
  (The default hw-neat app and hw-neat.Streamlit.yaml are not modified.)

After running, deploy will push both the default app and your personal app. Use your
personal app in CDF to avoid overwriting others' work.
"""

import argparse
import re
import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path

STREAMLIT_DIR = "modules/hw-neat/streamlit"
SOURCE_APP_DIR = "hw-neat"
SOURCE_YAML = "hw-neat.Streamlit.yaml"

YAML_TEMPLATE = """externalId: hw-neat-{suffix}
name: Hello World NEAT ({suffix})
creator: {creator}
description: "{version} - Hello World NEAT data management interface demo ({suffix})"
entrypoint: main.py
dataSetExternalId: hw-neat-dataset
"""


def get_creator(repo_root: Path, suffix: str) -> str:
    """Use git user.email if set; otherwise the name (suffix) passed in."""
    try:
        out = subprocess.run(
            ["git", "config", "user.email"],
            cwd=repo_root,
            capture_output=True,
            text=True,
            timeout=5,
        )
        if out.returncode == 0 and out.stdout and out.stdout.strip():
            return out.stdout.strip()
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    return suffix


def main():
    parser = argparse.ArgumentParser(
        description="Set up a personal hw-neat Streamlit app (keeps the default app unchanged)."
    )
    parser.add_argument(
        "suffix",
        help="Your unique suffix (e.g. jag, alice). Use lowercase letters, numbers, or hyphens.",
    )
    parser.add_argument(
        "--repo",
        default=None,
        help="Repo root path (default: auto-detect from script location)",
    )
    args = parser.parse_args()

    suffix = args.suffix.strip().lower()
    if not re.match(r"^[a-z0-9]([a-z0-9-]*[a-z0-9])?$", suffix):
        print("Error: suffix must be lowercase letters, numbers, or hyphens (e.g. jag, alice).")
        sys.exit(1)

    if args.repo:
        repo_root = Path(args.repo).resolve()
    else:
        repo_root = Path(__file__).resolve().parent.parent

    streamlit_path = repo_root / STREAMLIT_DIR
    source_dir = streamlit_path / SOURCE_APP_DIR
    source_yaml = streamlit_path / SOURCE_YAML
    target_dir = streamlit_path / f"hw-neat-{suffix}"
    target_yaml = streamlit_path / f"hw-neat-{suffix}.Streamlit.yaml"

    creator = get_creator(repo_root, suffix)

    # --- Verbose: paths ---
    print("=" * 60)
    print("SETUP PERSONAL HW-NEAT APP (verbose)")
    print("=" * 60)
    print()
    print("Creator (for Streamlit YAML):")
    print(f"  {creator}")
    if "@" in creator:
        print("  (from git config user.email)")
    else:
        print(f"  (fallback: name passed in '{suffix}', git user.email not set)")
    print()
    print("Paths:")
    print(f"  Repo root:        {repo_root}")
    print(f"  Streamlit dir:     {streamlit_path}")
    print(f"  Source app dir:    {source_dir}")
    print(f"  Source YAML:      {source_yaml} (unchanged)")
    print(f"  Target app dir:    {target_dir}")
    print(f"  Target YAML:      {target_yaml}")
    print()

    if not source_dir.is_dir():
        print(f"Error: Source app dir not found: {source_dir}")
        sys.exit(1)
    if not source_yaml.is_file():
        print(f"Error: Source YAML not found: {source_yaml}")
        sys.exit(1)
    if target_dir.exists():
        print(f"Error: Personal app dir already exists: {target_dir}")
        print("  If you want to re-run, remove it first or use a different suffix.")
        sys.exit(1)
    if target_yaml.exists():
        print(f"Error: Personal YAML already exists: {target_yaml}")
        sys.exit(1)

    # --- 1. Copy app directory (verbose: list what we copy) ---
    print("Step 1: Copy app directory")
    print("-" * 40)
    print(f"  Copying directory:")
    print(f"    FROM: {source_dir}")
    print(f"    TO:   {target_dir}")
    copied_files = []
    for p in sorted(source_dir.rglob("*")):
        rel = p.relative_to(source_dir)
        copied_files.append(rel)
    for rel in copied_files:
        print(f"      {SOURCE_APP_DIR}/{rel}")
    print()
    shutil.copytree(source_dir, target_dir)
    print(f"  Created directory: {target_dir}")
    for rel in copied_files:
        print(f"    Created file: {target_dir / rel}")
    print()

    # --- 2. Write personal Streamlit YAML (verbose: show content) ---
    print("Step 2: Create Streamlit YAML for personal app")
    print("-" * 40)
    version = f"v{date.today():%Y.%m.%d}.v1"
    yaml_content = YAML_TEMPLATE.format(suffix=suffix, creator=creator, version=version)
    print(f"  File to create: {target_yaml}")
    print("  File content (exact):")
    print("  ---")
    for line in yaml_content.splitlines():
        print(f"  {line}")
    print("  ---")
    print()
    target_yaml.write_text(yaml_content, encoding="utf-8")
    print(f"  Written: {target_yaml}")
    print()

    # --- Summary ---
    print("=" * 60)
    print("SUMMARY OF CHANGES")
    print("=" * 60)
    print()
    print("Directories created:")
    print(f"  1. {target_dir}")
    print()
    print("Files created:")
    for rel in copied_files:
        print(f"  - {target_dir / rel}")
    print(f"  - {target_yaml}")
    print()
    print("Files/directories NOT modified (left as-is for source control):")
    print(f"  - {source_dir}")
    print(f"  - {source_yaml}")
    print()
    print("Next steps:")
    print("  cdf build --env hw-neat")
    print("  cdf deploy --env hw-neat --dry-run")
    print("  cdf deploy --env hw-neat")
    print()
    print("In CDF you will see two apps: the default 'Hello World NEAT' and your")
    print(f"'Hello World NEAT ({suffix})' (externalId: hw-neat-{suffix}). Use your")
    print("personal app to avoid overwriting others' work.")
    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
