
import json
import pandas as pd

from pipeline import run_pipeline


def create_test_files(tmp_path):
    """Create small input and reference CSV files."""

    input_data = pd.DataFrame({
        "record_id": [1001, 1002, 1003, 1004],
        "product_code": ["P101", "P102", "P999", "P103"],
        "event_date": [
            "2026-05-15",
            "2026-08-15",
            "2026-08-15",
            "2026-08-15"
        ],
        "reference_version": [1, 2, 2, 1]
    })

    reference_data = pd.DataFrame({
        "product_code": [
            "P101", "P102", "P103", "P101", "P102"
        ],
        "reference_version": [1, 1, 1, 2, 2],
        "status": [
            "active", "active", "deprecated", "active", "deprecated"
        ],
        "valid_from": [
            "2026-01-01",
            "2026-01-01",
            "2026-01-01",
            "2026-07-01",
            "2026-07-01"
        ],
        "valid_to": [
            None, None, "2026-06-30", None, None
        ]
    })

    input_file = tmp_path / "input.csv"
    reference_file = tmp_path / "reference.csv"

    input_data.to_csv(input_file, index=False)
    reference_data.to_csv(reference_file, index=False)

    return input_file, reference_file


def test_pipeline_counts_and_reconciliation(tmp_path):
    input_file, reference_file = create_test_files(tmp_path)

    result = run_pipeline(
        input_file,
        reference_file,
        tmp_path / "output"
    )

    assert result["input_count"] == 4
    assert result["accepted_count"] == 1
    assert result["rejected_count"] == 3
    assert result["reconciliation_passed"] is True


def test_pipeline_creates_output_files(tmp_path):
    input_file, reference_file = create_test_files(tmp_path)

    result = run_pipeline(
        input_file,
        reference_file,
        tmp_path / "output"
    )

    output_folder = (
        tmp_path / "output" / result["run_id"]
    )

    expected_files = [
        "all_results.csv",
        "valid_records.csv",
        "rejected_records.csv",
        "rejection_summary.csv",
        "run_log.json"
    ]

    for filename in expected_files:
        assert (output_folder / filename).exists()


def test_pipeline_rejection_reasons(tmp_path):
    input_file, reference_file = create_test_files(tmp_path)

    result = run_pipeline(
        input_file,
        reference_file,
        tmp_path / "output"
    )

    output_folder = (
        tmp_path / "output" / result["run_id"]
    )

    rejected = pd.read_csv(
        output_folder / "rejected_records.csv"
    )

    reasons = set(rejected["rejection_reason"])

    assert reasons == {
        "DEPRECATED_CODE",
        "UNKNOWN_CODE",
        "EXPIRED_CODE"
    }


def test_pipeline_repeatable_run_id(tmp_path):
    input_file, reference_file = create_test_files(tmp_path)

    output_dir = tmp_path / "output"

    first = run_pipeline(
        input_file,
        reference_file,
        output_dir
    )

    second = run_pipeline(
        input_file,
        reference_file,
        output_dir
    )

    assert first["run_id"] == second["run_id"]


def test_pipeline_run_log(tmp_path):
    input_file, reference_file = create_test_files(tmp_path)

    result = run_pipeline(
        input_file,
        reference_file,
        tmp_path / "output"
    )

    log_file = (
        tmp_path / "output" / result["run_id"] / "run_log.json"
    )

    with open(log_file, encoding="utf-8") as file:
        log = json.load(file)

    assert log["run_status"] == "SUCCESS"
    assert log["input_count"] == 4
    assert log["accepted_count"] == 1
    assert log["rejected_count"] == 3
    assert log["reconciliation_passed"] is True
