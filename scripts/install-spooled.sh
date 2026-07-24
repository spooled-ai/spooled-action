#!/usr/bin/env bash
set -euo pipefail

source_input="${SPOOLED_SOURCE_INPUT:-}"
version_input="${SPOOLED_VERSION_INPUT:-}"
extra_deps_input="${SPOOLED_EXTRA_DEPS_INPUT:-}"
action_path="${SPOOLED_ACTION_PATH:-}"

if [[ -n "$source_input" && -n "$version_input" ]]; then
  echo "::error::Set only one of spooled-source or spooled-version" >&2
  exit 2
fi

if [[ -n "$source_input" ]]; then
  if [[ -e "$source_input" ]]; then
    pip install "$source_input"
  else
    # Keep the complete PEP 508 requirement in one argv element. This lets a
    # workflow pin an unreleased Git commit/archive without shell evaluation.
    pip install "spooled-ai @ $source_input"
  fi
elif [[ -n "$version_input" ]]; then
  pip install "spooled-ai==$version_input"
elif [[ -n "$action_path" && -f "$action_path/../pyproject.toml" ]]; then
  pip install -e "$action_path/.."
else
  pip install spooled-ai
fi

if [[ -n "$extra_deps_input" ]]; then
  if [[ ! -f "$extra_deps_input" ]]; then
    echo "::error::extra-deps file not found: $extra_deps_input" >&2
    exit 2
  fi
  pip install -r "$extra_deps_input"
fi
