-- Heart Failure Patient Phenotype Segmentation

-- 1. Segment size and descriptive observed outcome prevalence
SELECT
    segment_label,
    patient_count,
    ROUND(cohort_pct, 1) AS cohort_pct,
    observed_death_events,
    ROUND(observed_death_event_pct, 1) AS observed_death_event_pct
FROM segment_summary
ORDER BY segment_id;

-- 2. Core clinical profile
SELECT
    segment_label,
    ROUND(mean_age, 1) AS mean_age,
    ROUND(mean_ejection_fraction, 1) AS mean_ejection_fraction,
    ROUND(mean_serum_creatinine, 2) AS mean_serum_creatinine,
    ROUND(mean_serum_sodium, 1) AS mean_serum_sodium
FROM segment_summary
ORDER BY segment_id;

-- 3. Comorbidity / behavior prevalence
SELECT
    segment_label,
    ROUND(diabetes_pct, 1) AS diabetes_pct,
    ROUND(hypertension_pct, 1) AS hypertension_pct,
    ROUND(anaemia_pct, 1) AS anaemia_pct,
    ROUND(smoking_pct, 1) AS smoking_pct
FROM segment_summary
ORDER BY segment_id;

-- 4. Standardized feature centroid profile
SELECT
    segment_label,
    feature,
    ROUND(centroid_z, 3) AS centroid_z,
    ROUND(mean_raw, 3) AS mean_raw,
    ROUND(median_raw, 3) AS median_raw
FROM cluster_feature_profiles
ORDER BY segment_id, feature;

-- 5. Candidate cluster solutions
SELECT
    k,
    ROUND(inertia, 2) AS inertia,
    ROUND(silhouette_score, 4) AS silhouette_score,
    selected
FROM model_selection
ORDER BY k;
