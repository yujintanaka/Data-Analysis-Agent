import os
import streamlit as st
from dotenv import load_dotenv


st.set_page_config(page_title="EDA App", page_icon=":bar_chart:", layout="wide")

def is_remote_host():
    """
    Check if the app is running on Streamlit Cloud.
    Returns True if running on Streamlit Cloud, False if running locally.
    """
    try:
        # Try to access a secret - if it succeeds, we're on Streamlit Cloud
        _ = st.secrets["OPENAI_API_KEY"]
        return True
    except:
        return False

# Load environment variables from .env file if running locally
if not is_remote_host():
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        st.error("API key not found. Please check your environment configuration.")
else:
    try:
        # Access the API key from Streamlit secrets if running on Streamlit Cloud
        api_key = st.secrets["OPENAI_API_KEY"]
    except:
        st.error("Couldn't get API key from secrets")

# Set the API key for the OpenAI library
os.environ["OPENAI_API_KEY"] = api_key


data_visualization_page = st.Page(
    "./pages/frontend.py", title="Data Visualization", icon="📈"
)

pg = st.navigation(
    {
        "Visualization Agent": [data_visualization_page]
    }
)

pg.run()