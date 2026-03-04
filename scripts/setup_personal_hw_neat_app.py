#!/usr/bin/env python3
"""
One-time setup so each person can deploy their own hw-neat Streamlit app in a dedicated module.

Use in training when many people deploy from their own clone: each person gets a new module
modules/hw-neat-<suffix>/ and a config config.hw-neat-<suffix>.yaml. The default app stays
in modules/hw-neat and is not modified.

Usage (from repo root):
  python scripts/setup_personal_hw_neat_app.py <suffix>

Examples:
  python scripts/setup_personal_hw_neat_app.py jag
  python scripts/setup_personal_hw_neat_app.py alice

What it does:
  1. Creates modules/hw-neat-<suffix>/ with module.toml, data_sets, and streamlit app (copied from modules/hw-neat/streamlit/hw-neat/).
  2. Creates config.hw-neat-<suffix>.yaml that selects modules/hw-neat and modules/hw-neat-<suffix>.

After running, use: cdf build --env hw-neat-<suffix> and cdf deploy --env hw-neat-<suffix>.
"""

import argparse
import re
import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path

SOURCE_MODULE = "modules/hw-neat"
SOURCE_APP_DIR = "streamlit/hw-neat"
SOURCE_DATASET = "data_sets/hw-neat-dataset.DataSet.yaml"

MODULE_TOML_TEMPLATE = """[module]
title = "Hello World NEAT ({suffix})"

[packages]
tags = [
    "hello-world",
    "neat",
    "data-model",
    "demo",
    "personal",
]
"""

DATASET_YAML = """externalId: hw-neat-dataset
name: Hello World NEAT Dataset
description: Dataset for Hello World NEAT data model demo
"""

STREAMLIT_YAML_TEMPLATE = """externalId: hw-neat-{suffix}
name: Hello World NEAT ({suffix})
creator: {creator}
description: "{version} - Hello World NEAT data management interface demo ({suffix})"
entrypoint: main.py
dataSetExternalId: hw-neat-dataset
"""

CONFIG_TEMPLATE = """environment:
  name: bgfast
  project: bgfast
  validation-type: dev
  selected:
  ### ===========================================
  ### HELLO WORLD NEAT DATA MODEL (shared)
  ### ===========================================
  - modules/hw-neat                          ### Hello World NEAT data model + default Streamlit app

  ### ===========================================
  ### PERSONAL HW-NEAT APP ({suffix})
  ### ===========================================
  - modules/hw-neat-{suffix}                  ### Hello World NEAT personal app ({suffix})

variables:
  # Environment Configuration
  default_location: hw-neat
  source_asset: hw-neat
  source_event: hw-neat
  source_workorder: hw-neat
  source_files: hw-neat
  source_timeseries: hw-neat
  source_simulated: hw-neat

  # Hello World NEAT Data Model Configuration
  hw_neat_space: hw-neat
  hw_neat_container: HWNeatBasic
  hw_neat_view: HWNeatBasic
  hw_neat_dataset: hw-neat-dataset

  # Data Model Configuration
  company_process_industries_extensions: hw_neat_data
  company_process_industries_extensions_external_id: HWNeat
  company_process_industries_extensions_external_id_destination: HWNeat

  # Authentication Configuration
  superuser_sourceid: ${{SUPERUSER_SOURCEID_ENV}}
  my_user_identifier: ${{USER_IDENTIFIER}}
  readwrite_source_id: ${{SUPERUSER_SOURCEID_ENV}}

  # CDF Configuration (populated from .env file)
  CDF_PROJECT: ${{CDF_PROJECT}}
  CDF_CLUSTER: ${{CDF_CLUSTER}}
  CDF_URL: https://${{CDF_CLUSTER}}.cognitedata.com

  # IDP Configuration
  IDP_CLIENT_ID: ${{IDP_CLIENT_ID}}
  IDP_CLIENT_SECRET: ${{IDP_CLIENT_SECRET}}
  IDP_SCOPES: ${{IDP_SCOPES}}
  IDP_TENANT_ID: ${{IDP_TENANT_ID}}
  IDP_TOKEN_URL: ${{IDP_TOKEN_URL}}

  # Function Configuration
  function_clientId: ${{FUNCTION_CLIENT_ID}}
  function_clientSecret: ${{FUNCTION_CLIENT_SECRET}}
  transformation_clientId: ${{TRANSFORMATION_CLIENT_ID}}
  transformation_clientSecret: ${{TRANSFORMATION_CLIENT_SECRET}}

  # Hello World NEAT Testing Configuration
  hw_neat_test_asset_prefix: hw_test_
  hw_neat_sample_asset_count: 10
  hw_neat_cleanup_enabled: true
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
        description="Set up a personal hw-neat module and config (modules/hw-neat-<suffix>, config.hw-neat-<suffix>.yaml)."
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

    source_module_path = repo_root / SOURCE_MODULE
    source_app_dir = source_module_path / "streamlit" / "hw-neat"
    target_module_dir = repo_root / "modules" / f"hw-neat-{suffix}"
    target_app_dir = target_module_dir / "streamlit" / f"hw-neat-{suffix}"
    target_dataset_dir = target_module_dir / "data_sets"
    config_path = repo_root / f"config.hw-neat-{suffix}.yaml"

    creator = get_creator(repo_root, suffix)

    # --- Verbose: paths ---
    print("=" * 60)
    print("SETUP PERSONAL HW-NEAT MODULE (verbose)")
    print("=" * 60)
    print()
    print("Creator (for Streamlit YAML):")
    print(f"  {creator}")
    if "@" in creator:
        print("  (from git config user.email)")
    else:
        print(f"  (fallback: suffix '{suffix}', git user.email not set)")
    print()
    print("Paths:")
    print(f"  Repo root:          {repo_root}")
    print(f"  Source app:          {source_app_dir}")
    print(f"  Target module:       {target_module_dir}")
    print(f"  Target app:          {target_app_dir}")
    print(f"  Config file:         {config_path}")
    print()

    if not source_app_dir.is_dir():
        print(f"Error: Source app dir not found: {source_app_dir}")
        sys.exit(1)
    if target_module_dir.exists():
        print(f"Error: Module dir already exists: {target_module_dir}")
        print("  Remove it first or use a different suffix.")
        sys.exit(1)
    if config_path.exists():
        print(f"Error: Config already exists: {config_path}")
        sys.exit(1)

    # --- 1. Create module dir and module.toml ---
    print("Step 1: Create module and app structure")
    print("-" * 40)
    target_module_dir.mkdir(parents=True, exist_ok=True)
    (target_module_dir / "module.toml").write_text(
        MODULE_TOML_TEMPLATE.format(suffix=suffix), encoding="utf-8"
    )
    print(f"  Created: {target_module_dir / 'module.toml'}")
    target_dataset_dir.mkdir(parents=True, exist_ok=True)
    (target_module_dir / "data_sets" / "hw-neat-dataset.DataSet.yaml").write_text(DATASET_YAML, encoding="utf-8")
    print(f"  Created: {target_module_dir / 'data_sets/hw-neat-dataset.DataSet.yaml'}")
    target_app_dir.mkdir(parents=True, exist_ok=True)
    print()

    # --- 2. Copy app files (main.py, data_modeling.py, requirements.txt) ---
    print("Step 2: Copy Streamlit app files")
    print("-" * 40)
    copied_files = []
    for p in sorted(source_app_dir.rglob("*")):
        if p.is_file():
            rel = p.relative_to(source_app_dir)
            dest = target_app_dir / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(p, dest)
            copied_files.append(rel)
            print(f"  Copied: {rel}")
    print()

    # --- 3. Write Streamlit YAML ---
    print("Step 3: Create Streamlit YAML")
    print("-" * 40)
    version = f"v{date.today():%Y.%m.%d}.v1"
    streamlit_yaml = target_module_dir / "streamlit" / f"hw-neat-{suffix}.Streamlit.yaml"
    yaml_content = STREAMLIT_YAML_TEMPLATE.format(suffix=suffix, creator=creator, version=version)
    streamlit_yaml.write_text(yaml_content, encoding="utf-8")
    print(f"  Written: {streamlit_yaml}")
    print()

    # --- 4. Write config ---
    print("Step 4: Create config file")
    print("-" * 40)
    config_content = CONFIG_TEMPLATE.format(suffix=suffix)
    config_path.write_text(config_content, encoding="utf-8")
    print(f"  Written: {config_path}")
    print()

    # --- 5. Verify ---
    print("Step 5: Verify")
    print("-" * 40)
    errors = []
    if not (target_module_dir / "module.toml").is_file():
        errors.append("module.toml missing")
    if not (target_module_dir / "data_sets" / "hw-neat-dataset.DataSet.yaml").is_file():
        errors.append("data_sets/hw-neat-dataset.DataSet.yaml missing")
    if not streamlit_yaml.is_file():
        errors.append("Streamlit YAML missing")
    for rel in copied_files:
        if not (target_app_dir / rel).is_file():
            errors.append(f"App file missing: {rel}")
    if not config_path.is_file():
        errors.append("config file missing")
    if errors:
        print("ERROR:")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)
    print("  OK: All paths present.")
    print()

    # --- Summary ---
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print()
    print("Created:")
    print(f"  Module:  {target_module_dir.resolve()}")
    print(f"  Config:  {config_path.resolve()}")
    print()
    print("Next steps:")
    print(f"  cdf build --env hw-neat-{suffix}")
    print(f"  cdf deploy --env hw-neat-{suffix} --dry-run")
    print(f"  cdf deploy --env hw-neat-{suffix}")
    print()
    print(f"In CDF you will see the default 'Hello World NEAT' and your 'Hello World NEAT ({suffix})'.")
    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
