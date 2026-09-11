# Power BI Dashboard Blueprint

## Page 1 — Cohort & Segmentation Overview

Cards:
- 299 source records
- selected cluster count
- selected silhouette score
- observed death-event prevalence

Charts:
- patient count by segment
- cohort percentage by segment

Mandatory note:

> Segments are exploratory phenotypes. They are not validated diagnoses or individual risk scores.

## Page 2 — Segment Clinical Profiles

Compare by segment:

- age
- ejection fraction
- serum creatinine
- serum sodium
- creatinine phosphokinase
- platelets

Use both original-unit summary and standardized centroid heatmap.

## Page 3 — PCA Segment Map

Scatter:
- X: pca_1
- Y: pca_2
- legend: segment_label

PCA coordinates are for visualization only; clustering uses the full standardized 11-feature space.

## Page 4 — Comorbidity Mix

Segment-level percentages:

- diabetes
- high blood pressure
- anaemia
- smoking

## Page 5 — Post-hoc Outcome Comparison

Show:

- observed death events
- observed death-event percentage
- mean follow-up days

Mandatory note:

> DEATH_EVENT and follow-up time were excluded from clustering. These charts are retrospective descriptive comparisons, not prospective mortality predictions.

## Page 6 — Model Selection & Methodology

Show:

- candidate k
- silhouette score
- inertia
- selected solution
- source DOI and license
- clustering feature list
- leakage exclusions
- limitations
