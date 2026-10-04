
import streamlit as st
from modules.load_css import load_css
from modules.load_image import img_to_base64
from modules import uploader
from modules.growth_analysis import aggregate_growth, build_growth_insight
from modules.visualization import (
    aov_trend_chart,
    orders_trend_chart,
    revenue_trend_chart,
    revenue_vs_orders_chart,
)
import sample_data
from modules import schema_detection
from modules import data_cleaning


def format_currency(value):
    if abs(value) >= 1_000_000:
        return f"₹{value / 1_000_000:,.1f}M"
    if abs(value) >= 1_000:
        return f"₹{value / 1_000:,.1f}K"
    return f"₹{value:,.2f}"


def format_growth(value):
    return "N/A" if value is None else f"{value:+.1f}%"


#  Page Config 
st.set_page_config(
    page_title="E-Commerce Growth Overview Dashboard",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded",
)

load_css("assets/style.css")

# Sidebar image and profile information

with st.sidebar:
    # Profile section
    img_base64 = img_to_base64("assets/me.jpg")
    if img_base64:
        st.markdown(
            f'<div style="text-align:center; padding: 1rem 0;">'
            f'<img src="data:image/jpeg;base64,{img_base64}" class="profile-img">'
            f'</div>',
            unsafe_allow_html=True,
        )
    st.markdown("<h3 style='text-align:center; margin-bottom:0;'>Raja Poddar -- Ramah</h3>", unsafe_allow_html=True)
    st.markdown(
        "<p style='text-align:center; color:#6b7280; font-size:0.85rem;'>"
        "Ex- Data Analyst | Ex- GST Consultant | Web Developer "
        "</p>",
        unsafe_allow_html=True,
    )

    st.divider()


    # File Uploader
    st.markdown("### 📁 Data Source")
    uploaded_file = st.file_uploader(
        "Upload CSV or Excel",
        type=["csv", "xlsx"],
        help="Upload an e-commerce dataset with columns like date, order_id, "
             "customer_id, revenue. If no file is uploaded, sample data is used.",

    )


    st.divider()

    # Data source status
    df = None
    data_source = ""

    if uploaded_file is not None:
        df, status_msg = uploader.parse_file(uploaded_file)
        if df is not None:
            data_source = "uploaded"
            st.success("📁 **Using Uploaded Dataset**")
            st.caption(status_msg)
        else:
            st.error(status_msg)
            df = sample_data.generate()
            data_source = "sample"
            st.info("📊 Falling back to Sample Dataset")
    else:
        df = sample_data.generate()
        data_source = "sample"
        st.info("📊 **Using Sample Dataset**")
        st.caption("Upload a file above to analyze your own data.")


#  Main Area: Header 
st.markdown(
    '<div class="main-header">'
    '<h1>🚀 E-Commerce Growth Overview Intelligence Tool By Ramah</h1>'
    '<h3>Analytics for growth Overview diagnostics</h3>'
    '</div>',
    unsafe_allow_html=True,
)


#  Data Preview 
with st.expander("👀 Data Preview", expanded=False):
    st.dataframe(df.head(100), use_container_width=True, height=300)
    st.caption(f"Showing first {min(100, len(df))} rows of {len(df):,} total rows")

#  Schema Detection 
mapped_df, mapping, missing_required = schema_detection.detect_and_map(df)

mapping_report = schema_detection.format_mapping_report(mapping, missing_required)
with st.expander("🗺️ Column Mapping Summary", expanded=False):
    for line in mapping_report["summary"]:
        st.markdown(line)
    st.caption(f"Total columns mapped: {mapping_report['total_mapped']}")

if missing_required:
    st.error(
        f"❌ **Missing required columns:** {', '.join(missing_required)}\n\n"
        f"Your dataset must have columns that match: `date`, `order_id`, `customer_id`, `revenue`. "
        f"Please check your column names and re-upload."
    )
    st.stop()


#  Data Cleaning 
clean_df, cleaning_report = data_cleaning.clean(mapped_df)

cleaning_messages = data_cleaning.format_cleaning_report(cleaning_report)
with st.expander("🧹 Data Cleaning Report", expanded=False):
    for msg in cleaning_messages:
        st.markdown(msg)

if len(clean_df) < 5:
    st.warning("⚠️ **Very small dataset** — results may not be meaningful with fewer than 5 rows.")

if clean_df.empty:
    st.error("❌ No valid data remaining after cleaning. Please check your dataset.")
    st.stop()

st.markdown("## Growth Overview")
granularity = st.selectbox(
    "Trend interval",
    options=["Daily", "Weekly", "Monthly", "Quarterly"],
    index=2,
    help="Growth KPIs compare the latest represented interval with the previous interval.",
)

try:
    analysis = aggregate_growth(clean_df, granularity)
except ValueError as error:
    st.error(str(error))
    st.stop()

st.caption(
    f"Latest interval: **{analysis['latest_period_label']}**"
    f" · Compared with: **{analysis['previous_period_label'] or 'not available'}**"
)
if analysis["excluded_rows"]:
    st.caption(
        f"{analysis['excluded_rows']:,} rows without a valid date, order ID, or revenue "
        "were excluded from growth metrics."
    )

latest = analysis["latest"]
growth = analysis["growth"]
kpi_columns = st.columns(4)
kpi_columns[0].metric(
    "Revenue",
    format_currency(latest["revenue"]),
    format_growth(growth["revenue"]),
)
kpi_columns[1].metric(
    "Orders",
    f"{latest['orders']:,.0f}",
    format_growth(growth["orders"]),
)
kpi_columns[2].metric(
    "Unique Customers",
    f"{latest['customers']:,.0f}",
    format_growth(growth["customers"]),
)
kpi_columns[3].metric(
    "Average Order Value",
    format_currency(latest["aov"]) if latest["orders"] else "N/A",
    format_growth(growth["aov"]),
)

revenue_column, orders_column = st.columns(2)
with revenue_column:
    st.plotly_chart(revenue_trend_chart(analysis), use_container_width=True, config={"displayModeBar": False})
with orders_column:
    st.plotly_chart(orders_trend_chart(analysis), use_container_width=True, config={"displayModeBar": False})

comparison_column, aov_column = st.columns(2)
with comparison_column:
    st.plotly_chart(
        revenue_vs_orders_chart(analysis),
        use_container_width=True,
        config={"displayModeBar": False},
    )
with aov_column:
    st.plotly_chart(aov_trend_chart(analysis), use_container_width=True, config={"displayModeBar": False})

st.markdown("### Growth Summary")
st.info(build_growth_insight(analysis))
