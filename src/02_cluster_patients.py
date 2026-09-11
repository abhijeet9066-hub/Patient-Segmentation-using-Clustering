from __future__ import annotations

from pathlib import Path
import json
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parents[1]
CONFIG = json.loads((ROOT / "config" / "config.json").read_text(encoding="utf-8"))
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"
PROCESSED.mkdir(parents=True, exist_ok=True)

SOURCE = RAW / "heart_failure_clinical_records_dataset.csv"
FEATURES = CONFIG["cluster_features"]
CANDIDATE_K = [int(k) for k in CONFIG["candidate_k"]]
RANDOM_STATE = int(CONFIG["random_state"])
EXPECTED_ROWS = int(CONFIG["expected_rows"])


def main() -> None:
    if not SOURCE.exists():
        raise FileNotFoundError("Run src/01_extract_uci.py first.")

    df = pd.read_csv(SOURCE)
    if len(df) != EXPECTED_ROWS:
        raise RuntimeError(f"Expected {EXPECTED_ROWS} source rows; found {len(df)}")

    missing = [c for c in FEATURES + ["time", "DEATH_EVENT"] if c not in df.columns]
    if missing:
        raise RuntimeError(f"Missing required columns: {missing}")

    if df[FEATURES].isna().any().any():
        raise RuntimeError("Unexpected missing values in clustering features.")

    X = df[FEATURES].astype(float)
    scaler = StandardScaler()
    Xz = scaler.fit_transform(X)

    candidates = []
    fitted = {}
    for k in CANDIDATE_K:
        model = KMeans(
            n_clusters=k,
            random_state=RANDOM_STATE,
            n_init=30,
            algorithm="lloyd",
        )
        raw_labels = model.fit_predict(Xz)
        sil = float(silhouette_score(Xz, raw_labels))
        candidates.append(
            {
                "k": k,
                "inertia": float(model.inertia_),
                "silhouette_score": sil,
            }
        )
        fitted[k] = (model, raw_labels)

    selected = sorted(candidates, key=lambda r: (-r["silhouette_score"], r["k"]))[0]
    selected_k = int(selected["k"])
    model, raw_labels = fitted[selected_k]

    pca = PCA(n_components=2, random_state=RANDOM_STATE)
    coords = pca.fit_transform(Xz)

    # Stable, outcome-free relabeling: order raw clusters by their mean PCA-1 score.
    raw_cluster_pc1 = {
        int(c): float(coords[raw_labels == c, 0].mean())
        for c in np.unique(raw_labels)
    }
    ordered_raw = sorted(raw_cluster_pc1, key=lambda c: raw_cluster_pc1[c])
    stable_map = {raw_cluster: idx + 1 for idx, raw_cluster in enumerate(ordered_raw)}
    segment_ids = np.array([stable_map[int(c)] for c in raw_labels], dtype=int)

    out = df.copy()
    out.insert(0, "patient_record_id", np.arange(1, len(out) + 1))
    out["segment_id"] = segment_ids
    out["segment_label"] = out["segment_id"].map(lambda x: f"Segment {x}")
    out["pca_1"] = coords[:, 0]
    out["pca_2"] = coords[:, 1]
    out.to_csv(PROCESSED / "patient_segments.csv", index=False)

    # Candidate model diagnostics
    model_selection = pd.DataFrame(candidates)
    model_selection["selected"] = (model_selection["k"] == selected_k).astype(int)
    model_selection.to_csv(PROCESSED / "model_selection.csv", index=False)

    # Segment summary in original clinical units.
    summaries = []
    for seg in sorted(out["segment_id"].unique()):
        g = out[out["segment_id"] == seg]
        summaries.append(
            {
                "segment_id": int(seg),
                "segment_label": f"Segment {int(seg)}",
                "patient_count": int(len(g)),
                "cohort_pct": float(len(g) / len(out) * 100.0),
                "mean_age": float(g["age"].mean()),
                "mean_ejection_fraction": float(g["ejection_fraction"].mean()),
                "mean_serum_creatinine": float(g["serum_creatinine"].mean()),
                "mean_serum_sodium": float(g["serum_sodium"].mean()),
                "diabetes_pct": float(g["diabetes"].mean() * 100.0),
                "hypertension_pct": float(g["high_blood_pressure"].mean() * 100.0),
                "anaemia_pct": float(g["anaemia"].mean() * 100.0),
                "smoking_pct": float(g["smoking"].mean() * 100.0),
                "observed_death_events": int(g["DEATH_EVENT"].sum()),
                "observed_death_event_pct": float(g["DEATH_EVENT"].mean() * 100.0),
                "mean_followup_days": float(g["time"].mean()),
            }
        )
    pd.DataFrame(summaries).to_csv(PROCESSED / "segment_summary.csv", index=False)

    # Long feature profile table.
    profiles = []
    for raw_cluster in ordered_raw:
        seg = stable_map[raw_cluster]
        mask = raw_labels == raw_cluster
        raw_group = X.loc[mask]
        centroid = model.cluster_centers_[raw_cluster]

        for idx, feature in enumerate(FEATURES):
            profiles.append(
                {
                    "segment_id": seg,
                    "segment_label": f"Segment {seg}",
                    "feature": feature,
                    "mean_raw": float(raw_group[feature].mean()),
                    "median_raw": float(raw_group[feature].median()),
                    "centroid_z": float(centroid[idx]),
                }
            )
    pd.DataFrame(profiles).to_csv(
        PROCESSED / "cluster_feature_profiles.csv",
        index=False,
    )

    model_meta = {
        "algorithm": "KMeans",
        "selected_k": selected_k,
        "selection_rule": "highest silhouette score; ties favor smaller k",
        "random_state": RANDOM_STATE,
        "n_init": 30,
        "features": FEATURES,
        "excluded_from_clustering": CONFIG["excluded_from_clustering"],
        "posthoc_outcome": CONFIG["posthoc_outcome"],
        "pca_explained_variance_ratio": [float(x) for x in pca.explained_variance_ratio_],
        "segment_label_rule": "raw clusters ordered by mean PCA component 1; no outcome used",
    }
    (PROCESSED / "model_metadata.json").write_text(
        json.dumps(model_meta, indent=2) + "\n",
        encoding="utf-8",
    )

    print(f"Source rows: {len(df)}")
    print(f"Selected k: {selected_k}")
    print(f"Selected silhouette score: {selected['silhouette_score']:.4f}")
    print(f"Patient segment rows: {len(out)}")
    print(f"Feature profile rows: {len(profiles)}")


if __name__ == "__main__":
    main()
