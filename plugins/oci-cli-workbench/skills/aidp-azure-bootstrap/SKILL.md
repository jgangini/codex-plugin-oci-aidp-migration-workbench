---
name: aidp-azure-bootstrap
description: Bootstrap Azure CLI readiness and perform read-only Azure data-platform inventory for Azure-to-AIDP migration planning. Use when Codex needs to verify `az`, inspect the active Azure account or subscription, inventory ADLS/Blob, Synapse, Databricks, Data Factory, Event Hubs, Azure SQL, Cosmos DB, Key Vault, private networking, or hand off Azure findings into `.source`, `aidp-source-intake`, and `aidp-source-manifest` work.
---

# AIDP Azure Bootstrap

## Overview

Use this skill to prepare an Azure source environment for AIDP migration planning. Keep the flow read-only by default: verify Azure CLI, confirm the active subscription, inventory Azure data-platform resources, and translate findings into source-intake and manifest next steps.

## Prerequisites

- Azure CLI must be installed for live inspection.
- Azure login is required before subscription inventory.
- `.source/` is not required for bootstrap, but becomes the handoff target after Azure findings are coherent.
- `.oci/` is not required until follow-on AIDP validation, platform bootstrap, deploy, or runtime work.

## Workflow

1. Read `references/azure-data-platform-inventory.md` before running or proposing inventory commands.
2. Confirm Azure CLI readiness with `az version`. If Azure CLI cannot write logs under the user profile, use a temporary `AZURE_CONFIG_DIR` or request approval to run outside the sandbox.
3. Inspect the active account with `az account show` and list candidate subscriptions with `az account list`. Only run `az account set --subscription ...` when the user explicitly identifies the target subscription.
4. Inventory data-platform resources with read-only commands, scoped by resource group, subscription, or tags whenever the user provides them.
5. Convert findings into an AIDP migration handoff: source systems, storage roots, orchestration jobs, streaming lanes, private-network dependencies, security dependencies, and gaps.
6. If `.source/README.md` exists, align Azure findings with it. If it does not, recommend the minimum README content needed for `aidp-source-intake`.
7. Hand off to `$aidp-source-intake` for evidence-driven planning, then `$aidp-source-manifest` when the user is ready to shape `aidp/config/migration_manifest.json`.

## Rules

- Keep Azure bootstrap read-only by default. Do not create, update, delete, deploy, register providers, install extensions, or switch subscriptions unless the user explicitly asks.
- Do not print secrets, keys, connection strings, tokens, or full private credential material. Do not use admin-key or list-secret commands for inventory.
- Prefer scoped inventory over tenant-wide scans when resource groups, tags, naming conventions, or subscriptions are known.
- Treat Azure findings as source evidence. Do not mutate AIDP resources from this skill.
- Persist reports under `aidp/reports/` only when the user asks for saved evidence.
- When CLI output is incomplete because of permissions, report the missing permission and continue with the visible inventory instead of guessing.

## Outputs

- Azure CLI diagnostic summary.
- Active account and subscription summary, with sensitive values minimized.
- Data-platform inventory grouped by Azure service and migration relevance.
- Azure-to-AIDP handoff: what belongs in `.source/README.md`, what evidence to collect, and which AIDP skill should run next.
- Explicit blockers, gaps, and permissions that prevent a trustworthy inventory.
