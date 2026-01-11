# Data Pipeline: GitHub → Databricks → Silver Layer → Gold Layer → Synapse

Project type: Data Engineering / ETL / Azure Databricks / Azure Data Factory / Synapse

## 📌 Overview
This repository documents a layered data engineering workflow that:
- Ingests raw files from GitHub into Azure Blob / ADLS Gen2,
- Uses Azure Data Factory pipelines (Lookup + ForEach + Copy) to move data into a Bronze/raw zone,
- Processes and standardizes data in Databricks (Silver layer),
- Creates business-ready tables (Gold layer),
- Exposes Gold tables to Azure Synapse Analytics for reporting and BI.

Architecture:
GitHub → Blob Storage (ADLS Gen2) → Azure Data Factory (ingest) → Databricks (transform) → Silver Layer → Gold Layer → Azure Synapse

---

## 🧭 What’s included (from your submission)
- Databricks notebook: `silver_layer.py` (you provided the notebook code that reads CSVs from Bronze, performs transformations, and writes Parquet to Silver).
- ADF pipeline screenshots (Lookup + ForEach + Copy pattern) — labelled Image 1..4 in your message for reference.
  - Image 1: Azure resource list screenshot
  - Image 2: ADF pipeline single-panel screenshot (Lookup → ForEach → Copy)
  - Image 3: ADF pipeline with Datasets panel visible
  - Image 4: Synapse Studio create schema screen (create schema gold;)

> Note: I did not embed or modify the actual screenshots. Add them into the repository's `assets/` or `docs/` folder and reference them from this README (instructions below).

---

## ⚙️ Key Components & Flow

1. GitHub Source
   - Raw CSVs (example: Calendar, Customers, Products, Sales_2015/2016/2017, Returns, Territories, etc.) stored in GitHub or another raw source.
   - ADF pipeline enumerates files (Lookup → ForEach) and uses Copy Activity to push them into your Bronze storage container.

2. Bronze (Raw Zone)
   - Raw files landed into `abfss://bronze@<storage>/...`
   - Keep raw data immutable — append-only with partitioning if required.

3. Databricks (Silver layer)
   - Notebook `silver_layer.py` reads CSV files from Bronze, applies cleaning and basic enrichment, and writes Parquet files into the Silver container:
     - Adds Month/Year to Calendar
     - Concatenates fullName in Customers
     - Normalizes ProductSKU/ProductName
     - Unifies Sales files then converts timestamps/cleans columns
   - Output location examples (as in notebook):
     - `abfss://silver@<storage>/Calendar`
     - `abfss://silver@<storage>/Customers`
     - `abfss://silver@<storage>/Products`
     - `abfss://silver@<storage>/sales`
   - Silver is the trusted, cleaned layer — good for joins and downstream transformations.

4. Gold (Business layer)
   - Create views/tables on top of Silver to represent business concepts (sales_by_region, daily_revenue, product_performance).
   - Register or persist Gold tables in Synapse or as Delta tables accessible by Synapse.

5. Azure Synapse
   - Consume the Gold layer in Synapse for analytics, create schemas (e.g. `CREATE SCHEMA gold;`) and expose to Power BI or other BI tools.

---

## Security & Secrets (Important)
The notebook you provided includes inline Spark configuration for OAuth client credentials (client id, client secret, and tenant). NEVER store secrets directly in notebooks or checked-in code.

Recommended secure approaches:
- Use Databricks Secrets backed by Azure Key Vault:
  ```python
  # Example (do NOT store actual secrets in code)
  client_id = dbutils.secrets.get(scope="my-scope", key="sp-client-id")
  client_secret = dbutils.secrets.get(scope="my-scope", key="sp-client-secret")
  tenant_id = dbutils.secrets.get(scope="my-scope", key="sp-tenant-id")
  ```
- Or use Managed Identity + Unity Catalog/credential passthrough for ADLS Gen2 access.
- Rotate credentials regularly and use RBAC roles for least privilege.

Before publishing this project, replace the literal credentials in `silver_layer.py` with secrets or managed identity usage.

---

## How to reproduce (high-level)
1. Create required Azure resources:
   - Storage account (ADLS Gen2): containers `bronze`, `silver`, `gold` (or use folders)
   - Azure Databricks workspace
   - Azure Data Factory (ADF)
   - Azure Synapse workspace (optional)

2. Configure access:
   - Register an app in Azure AD or use a managed identity.
   - Grant access to the storage account (ACLs / role assignments).

3. ADF pipeline:
   - Create a Lookup activity to list files (or metadata).
   - Use ForEach to iterate over files.
   - Use Copy activity to copy files to Bronze (ADLS Gen2).

4. Databricks:
   - Create a cluster and workspace resources.
   - Store secrets in Databricks Secret Scope (backed by Key Vault).
   - Run `silver_layer.py` notebook to load raw CSVs from Bronze, transform, and write Parquet/Delta to Silver.

5. Synapse:
   - Create schema (e.g., `CREATE SCHEMA gold;`).
   - Create external tables / serverless SQL views over parquet or connect to Delta Lake.

---

## Notebook notes (summary of `silver_layer.py`)
- Uses PySpark to:
  - Read CSVs from abfss://bronze@navstoragedatalake.dfs.core.windows.net/...
  - Calendar: add Month and Year columns using `month()` and `year()`.
  - Customers: create `fullName` by concatenating prefix, FirstName, LastName.
  - Product Subcategories: written to silver as-is.
  - Products: normalize `ProductSKU` (take part before '-') and `ProductName` (first token).
  - Returns, Territories: written to silver as-is.
  - Sales: union 2015/2016/2017, convert `StockDate` to timestamp, replace 'S' with 'T' in OrderNumber, create `multiply` column.
  - Writes output in Parquet to silver container.

Important: Remove inline OAuth settings from the notebook and use secure retrieval of secrets.

---

## Suggested repository layout
- README.md (this file)
- notebooks/
  - silver_layer.py
- assets/ or docs/
  - image_1_azure_resources.png
  - image_2_adf_lookup_foreach.png
  - image_3_adf_pipeline.png
  - image_4_synapse_create_schema.png
- scripts/
  - deploy_adf_arm_template.json (optional)
  - create_synapse_schema.sql
- .gitignore

---

## How to add this as a GitHub Project / Profile README

Option A — Add as a repository and link it on your profile:
1. Create a new repo (e.g. `nav-data-pipeline`) and push the files:
   ```bash
   git init
   git add README.md notebooks/silver_layer.py assets/*
   git commit -m "Initial commit - Data pipeline documentation and notebook"
   git branch -M main
   git remote add origin git@github.com:Saikrishna22-P/nav-data-pipeline.git
   git push -u origin main
   ```
2. On your GitHub profile, pin the repository:
   - Go to your profile → Repositories → select the repo → click the "Pin" button (or use the "Customize your pins" option on your profile).

Option B — Add it directly to your GitHub profile README:
1. Create a repository with the name exactly matching your GitHub username: `Saikrishna22-P/Saikrishna22-P`.
2. Add this README.md to that repo (it will show as your profile README).
3. Push the file:
   ```bash
   git clone git@github.com:Saikrishna22-P/Saikrishna22-P.git
   cd Saikrishna22-P
   # Copy README.md here
   git add README.md
   git commit -m "Add data pipeline project to profile README"
   git push
   ```

How to include screenshots:
- Put images in `assets/` and reference them in the README:
  ```md
  ![Azure resources (Image 1)](assets/image_1_azure_resources.png)
  ![ADF pipeline (Image 2)](assets/image_2_adf_lookup_foreach.png)
  ![ADF pipeline + datasets (Image 3)](assets/image_3_adf_pipeline.png)
  ![Synapse create schema (Image 4)](assets/image_4_synapse_create_schema.png)
  ```

---

## Useful next steps & recommendations
- Convert Silver layer to Delta Lake (ACID, time travel, schema evolution).
- Add data quality checks (great_expectations, Deequ, or custom validations) after Silver ingestion.
- Automate Databricks job runs with ADF or Databricks Jobs API.
- Create incremental ingestion logic for large files (use watermark columns/modified times).
- Add a diagram (Mermaid or an image) showing the end-to-end flow.

---

## Contact / Maintainer
- Project owner: Saikrishna22-P
- If you want, I can:
  - Prepare a sanitized version of `silver_layer.py` that removes inline credentials and uses databricks secrets/Key Vault.
  - Provide a sample ADF pipeline JSON for the Lookup → ForEach → Copy pattern.
  - Generate a Delta conversion script and Synapse external table creation SQL.

Thank you — tell me which next step you'd like me to do (sanitize notebook, prepare deployment steps, or create a profile-ready repo structure).
