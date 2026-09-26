
import streamlit as st
from modules.load_css import load_css
from modules.load_image import img_to_base64
from modules import uploader

load_css("assets/style.css")

#  Page Config 
st.set_page_config(
    page_title="E-Commerce Growth Dashboard",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded",
)

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
    #     else:
    #         st.error(status_msg)
    #         df = sample_data.generate()
    #         data_source = "sample"
    #         st.info("📊 Falling back to Sample Dataset")
    # else:
    #     df = sample_data.generate()
    #     data_source = "sample"
    #     st.info("📊 **Using Sample Dataset**")
    #     st.caption("Upload a file above to analyze your own data.")




