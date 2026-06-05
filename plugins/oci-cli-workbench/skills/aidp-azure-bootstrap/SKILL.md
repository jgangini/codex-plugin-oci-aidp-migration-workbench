---
name: aidp-azure-bootstrap
description: Bootstrap Azure CLI readiness and perform read-only Azure data-platform inventory for Azure-to-AIDP migration planning. Use when Codex needs to verify `az`, inspect the active Azure account or subscription, inventory ADLS/Blob, Synapse, Databricks, Data Factory, Event Hubs, Azure SQL, Cosmos DB, Key Vault, private networking, or hand off Azure findings into `.source`, `aidp-source-intake`, and `aidp-source-manifest` work.
---

# AIDP Azure Bootstrap

## Overview

Use this skill to prepare an Azure source environment for AIDP migration planning. Keep the flow read-only by default: verify Azure CLI, confirm the active subscription, inventory Azure data-platform resources, and translate findings into source-intake and manifest next steps. Prefer the project-local `.az/` context for Azure CLI and Databricks configuration so Azure state is clearly separated from OCI state.

## Prerequisites

- Azure CLI must be installed for live inspection.
- Azure login is required before subscription inventory.
- `.az/` is the recommended project-local Azure context root. Use `.az/cli/` as `AZURE_CONFIG_DIR` when isolating CLI sessions from the user profile.
- `.source/` is not required for bootstrap, but becomes the handoff target after Azure findings are coherent.
- `.oci/` is not required until follow-on AIDP validation, platform bootstrap, deploy, or runtime work.

## Workflow

1. Read `references/azure-data-platform-inventory.md` before running or proposing inventory commands.
2. Initialize or verify the local `.az/` layout when the repo will perform repeatable Azure work: `.az/cli/`, `.az/azure.env.example`, and `.az/databricks.env.example`.
3. Confirm Azure CLI readiness with `az version`. Prefer `.az/cli/` as `AZURE_CONFIG_DIR` when Azure CLI would otherwise write logs or tokens under the user profile.
4. Inspect the active account with `az account show` and list candidate subscriptions with `az account list`. Only run `az account set --subscription ...` when the user explicitly identifies the target subscription.
5. Inventory data-platform resources with read-only commands, scoped by resource group, subscription, or tags whenever the user provides them.
6. Convert findings into an AIDP migration handoff: source systems, storage roots, orchestration jobs, streaming lanes, private-network dependencies, security dependencies, and gaps.
7. For Databricks migrations, capture or request real console evidence for source tables, join SQL, and `COUNT(*)` validation; CLI or API inventory can support the claim but does not replace console evidence in reports.
8. If `.source/README.md` exists, align Azure findings with it. If it does not, recommend the minimum README content needed for `aidp-source-intake`.
9. Hand off to `$aidp-source-intake` for evidence-driven planning, then `$aidp-source-manifest` when the user is ready to shape `aidp/config/migration_manifest.json`.

## Rules

- Keep Azure bootstrap read-only by default. Do not create, update, delete, deploy, register providers, install extensions, or switch subscriptions unless the user explicitly asks.
- Do not print secrets, keys, connection strings, tokens, or full private credential material. Do not use admin-key or list-secret commands for inventory.
- Treat `.az/` as sensitive local runtime state. Do not commit `.az/cli/`, Azure tokens, Databricks tokens, tenant ids, subscription ids, user ids, full workspace URLs, or generated Azure CLI logs.
- Do not label generated diagrams, redrawn pages, or API summaries as Azure Portal or Databricks console screenshots.
- Keep `.az/` for Azure and `.oci/` for OCI/AIDP. Do not require `.oci/` during read-only Azure bootstrap.
- Prefer scoped inventory over tenant-wide scans when resource groups, tags, naming conventions, or subscriptions are known.
- Treat Azure findings as source evidence. Do not mutate AIDP resources from this skill.
- Persist reports under `aidp/reports/` only when the user asks for saved evidence.
- When CLI output is incomplete because of permissions, report the missing permission and continue with the visible inventory instead of guessing.

## Outputs

- Azure CLI diagnostic summary.
- Active account and subscription summary, with sensitive values minimized or redacted.
- `.az/` readiness summary, including whether a project-local `AZURE_CONFIG_DIR` is active.
- Data-platform inventory grouped by Azure service and migration relevance.
- Azure-to-AIDP handoff: what belongs in `.source/README.md`, what evidence to collect, and which AIDP skill should run next.
- Databricks evidence checklist for source objects, join materialization, and row-count validation when Databricks is in scope.
- Explicit blockers, gaps, and permissions that prevent a trustworthy inventory.
