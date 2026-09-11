# Data Provenance

## Dataset

UCI Machine Learning Repository — **Heart Failure Clinical Records**.

- Dataset ID: `519`
- DOI: `10.24432/C5Z89R`
- UCI dataset page: `https://archive.ics.uci.edu/dataset/519/heart`
- Official archive used by the extractor:
  `https://archive.ics.uci.edu/static/public/519/heart%2Bfailure%2Bclinical%2Brecords.zip`
- License shown by UCI: CC BY 4.0

UCI describes 299 heart-failure patient records and lists clustering among the associated tasks.

## Download audit trail

`src/01_extract_uci.py` records:

- retrieval timestamp in UTC;
- exact archive URL;
- SHA-256 checksum;
- archive byte count;
- extracted CSV file name;
- row count;
- column names.

The metadata are stored in:

`data/raw/source_metadata.json`

## No invented data

The repository does not generate synthetic patient records.

The committed source CSV is extracted from the official UCI archive.

## Record IDs

The source dataset does not provide a patient identifier for portfolio use. `patient_record_id` is therefore a generated sequential row identifier used only to join project tables. It is **not** an original clinical identifier.
