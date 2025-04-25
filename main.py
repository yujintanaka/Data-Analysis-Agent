import os
import streamlit as st

# Access the API key from the secrets
api_key = st.secrets["OPENAI_API_KEY"]

# Set the API key for the OpenAI library
os.environ["OPENAI_API_KEY"] = api_key

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