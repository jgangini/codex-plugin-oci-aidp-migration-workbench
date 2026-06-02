---
name: aidp-catalog-governance
description: Provision or align Data Catalog governance for the medallion layout, including glossary terms, taxonomy, entities, attributes, lineage, and cleanup of drifted metadata. Use when Codex needs to prepare or repair catalog governance for AIDP tables, align medallion naming with the manifest, or explain the governance prerequisites before validation or handoff.
---

# AIDP Catalog Governance

## Overview

Use this skill when the medallion data layout must be reflected in OCI Data Catalog. The focus is not just creating objects, but keeping the glossary, entities, and lineage aligned with the manifest and with the AIDP runtime outputs.

## Prerequisites

- `.oci/` is required for live OCI Data Catalog work.
- `.source/` is optional and only needed when governance design is still being derived from source evidence.

## Workflow

1. Read `references/catalog-governance.md` before mutating catalog state.
2. Gather the required inputs first: catalog id, glossary key if applicable, profile, and owner.
3. Apply taxonomy or glossary structure before entity and lineage provisioning.
4. Keep catalog naming aligned with the manifest's canonical medallion layout.
5. Write provisioning reports so later validation or handoff work can reuse them.

## Rules

- Treat glossary and lineage changes as live metadata mutations.
- Prefer deterministic medallion naming over ad hoc labels.
- If drift exists, explain whether the fix is additive, replacement, or cleanup before applying it.
- Keep catalog work separate from deployment work in the summary.
