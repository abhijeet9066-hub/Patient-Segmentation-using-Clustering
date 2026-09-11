# Heart Failure Patient Phenotype Segmentation

A reproducible **UCI + Python + scikit-learn + SQL + Power BI** portfolio project that applies unsupervised learning to a real heart-failure clinical dataset.

> **Clinical interpretation warning:** The clusters are exploratory phenotypes, not validated diagnoses, treatment recommendations, or individual risk scores. `DEATH_EVENT` is excluded from clustering and is used only for post-hoc descriptive comparison between discovered segments.

## Why This Repository Was Rebuilt

The previous repository was a generic ML skeleton that mentioned “UCI diabetes/heart/health indicators” without choosing a real dataset or implementing a defensible clustering workflow.

This rebuild uses one clearly documented public dataset and a reproducible unsupervised-learning pipeline.

## Dataset

**UCI Heart Failure Clinical Records**, dataset ID 519.

UCI describes the dataset as 299 heart-failure patient records with 12 clinical features plus the follow-up death-event target. The UCI page lists clustering as one of the associated tasks.

Source DOI:

```text
10.24432/C5Z89R
```

License:

```text
CC BY 4.0
```

The repair script downloads the official UCI archive and records a SHA-256 hash of the downloaded bytes in:

```text
data/raw/source_metadata.json
```

## Clustering Scope

The clustering features are:

- age
- anaemia
- creatinine phosphokinase
- diabetes
- ejection fraction
- high blood pressure
- platelets
- serum creatinine
- serum sodium
- sex
- smoking

Two variables are deliberately **excluded** from clustering:

- `time` — follow-up duration;
- `DEATH_EVENT` — observed follow-up outcome.

This avoids using the outcome or follow-up duration to manufacture the patient segments.

## Modeling Workflow

1. validate schema and row count;
2. standardize the 11 clustering features;
3. fit KMeans for `k = 2..6`;
4. compare models with silhouette score and inertia;
5. choose the highest-silhouette solution, breaking ties toward smaller `k`;
6. create a 2D PCA projection for visualization only;
7. assign stable segment IDs by ordering cluster mean PC1 scores;
8. profile each segment using original clinical units;
9. compare the observed death-event prevalence **after clustering**.

The random seed is fixed at `42` and KMeans uses multiple initializations for reproducibility.

## Why This Is Not a Mortality Prediction Model

The model does not train on `DEATH_EVENT`.

Observed death-event prevalence is calculated only after clusters have been formed. It is useful for describing whether discovered clinical phenotypes happen to differ in the historical dataset, but it does not validate the clusters as prospective risk groups.

The project therefore does **not** claim:

- causal relationships;
- prospective mortality prediction;
- treatment effectiveness;
- clinical decision support;
- generalization to another hospital or population.

## Outputs

### `patient_segments.csv`

One row per UCI record with:

- source row ID;
- clinical features;
- follow-up variables;
- chosen segment ID;
- PCA coordinates.

### `segment_summary.csv`

One row per discovered segment with:

- patient count;
- percentage of cohort;
- mean age;
- mean ejection fraction;
- mean serum creatinine;
- mean serum sodium;
- diabetes prevalence;
- hypertension prevalence;
- anaemia prevalence;
- smoking prevalence;
- observed death events;
- observed death-event prevalence.

### `cluster_feature_profiles.csv`

Long-form segment profile table containing:

- raw feature mean;
- raw feature median;
- standardized centroid value.

### `model_selection.csv`

For each candidate `k`:

- inertia;
- silhouette score;
- whether it was selected.

## Pipeline

```text
UCI Heart Failure Clinical Records
        ↓
src/01_extract_uci.py
        ↓
data/raw/
        ↓
src/02_cluster_patients.py
        ↓
data/processed/
        ↓
src/03_build_sqlite.py
        ↓
data/processed/patient_segmentation.sqlite
        ↓
src/04_export_powerbi.py
        ↓
data/powerbi/
```

## Run

```bash
python -m pip install -r requirements.txt
python src/01_extract_uci.py
python src/02_cluster_patients.py
python src/03_build_sqlite.py
python src/04_export_powerbi.py
python src/validate_repo.py
```

GitHub Actions does not call the live UCI endpoint. CI rebuilds clustering from the committed UCI CSV and validates the analytical artifacts.

## SQL

The SQLite warehouse supports analysis such as:

- segment size and cohort share;
- post-hoc observed death-event prevalence;
- clinical profile comparison;
- binary comorbidity prevalence;
- segment-level feature centroids;
- model-selection diagnostics.

## Power BI

Recommended pages:

1. Cohort & Segmentation Overview
2. Segment Clinical Profiles
3. PCA Segment Map
4. Comorbidity Mix
5. Post-hoc Outcome Comparison
6. Model Selection & Methodology

## Interview Summary

> I rebuilt a placeholder patient-clustering repository into a reproducible unsupervised-learning project using the UCI Heart Failure Clinical Records dataset. I standardize 11 clinical features, exclude follow-up duration and death outcome from clustering, compare KMeans solutions from two to six clusters using silhouette score and inertia, generate PCA coordinates for visualization, profile clusters in original clinical units, and use the death-event field only as a post-hoc descriptive outcome. I also load the results into SQLite and export Power BI-ready tables.

## Skills Demonstrated

- unsupervised machine learning
- KMeans clustering
- silhouette analysis
- PCA visualization
- feature standardization
- healthcare data interpretation
- outcome-leakage prevention
- pandas / scikit-learn
- SQLite / SQL
- Power BI modeling
- source provenance
- GitHub Actions CI

## Author

**Abhijeet Vasantrao Patil**  
GitHub: https://github.com/abhijeet9066-hub
