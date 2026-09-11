from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"
POWERBI = ROOT / "data" / "powerbi"
POWERBI.mkdir(parents=True, exist_ok=True)

FILES = [
    "patient_segments.csv",
    "segment_summary.csv",
    "cluster_feature_profiles.csv",
    "model_selection.csv",
]


def main() -> None:
    for name in FILES:
        src = PROCESSED / name
        dst = POWERBI / name
        if not src.exists():
            raise FileNotFoundError(f"Missing {src}. Run prior pipeline steps first.")
        shutil.copy2(src, dst)
        print(f"Exported {dst}")


if __name__ == "__main__":
    main()
