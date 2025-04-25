import os
import streamlit as st


st.set_page_config(page_title="EDA App", page_icon=":bar_chart:", layout="wide")

data_visualization_page = st.Page(
    "./pages/frontend.py", title="Data Visualization", icon="📈"
)

pg = st.navigation(
    {
        "Visualization Agent": [data_visualization_page]
    }
)

pg.run()