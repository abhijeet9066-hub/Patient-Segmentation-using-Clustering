# Limitations

- The dataset contains only 299 heart-failure patient records.
- The cohort is historical and may not represent another hospital, country or era.
- KMeans assumes Euclidean geometry and tends to favor roughly spherical clusters.
- Binary and continuous features are combined after standardization; other distance functions or mixed-data clustering methods may produce different phenotypes.
- The chosen number of clusters is based on internal silhouette score, not a clinical gold standard.
- PCA is used for visualization and does not preserve all information in two dimensions.
- Cluster labels are descriptive and not diagnoses.
- `DEATH_EVENT` is not used to form clusters.
- Post-hoc death-event prevalence does not validate prospective mortality risk.
- The analysis does not establish causality or treatment effects.
- No cluster should be used for individual medical decisions without external clinical validation.
