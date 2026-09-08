# Databricks notebook source
# DBTITLE 1,Retrieve job parameters
catalog_use = dbutils.widgets.get("catalog_use")
schema_use = dbutils.widgets.get("schema_use")

print(f"Target catalog: {catalog_use}")
print(f"Target schema:  {schema_use}")

# COMMAND ----------

# DBTITLE 1,Discover metric view YAML definitions
import os
from pathlib import Path

# Resolve path to fixtures/metric_views relative to this notebook
metric_views_path = Path(os.path.abspath("../fixtures/metric_views"))

# Find all .metric_view.yml files
yml_files = sorted(metric_views_path.glob("*.metric_view.yml"))

print(f"Found {len(yml_files)} metric view definition(s):")
for yml_file in yml_files:
    print(f"  - {yml_file.name}")

assert len(yml_files) > 0, f"No .metric_view.yml files found in {metric_views_path}"

# COMMAND ----------

# DBTITLE 1,Register metric views in target catalog.schema
for yml_file in yml_files:
    print(f"\nProcessing: {yml_file.name}")

    # Read YAML content and inject catalog/schema placeholders
    with open(yml_file, "r") as f:
        yaml_content = f.read()

    yaml_content = yaml_content.format(
        catalog=catalog_use,
        schema=schema_use
    )

    # Derive view name from filename (strip .metric_view.yml)
    view_name = yml_file.stem.replace(".metric_view", "")
    full_view_name = f"{catalog_use}.{schema_use}.{view_name}"

    # Build and execute the CREATE OR REPLACE VIEW DDL
    create_sql = f"""CREATE OR REPLACE VIEW {full_view_name}
WITH METRICS
LANGUAGE YAML
AS $$
{yaml_content}
$$"""

    print(f"  Registering: {full_view_name}")
    spark.sql(create_sql)
    print(f"  ✓ Success")

print(f"\n{'=' * 60}")
print(f"Done. Registered {len(yml_files)} metric view(s) in {catalog_use}.{schema_use}")