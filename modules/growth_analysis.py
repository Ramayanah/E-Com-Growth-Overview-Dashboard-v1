"""Aggregation and plain-language growth interpretation."""

import pandas as pd


PERIOD_FREQUENCIES = {
    "Daily": "D",
    "Weekly": "W-SUN",
    "Monthly": "MS",
    "Quarterly": "QS",
}


def aggregate_growth(df, granularity):
    """Aggregate growth metrics and compare the latest bucket to the prior one."""
    if granularity not in PERIOD_FREQUENCIES:
        raise ValueError(
            f"Unsupported granularity {granularity!r}. "
            f"Choose one of: {', '.join(PERIOD_FREQUENCIES)}."
        )

    required_columns = {"date", "order_id", "revenue", "customer_id"}
    missing_columns = required_columns.difference(df.columns)
    if missing_columns:
        raise ValueError(
            f"Growth analysis requires these columns: {', '.join(sorted(missing_columns))}."
        )

    data = df[sorted(required_columns)].copy()
    data["date"] = pd.to_datetime(data["date"], errors="coerce")
    data["revenue"] = pd.to_numeric(data["revenue"], errors="coerce")
    data["order_id"] = data["order_id"].astype("string").str.strip()
    data = data.dropna(subset=["date", "revenue", "order_id"])
    data = data[data["order_id"] != ""]

    if data.empty:
        raise ValueError("No rows with a valid date, order ID, and revenue remain for analysis.")

    def count_customers(customer_ids):
        valid_ids = customer_ids.dropna().astype("string").str.strip()
        valid_ids = valid_ids[
            ~valid_ids.str.casefold().isin({"", "unknown", "nan", "none", "null", "na"})
        ]
        return int(valid_ids.nunique())

    frequency = PERIOD_FREQUENCIES[granularity]
    periods = (
        data.groupby(pd.Grouper(key="date", freq=frequency))
        .agg(
            revenue=("revenue", "sum"),
            orders=("order_id", "nunique"),
            customers=("customer_id", count_customers),
        )
        .sort_index()
    )

    full_index = pd.date_range(
        start=periods.index.min(),
        end=periods.index.max(),
        freq=frequency,
        name="date",
    )
    periods = periods.reindex(full_index, fill_value=0)
    periods["aov"] = periods["revenue"].div(periods["orders"].where(periods["orders"] != 0))

    latest = periods.iloc[-1]
    previous = periods.iloc[-2] if len(periods) > 1 else None
    growth = {
        metric: _percentage_change(latest[metric], previous[metric])
        if previous is not None
        else None
        for metric in ("revenue", "orders", "customers", "aov")
    }

    return {
        "granularity": granularity,
        "series": periods,
        "latest": latest.to_dict(),
        "previous": previous.to_dict() if previous is not None else None,
        "growth": growth,
        "excluded_rows": len(df) - len(data),
        "latest_period_label": _format_period(periods.index[-1], granularity),
        "previous_period_label": (
            _format_period(periods.index[-2], granularity)
            if previous is not None
            else None
        ),
    }


def build_growth_insight(analysis):
    """Summarize the latest period's growth and likely top-line drivers."""
    latest_label = analysis["latest_period_label"]
    previous_label = analysis["previous_period_label"]
    growth = analysis["growth"]

    if previous_label is None:
        return (
            f"Only one {analysis['granularity'].lower()} period is available "
            "for comparison, so growth rates cannot yet be calculated."
        )

    revenue_growth = growth["revenue"]
    orders_growth = growth["orders"]
    aov_growth = growth["aov"]

    if revenue_growth is None:
        summary = (
            f"Revenue growth for **{latest_label}** versus **{previous_label}** "
            "is unavailable because the previous period has no positive revenue baseline."
        )
    else:
        direction = "increased" if revenue_growth >= 0 else "declined"
        summary = (
            f"Revenue **{direction} {abs(revenue_growth):.1f}%** in **{latest_label}** "
            f"compared with **{previous_label}**."
        )

        if orders_growth is not None and aov_growth is not None:
            if orders_growth > 0 and aov_growth > 0:
                driver = (
                    "both higher order volume and higher average order value"
                    if abs(orders_growth - aov_growth) < 1
                    else (
                        "higher order volume"
                        if orders_growth > aov_growth
                        else "higher average order value"
                    )
                )
                summary += (
                    f" Orders grew **{orders_growth:.1f}%** and AOV grew "
                    f"**{aov_growth:.1f}%**, indicating growth from {driver}."
                )
            elif orders_growth > 0 and aov_growth <= 0:
                summary += (
                    f" Orders grew **{orders_growth:.1f}%**, while AOV "
                    f"{_describe_change(aov_growth)}; order volume was the positive driver."
                )
            elif aov_growth > 0 and orders_growth <= 0:
                summary += (
                    f" AOV grew **{aov_growth:.1f}%**, while orders "
                    f"{_describe_change(orders_growth)}; higher order value was the positive driver."
                )
            else:
                summary += (
                    f" Orders {_describe_change(orders_growth)} and AOV "
                    f"{_describe_change(aov_growth)}, so neither measure indicates "
                    "a positive volume or order-value contribution."
                )
        else:
            summary += " There is not enough baseline data to separate order-volume and AOV changes."

    customer_growth = growth["customers"]
    if customer_growth is None:
        summary += " Unique-customer growth is unavailable for this comparison."
    else:
        summary += (
            f" Unique customers {_describe_change(customer_growth)} "
            f"({customer_growth:+.1f}%)."
        )

    return summary


def _percentage_change(current, previous):
    if previous is None or pd.isna(previous) or previous <= 0:
        return None
    if pd.isna(current):
        return None
    return float((current - previous) / previous * 100)


def _format_period(timestamp, granularity):
    if granularity == "Daily":
        return timestamp.strftime("%b %d, %Y")
    if granularity == "Weekly":
        return f"week ending {timestamp.strftime('%b %d, %Y')}"
    if granularity == "Monthly":
        return timestamp.strftime("%B %Y")
    return f"Q{timestamp.quarter} {timestamp.year}"


def _describe_change(value):
    if value is None:
        return "was unavailable"
    return "increased" if value > 0 else "declined" if value < 0 else "was unchanged"
