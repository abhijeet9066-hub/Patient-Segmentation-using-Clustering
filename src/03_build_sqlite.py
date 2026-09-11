from pathlib import Path
import sqlite3
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"
DB = PROCESSED / "patient_segmentation.sqlite"

TABLES = {
    "patient_segments": "patient_segments.csv",
    "segment_summary": "segment_summary.csv",
    "cluster_feature_profiles": "cluster_feature_profiles.csv",
    "model_selection": "model_selection.csv",
}


def main() -> None:
    for filename in TABLES.values():
        path = PROCESSED / filename
        if not path.exists():
            raise FileNotFoundError(f"Missing {path}. Run src/02_cluster_patients.py first.")

    conn = sqlite3.connect(DB)
    try:
        counts = {}
        for table, filename in TABLES.items():
            df = pd.read_csv(PROCESSED / filename)
            df.to_sql(table, conn, if_exists="replace", index=False)
            counts[table] = len(df)

        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_patient_segment ON patient_segments(segment_id)"
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_profile_segment ON cluster_feature_profiles(segment_id)"
        )
        conn.commit()
    finally:
        conn.close()

    print(f"SQLite database: {DB}")
    for table, count in counts.items():
        print(f"{table} rows: {count}")


if __name__ == "__main__":
    main()
