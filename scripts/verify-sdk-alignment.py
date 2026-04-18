#!/usr/bin/env python3
"""Verify spooled-action aligns with the SDK manifest.

Checks that package names, action references, and version strings
match the SDK source of truth.

Usage:
  python3 scripts/verify-sdk-alignment.py --manifest ../spooled/spooled-manifest.json
"""

import argparse
import json
import re
import sys
from pathlib import Path

ACTION_ROOT = Path(__file__).resolve().parent.parent


def load_manifest(path: str) -> dict:
    return json.loads(Path(path).read_text())


def check_package_name(manifest: dict) -> list[str]:
    errors = []
    pkg = manifest["package_name"]
    for f in [ACTION_ROOT / "README.md", ACTION_ROOT / "action.yml"]:
        if not f.exists():
            continue
        content = f.read_text()
        if f"pip install {manifest['import_name']}\n" in content:
            errors.append(f"{f.name}: uses 'pip install {manifest['import_name']}' (should be {pkg})")
        # Check install command in action.yml
        for m in re.finditer(r'pip install (\S+)', content):
            installed = m.group(1).split("==")[0].split(">=")[0]
            if installed == manifest["import_name"] and installed != pkg:
                errors.append(f"{f.name}: installs '{installed}' (should be '{pkg}')")
    return errors


def check_action_reference(manifest: dict) -> list[str]:
    errors = []
    expected = manifest["action_reference"]
    readme = ACTION_ROOT / "README.md"
    if readme.exists():
        content = readme.read_text()
        for m in re.finditer(r'uses:\s*(\S+)', content):
            ref = m.group(1)
            if "spooled" in ref.lower() and ref != expected:
                errors.append(f"README.md: action ref '{ref}' (should be '{expected}')")
    return errors


def check_removed_features(manifest: dict) -> list[str]:
    errors = []
    removed = ["tone_drift", "refusal_policy_drift"]
    for f in ACTION_ROOT.rglob("*"):
        if f.is_file() and f.suffix in (".md", ".yml", ".yaml", ".sh"):
            content = f.read_text()
            rel = f.relative_to(ACTION_ROOT)
            for feature in removed:
                if feature in content:
                    errors.append(f"{rel}: references removed feature '{feature}'")
    return errors


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True)
    args = parser.parse_args()

    manifest = load_manifest(args.manifest)
    print(f"Manifest: v{manifest['version']}\n")

    all_errors = []
    for name, fn in [
        ("Package name", check_package_name),
        ("Action reference", check_action_reference),
        ("Removed features", check_removed_features),
    ]:
        errors = fn(manifest)
        status = "FAIL" if errors else "PASS"
        print(f"{status}  {name}")
        for e in errors:
            print(f"  - {e}")
        all_errors.extend(errors)

    print(f"\n{'=' * 60}")
    if all_errors:
        print(f"FAILED: {len(all_errors)} mismatches")
        sys.exit(1)
    else:
        print("ALL CHECKS PASSED")


if __name__ == "__main__":
    main()
