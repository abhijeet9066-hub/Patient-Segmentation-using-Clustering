# Methodology

## 1. Schema validation

The pipeline requires the 13 UCI columns:

- age
- anaemia
- creatinine_phosphokinase
- diabetes
- ejection_fraction
- high_blood_pressure
- platelets
- serum_creatinine
- serum_sodium
- sex
- smoking
- time
- DEATH_EVENT

The extracted dataset is expected to contain 299 rows.

## 2. Leakage-aware feature set

The unsupervised feature matrix excludes:

- `DEATH_EVENT`, because it is the follow-up outcome;
- `time`, because it is follow-up duration and can be entangled with the observed outcome process.

Clustering therefore uses 11 baseline clinical/demographic features.

## 3. Standardization

All clustering features are standardized with `StandardScaler`.

This prevents high-magnitude variables such as platelets or creatinine phosphokinase from dominating Euclidean distance purely because of their units.

## 4. Candidate KMeans models

Candidate cluster counts:

`k = 2, 3, 4, 5, 6`

For each candidate:

- `random_state = 42`
- `n_init = 30`
- inertia is recorded;
- silhouette score is recorded.

The selected model is the candidate with the highest silhouette score. Ties are resolved toward the smaller `k`.

## 5. PCA

A two-component PCA is fit on the standardized feature matrix.

PCA is used only to provide dashboard visualization coordinates and stable segment ordering.

It does not replace the full 11-feature KMeans model.

## 6. Stable segment labels

Raw KMeans cluster labels are arbitrary.

To make outputs deterministic and easier to compare, raw clusters are ordered by their mean PCA component 1 value and then relabeled:

`Segment 1`, `Segment 2`, ...

This ordering does not use `DEATH_EVENT`.

## 7. Post-hoc outcome description

After segment assignment, the project calculates observed `DEATH_EVENT` prevalence within each segment.

This is a descriptive retrospective comparison only.

It does not convert the clustering model into a validated mortality-risk model.

## 8. Interpretation boundaries

The clusters are exploratory phenotypes in a small historical heart-failure cohort.

External validation would be required before using the segments for any clinical workflow.
