"""
config.py — Growth Overview Dashboard Configuration
----------------------------------------------------
Single source of truth for:
- Required & optional columns
- Column alias mapping
- Currency cleanup
- Date formats
- Chart configuration
- Text normalization
- Safe math utilities

Dashboard schema:
    order_id, date, revenue, customer_id
"""

# ============================================================
# Required & Optional Columns
# ============================================================

REQUIRED_COLUMNS = [
    "order_id",
    "date",
    "revenue",
    "customer_id",
]

# Keep this empty for the first Growth Overview dashboard.
# Add columns here only when a metric/chart genuinely needs them.
OPTIONAL_COLUMNS = []


# ============================================================
# Column Alias Map
# ============================================================
# Each standard column name maps to possible names found in
# uploaded CSV/XLSX files.

COLUMN_ALIASES = {
    "order_id": [
        "order_id",
        "orderid",
        "order_number",
        "order_no",
        "order",
        "transaction_id",
        "transactionid",
        "txn_id",
        "invoice_id",
        "invoice_no",
    ],

    "date": [
        "date",
        "order_date",
        "purchase_date",
        "transaction_date",
        "created_at",
        "created_date",
        "sale_date",
        "sales_date",
        "invoice_date",
        "order_datetime",
        "transaction_datetime",
        "dt",
        "dates",
    ],

    "revenue": [
        "revenue",
        "sales",
        "sale",
        "amount",
        "total_amount",
        "order_value",
        "order_amount",
        "total_sales",
        "total_revenue",
        "sale_amount",
        "gmv",
        "gross_revenue",
        "net_revenue",
        "price",
        "total_price",
        "transaction_amount",
    ],

    "customer_id": [
        "customer_id",
        "customerid",
        "customer",
        "cust_id",
        "custid",
        "client_id",
        "clientid",
        "user_id",
        "userid",
        "buyer_id",
        "buyerid",
    ],
}


# ============================================================
# Currency Symbols / Characters to Strip
# ============================================================
# Used before converting revenue to numeric.

CURRENCY_SYMBOLS = [
    "₹",
    "$",
    "€",
    "£",
    "¥",
    ",",
]


# ============================================================
# Date Formats to Try
# ============================================================
# Used as fallback formats when automatic date parsing needs
# explicit format attempts.

DATE_FORMATS = [
    "%Y-%m-%d",
    "%d-%m-%Y",
    "%m-%d-%Y",
    "%d/%m/%Y",
    "%m/%d/%Y",
    "%Y/%m/%d",
    "%d.%m.%Y",
    "%Y.%m.%d",
    "%d %b %Y",
    "%d %B %Y",
    "%b %d, %Y",
    "%B %d, %Y",
]


# ============================================================
# Chart Configuration
# ============================================================
# Centralized chart defaults so individual dashboard pages
# do not repeat styling/configuration.

CHART_TEMPLATE = "plotly_white"
CHART_HEIGHT = 350

CHART_CONFIG = {
    "displayModeBar": False,
    "responsive": True,
}

# Growth Overview charts should use a small, consistent palette.
CHART_COLORS = [
    "#636EFA",
    "#00CC96",
    "#EF553B",
    "#AB63FA",
    "#FFA15A",
    "#19D3F3",
]


# ============================================================
# Text Columns
# ============================================================
# Columns that should be normalized as text.
# These are not required for the current four-column schema,
# but keeping the setting makes the data-cleaning layer reusable.

TEXT_COLUMNS = [
    "order_id",
    "customer_id",
]


# ============================================================
# Safe Math Utilities
# ============================================================

def safe_divide(numerator, denominator, default=0.0):
    """Safely divide two values without raising ZeroDivisionError."""
    try:
        if denominator is None or denominator == 0:
            return default
        return numerator / denominator
    except (TypeError, ZeroDivisionError):
        return default


def safe_pct_change(new_val, old_val, default=0.0):
    """
    Safely calculate percentage change.

    Formula:
        ((new - old) / old) * 100
    """
    try:
        if old_val is None or old_val == 0:
            return default
        return ((new_val - old_val) / old_val) * 100
    except (TypeError, ZeroDivisionError):
        return default
