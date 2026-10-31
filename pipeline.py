
import argparse
import hashlib
import json
import os
import time
from pathlib import Path
from datetime import datetime, timezone

import pandas as pd
from validator import validate_record


REQUIRED_INPUT_COLUMNS = [
    "record_id",
    "product_code",
    "event_date",
    "reference_version"
]

REQUIRED_REFERENCE_COLUMNS = [
    "product_code",
    "reference_version",
    "status",
    "valid_from",
    "valid_to"
]


def generate_run_id(input_file, reference_file):
    """Generate a repeatable ID from both input files."""

    hasher = hashlib.sha256()

    for file_path in [input_file, reference_file]:
        with open(file_path, "rb") as file:
            for chunk in iter(lambda: file.read(1024 * 1024), b""):
                hasher.update(chunk)

    return hasher.hexdigest()[:16]


def safe_write_csv(dataframe, output_path):
    """Write a CSV through a temporary file."""

    output_path = Path(output_path)

    temporary_path = output_path.with_name(
        output_path.name + ".tmp"
    )

    try:
        dataframe.to_csv(temporary_path, index=False)
        os.replace(temporary_path, output_path)

    finally:
        if temporary_path.exists():
            temporary_path.unlink()


def safe_write_json(data, output_path):
    """Write JSON through a temporary file."""

    output_path = Path(output_path)

    temporary_path = output_path.with_name(
        output_path.name + ".tmp"
    )

    try:
        with open(
            temporary_path,
            "w",
            encoding="utf-8"
        ) as file:
            json.dump(data, file, indent=4)

        os.replace(temporary_path, output_path)

    finally:
        if temporary_path.exists():
            temporary_path.unlink()


def load_data(input_file, reference_file):
    """Load data and validate the required schemas."""

    incoming = pd.read_csv(input_file)
    reference = pd.read_csv(reference_file)

    missing_input = (
        set(REQUIRED_INPUT_COLUMNS) - set(incoming.columns)
    )

    missing_reference = (
        set(REQUIRED_REFERENCE_COLUMNS) - set(reference.columns)
    )

    if missing_input:
        raise ValueError(
            f"Missing input columns: {sorted(missing_input)}"
        )

    if missing_reference:
        raise ValueError(
            f"Missing reference columns: {sorted(missing_reference)}"
        )

    reference["valid_from"] = pd.to_datetime(
        reference["valid_from"],
        errors="coerce"
    )

    reference["valid_to"] = pd.to_datetime(
        reference["valid_to"],
        errors="coerce"
    )

    if reference["valid_from"].isna().any():
        raise ValueError(
            "Reference data contains invalid valid_from dates."
        )

    if reference["product_code"].isna().any():
        raise ValueError(
            "Reference data contains missing product codes."
        )

    if reference["reference_version"].isna().any():
        raise ValueError(
            "Reference data contains missing versions."
        )

    if reference["status"].isna().any():
        raise ValueError(
            "Reference data contains missing statuses."
        )

    return incoming, reference


def build_reference_lookup(reference):
    """Build a dictionary for fast reference lookups."""

    lookup = {}

    for row in reference.to_dict(orient="records"):

        key = (
            row["product_code"],
            row["reference_version"]
        )

        if key not in lookup:
            lookup[key] = row

        else:
            if not isinstance(lookup[key], list):
                lookup[key] = [lookup[key]]

            lookup[key].append(row)

    return lookup


def process_records(incoming, reference):
    """Validate incoming records and separate accepted/rejected rows."""

    reference_lookup = build_reference_lookup(reference)

    incoming = incoming.copy()

    # Detect missing dates before conversion.
    missing_dates = incoming["event_date"].isna()

    # Parse dates in one vectorized operation.
    incoming["event_date"] = pd.to_datetime(
        incoming["event_date"],
        errors="coerce"
    )

    results = []
    seen_ids = set()

    records = incoming.to_dict(orient="records")

    for position, record in enumerate(records):

        record_data = record.copy()
        record_data["source_row"] = position + 2

        reason = None

        # Check required fields.
        for column in [
            "record_id",
            "product_code",
            "reference_version"
        ]:
            if pd.isna(record_data[column]):
                reason = f"MISSING_{column.upper()}"
                break

        # Check missing and invalid dates.
        if reason is None:

            if missing_dates.iloc[position]:
                reason = "MISSING_EVENT_DATE"

            elif pd.isna(record_data["event_date"]):
                reason = "INVALID_DATE"

        # Check duplicate record IDs.
        if reason is None:

            record_id = record_data["record_id"]

            if record_id in seen_ids:
                reason = "DUPLICATE_RECORD_ID"

            else:
                seen_ids.add(record_id)

        # Validate against reference data.
        if reason is None:

            status = validate_record(
                record_data,
                reference_lookup
            )

            if status != "VALID":
                reason = status

        record_data["validation_status"] = (
            "VALID" if reason is None else "REJECTED"
        )

        record_data["rejection_reason"] = reason

        results.append(record_data)

    # Preserve output columns even for empty input.
    result_columns = list(incoming.columns) + [
        "source_row",
        "validation_status",
        "rejection_reason"
    ]

    result_df = pd.DataFrame(
        results,
        columns=result_columns
    )

    valid_records = result_df[
        result_df["validation_status"] == "VALID"
    ].copy()

    rejected_records = result_df[
        result_df["validation_status"] == "REJECTED"
    ].copy()

    return result_df, valid_records, rejected_records


def run_pipeline(input_file, reference_file, output_dir):
    """Execute the complete validation pipeline."""

    start_time = time.perf_counter()

    started_at = datetime.now(timezone.utc).isoformat()

    input_file = Path(input_file)
    reference_file = Path(reference_file)
    output_dir = Path(output_dir)

    if not input_file.exists():
        raise FileNotFoundError(
            f"Input file not found: {input_file}"
        )

    if not reference_file.exists():
        raise FileNotFoundError(
            f"Reference file not found: {reference_file}"
        )

    run_id = generate_run_id(
        input_file,
        reference_file
    )

    run_folder = output_dir / run_id
    run_folder.mkdir(parents=True, exist_ok=True)

    incoming, reference = load_data(
        input_file,
        reference_file
    )

    results, valid, rejected = process_records(
        incoming,
        reference
    )

    input_count = len(incoming)
    accepted_count = len(valid)
    rejected_count = len(rejected)

    # Reconciliation.
    reconciliation_passed = (
        input_count == accepted_count + rejected_count
    )

    if not reconciliation_passed:
        raise RuntimeError("Reconciliation failed!")

    # Build rejection summary.
    rejection_summary = (
        rejected["rejection_reason"]
        .value_counts()
        .rename_axis("rejection_reason")
        .reset_index(name="count")
    )

    elapsed_seconds = round(
        time.perf_counter() - start_time,
        3
    )

    completed_at = datetime.now(timezone.utc).isoformat()

    run_log = {
        "run_id": run_id,
        "started_at_utc": started_at,
        "completed_at_utc": completed_at,
        "input_file": str(input_file),
        "reference_file": str(reference_file),
        "input_count": input_count,
        "accepted_count": accepted_count,
        "rejected_count": rejected_count,
        "reconciliation_passed": reconciliation_passed,
        "elapsed_seconds": elapsed_seconds,
        "run_status": "SUCCESS"
    }

    # Publish each output file safely.
    safe_write_csv(
        results,
        run_folder / "all_results.csv"
    )

    safe_write_csv(
        valid,
        run_folder / "valid_records.csv"
    )

    safe_write_csv(
        rejected,
        run_folder / "rejected_records.csv"
    )

    safe_write_csv(
        rejection_summary,
        run_folder / "rejection_summary.csv"
    )

    # Publish the run log last.
    safe_write_json(
        run_log,
        run_folder / "run_log.json"
    )

    print("PIPELINE COMPLETED")
    print("------------------")
    print("Run ID:", run_id)
    print("Input records:", input_count)
    print("Accepted records:", accepted_count)
    print("Rejected records:", rejected_count)
    print("Reconciliation: PASSED")
    print("Execution time:", elapsed_seconds, "seconds")
    print("Output folder:", run_folder.resolve())

    return run_log


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Versioned Reference Data Validation Pipeline"
    )

    parser.add_argument("--input", required=True)
    parser.add_argument("--reference", required=True)
    parser.add_argument(
        "--output",
        default="pipeline_runs"
    )

    args = parser.parse_args()

    run_pipeline(
        args.input,
        args.reference,
        args.output
    )
