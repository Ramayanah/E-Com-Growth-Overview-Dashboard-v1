"""
data_cleaning.py
----------------
Clean uploaded Growth Overview data.

Expected columns:
    order_id
    date
    revenue
    customer_id

Pure functions — no Streamlit calls.
"""

import re
import numpy as np
import pandas as pd

import config


def clean(df):
    """
    Clean and standardize Growth Overview data.

    Args:
        df: DataFrame with standardized column names
            after schema detection.

    Returns:
        tuple:
            cleaned_df: Cleaned pandas DataFrame
            cleaning_report: Dictionary containing cleaning statistics
    """

    if not isinstance(df, pd.DataFrame):
        raise TypeError("df must be a pandas DataFrame.")

    df = df.copy()

    report = {
        "original_rows": len(df),
        "duplicates_removed": 0,
        "invalid_dates": 0,
        "invalid_revenue": 0,
        "negative_revenue": 0,
        "null_rows_dropped": 0,
        "missing_customer_ids": 0,
        "final_rows": 0,
    }

    # ---------------------------------------------------------
    # 1. Clean column names
    # ---------------------------------------------------------
    df.columns = (
        df.columns
        .astype(str)
        .str.strip()
        .str.lower()
    )

    # ---------------------------------------------------------
    # 2. Clean order_id
    # ---------------------------------------------------------
    if "order_id" in df.columns:
        df["order_id"] = (
            df["order_id"]
            .astype("string")
            .str.strip()
        )

        # Treat empty strings as missing
        df["order_id"] = df["order_id"].replace(
            {"": pd.NA, "nan": pd.NA, "none": pd.NA, "null": pd.NA}
        )

        # Remove duplicate orders
        before = len(df)

        df = df.drop_duplicates(
            subset=["order_id"],
            keep="first"
        )

        report["duplicates_removed"] = before - len(df)

    # ---------------------------------------------------------
    # 3. Convert date
    # ---------------------------------------------------------
    if "date" in df.columns:

        df["date"], invalid_dates = _convert_dates(
            df["date"]
        )

        report["invalid_dates"] = invalid_dates

        # Remove rows where date could not be interpreted
        before = len(df)

        df = df.dropna(
            subset=["date"]
        )

        report["null_rows_dropped"] += before - len(df)

    # ---------------------------------------------------------
    # 4. Clean revenue
    # ---------------------------------------------------------
    if "revenue" in df.columns:

        original_revenue = df["revenue"].copy()

        df["revenue"] = _clean_revenue(
            df["revenue"]
        )

        # Count values that could not be converted
        original_not_null = original_revenue.notna()

        invalid_revenue = (
            original_not_null
            & df["revenue"].isna()
        )

        report["invalid_revenue"] = int(
            invalid_revenue.sum()
        )

        # Track negative revenue
        report["negative_revenue"] = int(
            (df["revenue"] < 0).sum()
        )

    # ---------------------------------------------------------
    # 5. Clean customer_id
    # ---------------------------------------------------------
    if "customer_id" in df.columns:

        df["customer_id"] = (
            df["customer_id"]
            .astype("string")
            .str.strip()
        )

        # Standardize missing customer IDs
        df["customer_id"] = df["customer_id"].replace(
            {
                "": pd.NA,
                "nan": pd.NA,
                "none": pd.NA,
                "null": pd.NA,
                "na": pd.NA,
            }
        )

        missing_customers = df["customer_id"].isna().sum()

        report["missing_customer_ids"] = int(
            missing_customers
        )

        # Use explicit category for aggregation
        df["customer_id"] = df["customer_id"].fillna(
            "unknown"
        )

    # ---------------------------------------------------------
    # 6. Remove completely empty required rows
    # ---------------------------------------------------------
    required_columns = [
        "order_id",
        "date",
        "revenue",
        "customer_id",
    ]

    available_required = [
        col
        for col in required_columns
        if col in df.columns
    ]

    if available_required:

        before = len(df)

        df = df.dropna(
            subset=available_required,
            how="all"
        )

        report["null_rows_dropped"] += (
            before - len(df)
        )

    # ---------------------------------------------------------
    # 7. Add year_month
    # ---------------------------------------------------------
    if "date" in df.columns:

        df["year_month"] = (
            df["date"]
            .dt.to_period("M")
            .astype(str)
        )

    # ---------------------------------------------------------
    # 8. Sort by date
    # ---------------------------------------------------------
    if "date" in df.columns:

        df = df.sort_values(
            by="date",
            ascending=True
        )

    # ---------------------------------------------------------
    # 9. Reset index
    # ---------------------------------------------------------
    df = df.reset_index(drop=True)

    report["final_rows"] = len(df)

    return df, report


def _convert_dates(series):
    """
    Convert values to datetime.

    Tries pandas automatic parsing first.
    Falls back to DATE_FORMATS from config.py
    when necessary.

    Returns:
        tuple:
            converted_series
            invalid_count
    """

    original_not_null = series.notna()

    # First attempt
    converted = pd.to_datetime(
        series,
        errors="coerce"
    )

    # If configured date formats exist,
    # try them when automatic parsing performs poorly.
    date_formats = getattr(
        config,
        "DATE_FORMATS",
        []
    )

    nat_ratio = (
        converted.isna().sum()
        / max(len(series), 1)
    )

    if nat_ratio > 0.5:

        for fmt in date_formats:

            try:

                attempt = pd.to_datetime(
                    series,
                    format=fmt,
                    errors="coerce"
                )

                if (
                    attempt.notna().sum()
                    > converted.notna().sum()
                ):
                    converted = attempt

            except (ValueError, TypeError):
                continue

    invalid_count = int(
        (original_not_null & converted.isna()).sum()
    )

    return converted, invalid_count


def _clean_revenue(series):
    """
    Clean revenue values.

    Handles:
        ₹1,200
        $1,200
        €1,200
        1,200
        1200
        ' 1200 '
        empty/null values

    Returns:
        Numeric pandas Series.
    """

    s = series.astype("string").str.strip()

    # Currency symbols from config.py
    currency_symbols = getattr(
        config,
        "CURRENCY_SYMBOLS",
        ["₹", "$", "€", "£"]
    )

    if currency_symbols:

        pattern = "[" + re.escape(
            "".join(currency_symbols)
        ) + r"\s]"

        s = s.str.replace(
            pattern,
            "",
            regex=True
        )

    # Remove commas used as thousands separators
    s = s.str.replace(
        ",",
        "",
        regex=False
    )

    # Standardize common missing values
    s = s.replace(
        {
            "": pd.NA,
            "nan": pd.NA,
            "none": pd.NA,
            "null": pd.NA,
            "na": pd.NA,
        }
    )

    return pd.to_numeric(
        s,
        errors="coerce"
    )


def format_cleaning_report(report):
    """
    Convert cleaning report into user-friendly messages.

    Args:
        report: Dictionary returned by clean().

    Returns:
        List of messages.
    """

    messages = []

    messages.append(
        f"Started with **{report['original_rows']:,}** rows "
        f"→ **{report['final_rows']:,}** rows after cleaning."
    )

    if report["duplicates_removed"] > 0:
        messages.append(
            f"Removed **{report['duplicates_removed']:,}** "
            f"duplicate orders."
        )

    if report["invalid_dates"] > 0:
        messages.append(
            f"Found **{report['invalid_dates']:,}** "
            f"invalid dates."
        )

    if report["invalid_revenue"] > 0:
        messages.append(
            f"Found **{report['invalid_revenue']:,}** "
            f"invalid revenue values."
        )

    if report["negative_revenue"] > 0:
        messages.append(
            f"Found **{report['negative_revenue']:,}** "
            f"negative revenue values. These were kept."
        )

    if report["missing_customer_ids"] > 0:
        messages.append(
            f"Found **{report['missing_customer_ids']:,}** "
            f"missing customer IDs."
        )

    if report["null_rows_dropped"] > 0:
        messages.append(
            f"Dropped **{report['null_rows_dropped']:,}** "
            f"rows containing no usable required data."
        )

    return messages