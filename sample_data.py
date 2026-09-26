import pandas as pd
import numpy as np
import streamlit as st

@st.cache_data
def generate(n_orders=1000, seed=42):
    """
    Generate dummy e-commerce data for growth analysis.

    Columns:
        order_id
        date
        revenue
        customer_id
    """

    np.random.seed(seed)

    # -------------------------
    # 1. Generate dates
    # -------------------------
    start_date = pd.Timestamp("2024-01-01")
    end_date = pd.Timestamp("2024-12-31")

    random_days = np.random.randint(
        0,
        (end_date - start_date).days + 1,
        size=n_orders
    )

    dates = [
        start_date + pd.Timedelta(days=int(day))
        for day in random_days
    ]

    # -------------------------
    # 2. Generate customer IDs
    # -------------------------
    n_customers = 300

    customer_ids = [
        f"CUST-{i:04d}"
        for i in range(1, n_customers + 1)
    ]

    assigned_customers = np.random.choice(
        customer_ids,
        size=n_orders
    )

    # -------------------------
    # 3. Generate revenue
    # -------------------------
    revenue = np.random.normal(
        loc=1500,
        scale=500,
        size=n_orders
    )

    revenue = np.clip(
        revenue,
        100,
        None
    ).round(2)

    # -------------------------
    # 4. Create DataFrame
    # -------------------------
    df = pd.DataFrame({
        "order_id": [
            f"ORD-{i:04d}"
            for i in range(1, n_orders + 1)
        ],
        "date": dates,
        "revenue": revenue,
        "customer_id": assigned_customers
    })

    # Sort by date
    df = (
        df.sort_values("date")
          .reset_index(drop=True)
    )

    return df

