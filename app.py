import streamlit as st
from modules.load_css import load_css
from modules.load_image import img_to_base64

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


