# Versioned Reference Data Validation Pipeline

## 1. Project Overview

The Versioned Reference Data Validation Pipeline validates incoming records against versioned reference data using product codes, reference versions, effective dates, and deprecation status.

The pipeline identifies invalid records, assigns clear validation outcomes, generates rejection reports, and maintains run-level information to support data quality, traceability, and reliable processing.

## 2. Key Features

- Version-aware reference data validation
- Effective-date validation
- Detection of unknown product codes
- Detection of expired and deprecated reference codes
- Invalid and missing date handling
- Missing required field validation
- Duplicate record ID detection
- Duplicate reference key detection
- Automated tests using pytest
- Reproducible synthetic data experiments
- CSV-based input and output
- Validation summaries and reconciliation checks
- Optimized reference lookup for larger datasets
- Run logging and safe output file publishing

## 3. Validation Outcomes

| Status | Meaning |
|---|---|
| VALID | Record matches a valid reference entry |
| UNKNOWN_CODE | Product code and reference version were not found |
| NOT_YET_VALID | Event date precedes the reference start date |
| EXPIRED_CODE | Event date is after the reference end date |
| DEPRECATED_CODE | Reference entry is marked deprecated |
| INVALID_DATE | Event date cannot be parsed |
| MISSING_PRODUCT_CODE | Required product code is missing |
| MISSING_EVENT_DATE | Required event date is missing |
| DUPLICATE_RECORD_ID | Record ID has already appeared |
| DUPLICATE_REFERENCE_KEY | Reference data contains a duplicate key |

## 4. Project Structure

| File | Description |
|---|---|
| `pipeline.py` | Main validation and processing pipeline |
| `validator.py` | Reusable validation function |
| `test_validator.py` | Unit tests for validation rules |
| `test_pipeline.py` | Pipeline integration and output tests |
| `pipeline_setup.ipynb` | Development, data preparation, and experiments |
| `versioned_reference.csv` | Versioned reference data |
| `data_dictionary.csv` | Field definitions |
| `requirements.txt` | Python dependencies |
| `README.md` | Project documentation |

The project also generates validation outputs and synthetic benchmark files during execution.

## 5. Requirements

- Python 3.9 or later
- pandas
- numpy
- pytest

Install dependencies:

```bash
pip install -r requirements.txt
```

## 6. Running the Pipeline

Run the following command from the project directory:

```bash
python pipeline.py --input test_input.csv --reference versioned_reference.csv --output run_outputs
```

Replace the input and reference filenames with your own CSV files when needed.

The input data should contain the required record fields, including:

- `record_id`
- `product_code`
- `reference_version`
- `event_date`

The reference data should contain:

- `product_code`
- `reference_version`
- `valid_from`
- `valid_to`
- `status`

## 7. Generated Outputs

The pipeline generates the following files in the selected output directory:

| Output | Description |
|---|---|
| `all_results.csv` | Complete validation results |
| `valid_records.csv` | Records that passed validation |
| `rejected_records.csv` | Records that failed validation |
| `rejection_summary.csv` | Summary of rejection reasons |
| `run_log.json` | Run-level metadata and processing information |

The pipeline also checks that accepted and rejected records reconcile with the total number of processed records.

## 8. Running Automated Tests

Run all tests from the project directory:

```bash
python -m pytest -v
```

The test suite covers validation rules, pipeline processing, output generation, rejection reasons, repeatable run IDs, and run logging.

## 9. Performance Experiment

A synthetic dataset containing 100,000 records was used to evaluate pipeline performance.

Recorded experiment:

- Records processed: 100,000
- Execution time: approximately 61.54 seconds
- Processing throughput: approximately 1,625 records per second
- Accepted records: 25,000
- Rejected records: 75,000
- Reconciliation: Passed

These are results from the recorded synthetic experiment. Actual performance may vary depending on hardware and dataset characteristics.

## 10. Data Reproducibility

The development notebook includes synthetic dataset generation using a fixed random seed. This supports repeatable experiments and consistent validation testing.

## 11. Current Limitations and Future Improvements

- Current implementation uses CSV files rather than a database.
- The benchmark uses synthetic data rather than production data.
- Output files are published safely one file at a time; the complete output set is not a single atomic transaction.
- Concurrent execution and output-directory locking are not currently implemented.
- Additional integration tests and production-scale testing can be added.

## 12. Project Status

The core validation pipeline has been implemented and tested. Unit tests, pipeline tests, end-to-end validation, and a 100,000-record synthetic performance experiment have been completed.

The project is designed to demonstrate reliable, traceable, and version-aware reference data validation.
