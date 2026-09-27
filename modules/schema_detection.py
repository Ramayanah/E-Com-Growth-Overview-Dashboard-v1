"""
schema_detection.py — Growth Overview Schema Detection
-------------------------------------------------------
Detects and maps uploaded dataset columns to the standard
Growth Overview schema using aliases from config.py.

Standard schema:
    order_id
    date
    revenue
    customer_id

This module is intentionally independent of Streamlit.
"""

import re
import pandas as pd

import config


def detect_and_map(df):
    """
    Detect and map uploaded DataFrame columns to the standard schema.

    Args:
        df: Raw pandas DataFrame.

    Returns:
        tuple:
            mapped_df: DataFrame with standardized column names.
            mapping_report: dict mapping standard names to source names.
            missing_required: list of required columns not found.
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError("df must be a pandas DataFrame")

    df = df.copy()

    # --------------------------------------------------------
    # Step 1: Normalize uploaded column names
    # --------------------------------------------------------
    original_columns = list(df.columns)

    normalized_columns = [
        _normalize_col_name(column)
        for column in original_columns
    ]

    df.columns = _deduplicate_columns(normalized_columns)

    # --------------------------------------------------------
    # Step 2: Build alias lookup
    # --------------------------------------------------------
    all_standard_columns = (
        config.REQUIRED_COLUMNS + config.OPTIONAL_COLUMNS
    )

    mapping = {}
    rename_map = {}

    # --------------------------------------------------------
    # Step 3: Match standard columns against aliases
    # --------------------------------------------------------
    for standard_column in all_standard_columns:
        aliases = config.COLUMN_ALIASES.get(
            standard_column,
            [standard_column],
        )

        for alias in aliases:
            normalized_alias = _normalize_col_name(alias)

            if (
                normalized_alias in df.columns
                and normalized_alias not in rename_map
            ):
                mapping[standard_column] = normalized_alias

                if normalized_alias != standard_column:
                    rename_map[normalized_alias] = standard_column

                break

    # --------------------------------------------------------
    # Step 4: Rename detected columns
    # --------------------------------------------------------
    if rename_map:
        df = df.rename(columns=rename_map)

    # --------------------------------------------------------
    # Step 5: Find missing required columns
    # --------------------------------------------------------
    missing_required = [
        column
        for column in config.REQUIRED_COLUMNS
        if column not in mapping
    ]

    # --------------------------------------------------------
    # Step 6: Create detailed report
    # --------------------------------------------------------
    report = format_mapping_report(
        mapping=mapping,
        missing_required=missing_required,
    )

    return df, report, missing_required


def format_mapping_report(mapping, missing_required):
    """
    Create a UI-friendly mapping report.

    Args:
        mapping: dict of {standard_name: source_name}
        missing_required: list of missing required columns

    Returns:
        dict containing mapped columns, missing columns,
        total count, and human-readable summary.
    """
    report = {
        "mapped": dict(mapping),
        "missing": list(missing_required),
        "total_mapped": len(mapping),
        "summary": [],
    }

    for standard_name, source_name in mapping.items():
        if standard_name == source_name:
            report["summary"].append(
                f"✅ **{standard_name}** — found directly"
            )
        else:
            report["summary"].append(
                f"✅ **{standard_name}** ← mapped from `{source_name}`"
            )

    for column in missing_required:
        report["summary"].append(
            f"❌ **{column}** — not found (required)"
        )

    return report


def _normalize_col_name(name):
    """
    Normalize a column name for reliable alias matching.

    Examples:
        'Order ID'       -> 'order_id'
        ' order-date '   -> 'order_date'
        'Customer ID'    -> 'customer_id'
    """
    name = str(name).strip().lower()

    # Replace any non-alphanumeric sequence with underscore.
    name = re.sub(r"[^a-z0-9]+", "_", name)

    # Remove leading/trailing underscores.
    return name.strip("_")


def _deduplicate_columns(columns):
    """
    Make normalized column names unique.

    Example:
        ['date', 'date', 'revenue']
        -> ['date', 'date_1', 'revenue']
    """
    seen = {}
    result = []

    for column in columns:
        if column in seen:
            seen[column] += 1
            result.append(f"{column}_{seen[column]}")
        else:
            seen[column] = 0
            result.append(column)

    return result
