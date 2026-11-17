# Source Intake

## Local contract

- `.source/` is the local evidence root for source-driven AIDP work.
- `.source/README.md` must describe the source platform, migration or project goal, known constraints, and the most relevant artifacts.
- `.source/` may contain SQL, notebooks, exports, scripts, and requirement documents from platforms such as Databricks, Cloudera, SQL Server, Oracle, or document-only greenfield designs.

## Canonical commands

- `uv run codex-oci doctor`
- `uv run codex-oci aidp source inspect`
- `uv run codex-oci aidp manifest inspect --manifest <path>`
- `uv run codex-oci aidp blueprint medallion`

## Intake heuristics

- Start from `.source/README.md`, then inspect the highest-signal SQL, notebooks, exports, and design documents.
- Infer platform hints from filenames, directory names, and README language, but keep them as hints until the artifacts confirm the pattern.
- Separate planning from live execution: `.source` drives the plan; `.oci` and OCI CLI drive validation and mutation later.
- Map source evidence into medallion layers, reference data, control tables, stage tables, and batch-versus-streaming coexistence requirements.

## Good output shape

- Source platforms or platform hints.
- Key source systems and datasets.
- Expected medallion layers and control-state entities.
- Gaps, assumptions, and which next skill or wrapper command should be used.
