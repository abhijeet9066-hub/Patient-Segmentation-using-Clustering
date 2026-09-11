from pathlib import Path
import hashlib
import json
import re
import sqlite3
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CONFIG = json.loads((ROOT / "config" / "config.json").read_text(encoding="utf-8"))
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"

required = [
    ROOT / "README.md",
    ROOT / "config" / "config.json",
    RAW / "heart_failure_clinical_records_dataset.csv",
    RAW / "source_metadata.json",
    ROOT / "data" / "source_manifest.csv",
    PROCESSED / "patient_segments.csv",
    PROCESSED / "segment_summary.csv",
    PROCESSED / "cluster_feature_profiles.csv",
    PROCESSED / "model_selection.csv",
    PROCESSED / "model_metadata.json",
    PROCESSED / "patient_segmentation.sqlite",
    ROOT / "data" / "powerbi" / "patient_segments.csv",
    ROOT / "docs" / "data_provenance.md",
    ROOT / "docs" / "methodology.md",
    ROOT / "docs" / "data_dictionary.md",
    ROOT / "docs" / "limitations.md",
    ROOT / "sql" / "analysis_queries.sql",
    ROOT / "powerbi" / "dashboard_blueprint.md",
    ROOT / "powerbi" / "measures.dax",
    ROOT / ".github" / "workflows" / "ci.yml",
]
missing = [str(p.relative_to(ROOT)) for p in required if not p.exists()]
if missing:
    raise SystemExit("Missing required files: " + ", ".join(missing))

for legacy in [
    ROOT / "config" / "config.yaml",
    ROOT / "src" / "01_ingest.py",
    ROOT / "src" / "02_clean.py",
    ROOT / "src" / "03_train_model.py",
]:
    if legacy.exists():
        raise SystemExit(f"Legacy placeholder file still exists: {legacy.relative_to(ROOT)}")

meta = json.loads((RAW / "source_metadata.json").read_text(encoding="utf-8"))
if meta.get("row_count") != 299:
    raise SystemExit(f"Unexpected source row count: {meta.get('row_count')}")
if meta.get("synthetic_data") is not False:
    raise SystemExit("Source metadata must explicitly identify the dataset as non-synthetic.")
if not re.fullmatch(r"[0-9a-f]{64}", meta.get("archive_sha256", "")):
    raise SystemExit("Invalid/missing source archive SHA-256.")

patients = pd.read_csv(PROCESSED / "patient_segments.csv")
summary = pd.read_csv(PROCESSED / "segment_summary.csv")
profiles = pd.read_csv(PROCESSED / "cluster_feature_profiles.csv")
selection = pd.read_csv(PROCESSED / "model_selection.csv")
model_meta = json.loads((PROCESSED / "model_metadata.json").read_text(encoding="utf-8"))

if len(patients) != 299:
    raise SystemExit(f"Expected 299 segmented records; found {len(patients)}.")
if patients["patient_record_id"].nunique() != 299:
    raise SystemExit("patient_record_id must be unique.")
if patients["segment_id"].isna().any():
    raise SystemExit("Missing segment assignments.")

selected_rows = selection[selection["selected"] == 1]
if len(selected_rows) != 1:
    raise SystemExit("Exactly one candidate k must be selected.")
selected_k = int(selected_rows.iloc[0]["k"])
if selected_k != int(model_meta["selected_k"]):
    raise SystemExit("Selected k mismatch between diagnostics and metadata.")
if len(summary) != selected_k:
    raise SystemExit("Segment summary row count does not match selected k.")
if len(profiles) != selected_k * len(CONFIG["cluster_features"]):
    raise SystemExit("Feature profile row count does not match k × clustering features.")

if set(CONFIG["excluded_from_clustering"]) != {"time", "DEATH_EVENT"}:
    raise SystemExit("Expected time and DEATH_EVENT to be excluded from clustering.")
if "DEATH_EVENT" in model_meta["features"] or "time" in model_meta["features"]:
    raise SystemExit("Outcome/follow-up leakage detected in clustering feature list.")

if abs(summary["patient_count"].sum() - 299) > 0:
    raise SystemExit("Segment counts do not sum to source cohort.")
if ((summary["observed_death_event_pct"] < 0) | (summary["observed_death_event_pct"] > 100)).any():
    raise SystemExit("Observed death-event prevalence outside [0,100].")

conn = sqlite3.connect(PROCESSED / "patient_segmentation.sqlite")
try:
    db_patients = conn.execute("SELECT COUNT(*) FROM patient_segments").fetchone()[0]
    db_summary = conn.execute("SELECT COUNT(*) FROM segment_summary").fetchone()[0]
    db_profiles = conn.execute("SELECT COUNT(*) FROM cluster_feature_profiles").fetchone()[0]
finally:
    conn.close()

if (db_patients, db_summary, db_profiles) != (len(patients), len(summary), len(profiles)):
    raise SystemExit("SQLite row counts do not match processed outputs.")

readme = (ROOT / "README.md").read_text(encoding="utf-8")
normalized = readme.replace("**", "").replace("__", "").replace("`", "").lower()
required_phrases = [
    "exploratory phenotypes",
    "death_event is excluded from clustering",
    "post-hoc descriptive",
    "not validated diagnoses",
]
for phrase in required_phrases:
    if phrase not in normalized:
        raise SystemExit(f"Required interpretation statement missing: {phrase}")

print("PASS: official UCI source metadata and SHA-256 provenance captured")
print(f"PASS: segmented source records = {len(patients)}")
print(f"PASS: selected cluster count = {selected_k}")
print(f"PASS: model-selection candidates = {len(selection)}")
print(f"PASS: segment feature-profile rows = {len(profiles)}")
print("PASS: time and DEATH_EVENT excluded from clustering features")
print("PASS: SQLite warehouse matches processed outputs")
print("PASS: clinical interpretation and post-hoc outcome limitations documented")
