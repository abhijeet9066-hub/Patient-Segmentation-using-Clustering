# Data Dictionary

## UCI clinical fields

| Field | Meaning |
|---|---|
| age | Age in years |
| anaemia | Binary anaemia indicator |
| creatinine_phosphokinase | CPK enzyme level |
| diabetes | Binary diabetes indicator |
| ejection_fraction | Percent blood leaving the heart at each contraction |
| high_blood_pressure | Binary hypertension indicator |
| platelets | Platelet count |
| serum_creatinine | Serum creatinine |
| serum_sodium | Serum sodium |
| sex | Binary sex field as supplied by UCI |
| smoking | Binary smoking indicator |
| time | Follow-up period in days |
| DEATH_EVENT | Observed death event during follow-up |

## Generated fields

| Field | Meaning |
|---|---|
| patient_record_id | Sequential project row ID; not an original clinical identifier |
| segment_id | Stable project segment number |
| segment_label | Display label such as `Segment 1` |
| pca_1 | First PCA visualization coordinate |
| pca_2 | Second PCA visualization coordinate |

## `model_selection.csv`

| Field | Meaning |
|---|---|
| k | Candidate number of clusters |
| inertia | KMeans within-cluster sum of squares |
| silhouette_score | Mean silhouette coefficient |
| selected | 1 for the chosen solution |

## `cluster_feature_profiles.csv`

| Field | Meaning |
|---|---|
| segment_id | Stable segment ID |
| feature | Clustering feature |
| mean_raw | Segment feature mean in original units |
| median_raw | Segment feature median in original units |
| centroid_z | KMeans centroid coordinate on standardized scale |
