# Project Memory — wb-metric-views

## Overview

Bundle for authoring and registering Unity Catalog metric views as part of the `wanderBricksSemtantics` monorepo. Teaching project demonstrating how Genie Code builds the UC Semantic Layer.

**Bundle root:** `/Users/matthew.giglia@databricks.com/wanderBricksSemtantics/wb-metric-views/`  
**Monorepo root:** `/Users/matthew.giglia@databricks.com/wanderBricksSemtantics/`  
**Sibling bundle:** `wb-genie-agent` (Genie Space consuming these metric views)

---

## Git Workflow

* **NEVER commit or merge directly to `main`.** All work is done in feature branches.
* Branch naming: `mg-genie-<short-description>` (e.g., `mg-genie-project-init`, `mg-genie-add-revenue-metrics`).
* Push the feature branch, then provide a PR title/description for manual merge.
* Commits use conventional-commit style: `feat:`, `fix:`, `docs:`, `chore:`, etc.

---

## Session Summaries

After meaningful work sessions, write a summary in `fixtures/sessions/`.

**Format:** `YYYY-MM-DD_short-description.md`  
**Dates:** Always use `datetime.now()` — never guess.

**Content structure:**

```markdown
# Session: <short description>
**Date:** YYYY-MM-DD

## Problems
- What issue(s) were addressed

## Root Causes
- Why the problem occurred (if applicable)

## Changes
- What was added/modified/removed

## Decisions
- Key choices made and rationale

## Files Modified
- List of files touched
```

**INDEX.md:** Maintain `fixtures/sessions/INDEX.md` in reverse-chronological order (newest first). Each entry links to the session file with a one-line summary.

---

## Targets

| Target | Mode | Workspace | Default |
| --- | --- | --- | --- |
| dev | development | fevm-hls-fde | yes |
| prod | production | fevm-hls-fde | no |

---

## Conventions

* Notebook paths default to `.ipynb`; use `.sql` only with `warehouse_id`.
* First notebook cell: `%pip install --upgrade databricks-sdk` + `dbutils.library.restartPython()`.

### Resource References

**Always** reference deployed resources via their bundle interpolation — never hardcode IDs, names, or raw variables:

```yaml
${resources.<resource_type>.<resource_key>.<value_name>}
```

Examples:

```yaml
# Schemas
${resources.schemas.metric_views_schema.name}
${resources.schemas.metric_views_schema.id}

# Jobs
${resources.jobs.deploy_metrics.id}

# Pipelines
${resources.pipelines.ingest_pipeline.id}

# SQL Warehouses
${resources.sql_warehouses.compute.id}

# Volumes
${resources.volumes.fixtures.id}
```

This ensures dependency ordering, avoids drift between targets, and makes refactors safe. Use `${var.*}` only within the resource definition itself (e.g., the schema resource reads `${var.catalog}`) — downstream consumers always go through `${resources.*}`.

---

## Metric View Registration Pattern

* Metric view YAML definitions live in `fixtures/metric_views/` and follow the `*.metric_view.yml` naming convention.
* A generic registration job discovers all metric view YAML files and registers them into the target schema.
* The registration task passes `catalog_use` from `${var.catalog}` and `schema_use` from `${resources.schemas.wb_metric_views_schema.name}`.
* The registration notebook must be target-flexible: inject catalog and schema at runtime, derive the metric view name from the file name, and publish the metric view into the target location.
* Start with simple verification metric views against the WanderBricks properties sample before expanding to richer semantic-layer definitions.