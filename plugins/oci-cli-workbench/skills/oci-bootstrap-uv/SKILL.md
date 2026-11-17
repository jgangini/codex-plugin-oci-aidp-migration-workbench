---
name: oci-bootstrap-uv
description: Bootstrap and repair the Python 3.11 + uv environment for this repository, install the local OCI CLI toolchain, validate the `codex-oci` wrapper, and optionally export a compatibility `requirements.txt`. Use when Codex needs to prepare `.venv`, refresh dependencies, diagnose missing `oci`, or ready the workspace for OCI CLI work.
---

# OCI Bootstrap with uv

## Overview

Prepare this repo for OCI work with the repo-local `uv` workflow. Treat `pyproject.toml` and `uv.lock` as the source of truth and use repo scripts instead of ad hoc install steps whenever possible.

## Prerequisites

- `.source/` is not required for bootstrap.
- `.oci/` is only required when the flow includes `uv run codex-oci doctor --live` or other live OCI checks.

## Canonical Workflow

1. Run `.\scripts\bootstrap-dev.ps1` from the repo root.
2. Use `-RecreateVenv` only when the environment is corrupted or must be rebuilt from scratch.
3. Use `-LiveDoctor` only when a read-only network check against OCI is appropriate.
4. Use `-ExportRequirements` only when another tool explicitly needs `requirements.txt`.

## Manual Fallback

If the bootstrap script is unavailable or needs repair, run the sequence directly:

```powershell
uv venv --python 3.11 .venv
uv sync
uv run oci --version
uv run codex-oci doctor
```

Export compatibility requirements only on demand:

```powershell
uv export --format requirements.txt --output-file requirements.txt
```

## Rules

- Prefer `uv run ...` over activating `.venv` unless a human explicitly asks for an interactive shell.
- Do not use `uv pip install -r requirements.txt` as the primary repo bootstrap path.
- Never commit `.venv/` or `.oci/`.
- Treat `oci` missing from PATH as an environment issue to fix through `uv sync`, not by installing random global tooling.
