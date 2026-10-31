
import pandas as pd
from validator import validate_record


def create_reference(
    product_code, version, status, valid_from, valid_to=None
):
    reference = pd.DataFrame([
        {
            "product_code": product_code,
            "reference_version": version,
            "status": status,
            "valid_from": valid_from,
            "valid_to": valid_to
        }
    ])

    reference["valid_from"] = pd.to_datetime(reference["valid_from"])
    reference["valid_to"] = pd.to_datetime(reference["valid_to"])

    return reference


def test_valid_code():
    reference = create_reference(
        "P101", 1, "active", "2026-01-01"
    )
    record = {
        "product_code": "P101",
        "event_date": "2026-05-15",
        "reference_version": 1
    }
    assert validate_record(record, reference) == "VALID"


def test_unknown_code():
    reference = create_reference(
        "P101", 1, "active", "2026-01-01"
    )
    record = {
        "product_code": "P999",
        "event_date": "2026-05-15",
        "reference_version": 1
    }
    assert validate_record(record, reference) == "UNKNOWN_CODE"


def test_deprecated_code():
    reference = create_reference(
        "P102", 2, "deprecated", "2026-07-01"
    )
    record = {
        "product_code": "P102",
        "event_date": "2026-08-15",
        "reference_version": 2
    }
    assert validate_record(record, reference) == "DEPRECATED_CODE"


def test_invalid_date():
    reference = create_reference(
        "P101", 1, "active", "2026-01-01"
    )
    record = {
        "product_code": "P101",
        "event_date": "not-a-date",
        "reference_version": 1
    }
    assert validate_record(record, reference) == "INVALID_DATE"


def test_expired_code():
    reference = create_reference(
        "P103", 1, "active", "2026-01-01", "2026-06-30"
    )
    record = {
        "product_code": "P103",
        "event_date": "2026-08-15",
        "reference_version": 1
    }
    assert validate_record(record, reference) == "EXPIRED_CODE"
