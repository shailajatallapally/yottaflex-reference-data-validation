
import pandas as pd


def validate_record(record, reference_data):
    """Validate a record against a dictionary or DataFrame."""

    product_code = record["product_code"]
    reference_version = record["reference_version"]

    event_date = record["event_date"]

    if not isinstance(event_date, pd.Timestamp):
        event_date = pd.to_datetime(
            event_date,
            errors="coerce"
        )

    if pd.isna(event_date):
        return "INVALID_DATE"

    key = (product_code, reference_version)

    # Support the optimized dictionary lookup.
    if isinstance(reference_data, dict):

        reference = reference_data.get(key)

        if reference is None:
            return "UNKNOWN_CODE"

        if isinstance(reference, list):
            return "DUPLICATE_REFERENCE_KEY"

    # Also support DataFrames used by automated tests.
    else:

        matches = reference_data[
            (reference_data["product_code"] == product_code)
            & (
                reference_data["reference_version"]
                == reference_version
            )
        ]

        if matches.empty:
            return "UNKNOWN_CODE"

        if len(matches) > 1:
            return "DUPLICATE_REFERENCE_KEY"

        reference = matches.iloc[0]

    if event_date < reference["valid_from"]:
        return "NOT_YET_VALID"

    if (
        pd.notna(reference["valid_to"])
        and event_date > reference["valid_to"]
    ):
        return "EXPIRED_CODE"

    if reference["status"] == "deprecated":
        return "DEPRECATED_CODE"

    return "VALID"
