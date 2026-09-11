from __future__ import annotations

from pathlib import Path
from urllib.request import Request, urlopen
from datetime import datetime, timezone
import csv
import hashlib
import io
import json
import zipfile

ROOT = Path(__file__).resolve().parents[1]
CONFIG = json.loads((ROOT / "config" / "config.json").read_text(encoding="utf-8"))
RAW = ROOT / "data" / "raw"
RAW.mkdir(parents=True, exist_ok=True)

URL = CONFIG["source_url"]
EXPECTED_ROWS = int(CONFIG["expected_rows"])
EXPECTED_FILE = "heart_failure_clinical_records_dataset.csv"


def main() -> None:
    print("Downloading official UCI Heart Failure Clinical Records archive...")
    req = Request(
        URL,
        headers={
            "User-Agent": "heart-failure-patient-segmentation-portfolio/1.0",
            "Accept": "application/zip,*/*;q=0.8",
        },
    )
    with urlopen(req, timeout=120) as response:
        raw_zip = response.read()

    digest = hashlib.sha256(raw_zip).hexdigest()

    with zipfile.ZipFile(io.BytesIO(raw_zip)) as zf:
        names = zf.namelist()
        candidates = [n for n in names if n.endswith(EXPECTED_FILE)]
        if len(candidates) != 1:
            raise RuntimeError(
                f"Expected exactly one {EXPECTED_FILE} in archive; found {candidates}"
            )
        csv_bytes = zf.read(candidates[0])

    csv_text = csv_bytes.decode("utf-8-sig")
    rows = list(csv.DictReader(io.StringIO(csv_text)))
    if len(rows) != EXPECTED_ROWS:
        raise RuntimeError(f"Expected {EXPECTED_ROWS} rows; found {len(rows)}")

    required = [
        "age", "anaemia", "creatinine_phosphokinase", "diabetes",
        "ejection_fraction", "high_blood_pressure", "platelets",
        "serum_creatinine", "serum_sodium", "sex", "smoking",
        "time", "DEATH_EVENT"
    ]
    missing = [c for c in required if c not in (rows[0].keys() if rows else [])]
    if missing:
        raise RuntimeError(f"Missing expected UCI columns: {missing}")

    out = RAW / EXPECTED_FILE
    out.write_bytes(csv_bytes)

    metadata = {
        "dataset": CONFIG["dataset_name"],
        "uci_dataset_id": CONFIG["uci_dataset_id"],
        "source_url": URL,
        "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
        "archive_sha256": digest,
        "archive_bytes": len(raw_zip),
        "csv_file": EXPECTED_FILE,
        "row_count": len(rows),
        "columns": list(rows[0].keys()),
        "license": "CC BY 4.0",
        "doi": "10.24432/C5Z89R",
        "synthetic_data": False,
    }
    (RAW / "source_metadata.json").write_text(
        json.dumps(metadata, indent=2) + "\n",
        encoding="utf-8",
    )

    print(f"Rows extracted: {len(rows)}")
    print(f"SHA-256: {digest}")
    print(f"Raw CSV: {out}")


if __name__ == "__main__":
    main()
