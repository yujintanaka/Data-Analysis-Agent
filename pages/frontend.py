# Standard library imports
import os
import pickle
import socket
import json
# Third-party imports
import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, inspect, text
from langchain_core.messages import HumanMessage, AIMessage

# Database connectors
import sqlite3
import mysql.connector
import psycopg2

# Local imports
from pages.backend import PythonChatBot

def is_remote_host():
    """
    Check if the app is running on Streamlit Cloud.
    Returns True if running on Streamlit Cloud, False if running locally.
    """
    try:
        # Try to access a secret - if it succeeds, we're on Streamlit Cloud
        st.secrets["OPENAI_API_KEY"]
        return True
    except:
        return False

st.header("Data Analysis LangGraph Agent")


def get_database_connection(db_type, **kwargs):
    """
    Unified function to establish database connections for different database types.
    
    Args:
        db_type (str): Type of database ('SQLite', 'MySQL', or 'PostgreSQL')
        **kwargs: Connection parameters specific to each database type
            For SQLite: db_path
            For MySQL/PostgreSQL: host, port, user, password, database
    
    Returns:
        tuple: (connection_uri, engine_object, error_message)
    """
    if db_type == "SQLite":
        try:
            db_path = kwargs.get('db_path')
            if not os.path.exists(db_path):
                return None, None, f"Database file not found: {db_path}"
            uri = f'sqlite:///{db_path}'
            engine = create_engine(uri)
            # Verify connection
            with engine.connect() as conn:
                conn.execute(text("SELECT 1")).fetchone()
            return uri, engine, None
        except Exception as e:
            return None, None, str(e)
    elif db_type == "MySQL":
        try:
            host = kwargs.get('host')
            port = kwargs.get('port')
            user = kwargs.get('user')
            password = kwargs.get('password')
            database = kwargs.get('database')
            uri = f'mysql+mysqlconnector://{user}:{password}@{host}:{port}/{database}'
            engine = create_engine(uri)
            # Verify connection
            with engine.connect() as conn:
                conn.execute(text("SELECT 1")).fetchone()
            return uri, engine, None
        except Exception as e:
            return None, None, str(e)
    elif db_type == "PostgreSQL":
        try:
            host = kwargs.get('host')
            port = kwargs.get('port')
            user = kwargs.get('user')
            password = kwargs.get('password')
            database = kwargs.get('database')
            uri = f'postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}'
            engine = create_engine(uri)
            # Verify connection
            with engine.connect() as conn:
                conn.execute(text("SELECT 1")).fetchone()
            return uri, engine, None
        except Exception as e:
            return None, None, str(e)

def get_schema(engine):
    """
    Get the database schema using SQLAlchemy inspector.
    
    Args:
        engine: SQLAlchemy engine object
    
    Returns:
        dict: Database schema information
    """
    inspector = inspect(engine)
    schema = {}
    
    for table_name in inspector.get_table_names():
        columns = []
        for column in inspector.get_columns(table_name):
            columns.append({
                'name': column['name'],
                'type': str(column['type']),
                'nullable': column['nullable']
            })
        schema[table_name] = columns
    
    return schema

# Initialize session state variables
if 'connection_status' not in st.session_state:
    st.session_state.connection_status = False
if 'db_schema' not in st.session_state:
    st.session_state.db_schema = None
if 'db_type' not in st.session_state:
    st.session_state.db_type = None
if 'db_uri' not in st.session_state:
    st.session_state.db_uri = None
if 'stored_figures' not in st.session_state:
    st.session_state.stored_figures = {}

# Sidebar for database connection
st.sidebar.title("Database Connection")

# If running on Streamlit Cloud, only allow SQLite with chinook.db
if is_remote_host():
    st.sidebar.warning("⚠️ Running on Streamlit Cloud: You can only connect to our sample database.")
    db_type = "SQLite"
    if not st.session_state.connection_status:
        if st.sidebar.button("Connect to chinook.db"):
            uri, engine, error = get_database_connection("SQLite", db_path="data/chinook.db")
            if error:
                st.error(f"Connection Error: {error}")
                st.session_state.connection_status = False
            else:
                st.success("Successfully connected to chinook.db!")
                st.session_state.connection_status = True
                st.session_state.db_type = "SQLite"
                st.session_state.db_schema = get_schema(engine)
                st.session_state.db_uri = uri
else:
    st.sidebar.info("Running locally: You can connect to any database.")
    db_type = st.sidebar.selectbox(
        "Select Database Type",
        ["SQLite", "MySQL", "PostgreSQL"]
    )

    # Create an expander for connection fields
    with st.sidebar.expander("Connection Settings", expanded=not st.session_state.connection_status):
        if db_type == "SQLite":
            db_path = st.text_input("Database Path", "data/chinook.db")
            if st.button("Connect to SQLite"):
                uri, engine, error = get_database_connection("SQLite", db_path=db_path)
                if error:
                    st.error(f"Connection Error: {error}")
                    st.session_state.connection_status = False
                else:
                    st.success("Successfully connected to SQLite database!")
                    st.session_state.connection_status = True
                    st.session_state.db_type = "SQLite"
                    st.session_state.db_schema = get_schema(engine)
                    st.session_state.db_uri = uri

        elif db_type == "MySQL":
            host = st.text_input("Host", "localhost")
            port = st.number_input("Port", value=3306)
            user = st.text_input("Username")
            password = st.text_input("Password", type="password")
            database = st.text_input("Database Name")
        
            if st.button("Connect to MySQL"):
                uri, engine, error = get_database_connection("MySQL", 
                    host=host, port=port, user=user, 
                    password=password, database=database)
                if error:
                    st.error(f"Connection Error: {error}")
                    st.session_state.connection_status = False
                else:
                    st.success("Successfully connected to MySQL database!")
                    st.session_state.connection_status = True
                    st.session_state.db_type = "MySQL"
                    st.session_state.db_schema = get_schema(engine)
                    st.session_state.db_uri = uri

        elif db_type == "PostgreSQL":
            host = st.text_input("Host", "localhost")
            port = st.number_input("Port", value=5432)
            user = st.text_input("Username")
            password = st.text_input("Password", type="password")
            database = st.text_input("Database Name")
            
            if st.button("Connect to PostgreSQL"):
                uri, engine, error = get_database_connection("PostgreSQL", 
                    host=host, port=port, user=user, 
                    password=password, database=database)
                if error:
                    st.error(f"Connection Error: {error}")
                    st.session_state.connection_status = False
                else:
                    st.success("Successfully connected to PostgreSQL database!")
                    st.session_state.connection_status = True
                    st.session_state.db_type = "PostgreSQL"
                    st.session_state.db_schema = get_schema(engine)
                    st.session_state.db_uri = uri

# Display schema if available
if st.session_state.db_schema:
    st.sidebar.subheader("Database Schema")
    for table, columns in st.session_state.db_schema.items():
        with st.sidebar.expander(f"Table: {table}"):
            for col in columns:
                st.write(f"- {col['name']} ({col['type']})")


tab1, tab2 = st.tabs(["Chat Interface", "Agent Actions"])


# Main content area for chatbot
with tab1:
    if st.session_state.connection_status:

        if 'chatbot' not in st.session_state:
            st.session_state.chatbot = PythonChatBot()
        
        # Display chat history
        chat_container = st.container(height=500)
        with chat_container:
            for message_index, message in enumerate(st.session_state.chatbot.chat_history):
                if message.content != "":
                    if isinstance(message, HumanMessage):
                        st.chat_message("Human").markdown(message.content)
                    elif isinstance(message, AIMessage):
                        with st.chat_message("AI"):
                            st.markdown(message.content)

                    if isinstance(message, AIMessage) and message_index in st.session_state.chatbot.output_image_paths:
                        # Display stored figures if available
                        if message_index in st.session_state.stored_figures:
                            for fig in st.session_state.stored_figures[message_index]:
                                st.plotly_chart(fig, use_container_width=True)
                        else:
                            # If figures aren't in session state, try to load from pickle files
                            image_paths = st.session_state.chatbot.output_image_paths[message_index]
                            for image_path in image_paths:
                                pickle_path = os.path.join("images/plotly_figures/pickle", image_path)
                                try:
                                    with open(pickle_path, "rb") as f:
                                        fig = pickle.load(f)

                                    # Store the figure in session state
                                    if message_index not in st.session_state.stored_figures:
                                        st.session_state.stored_figures[message_index] = []
                                    st.session_state.stored_figures[message_index].append(fig)
                                    st.plotly_chart(fig, use_container_width=True)
                                    # Delete the pickle file after loading
                                    try:
                                        os.remove(pickle_path)
                                    except Exception as e:
                                        st.warning(f"Could not delete pickle file: {e}")
                                except FileNotFoundError:
                                    st.warning(f"Figure file not found: {image_path}")
            
        # Chat input
        if user_input := st.chat_input("Ask a question about your data..."):
            # Create input data object with current database info
            input_data = {
                "db_uri": st.session_state.db_uri,
                "db_type": st.session_state.db_type
            }
            
            # Process user message
            with chat_container:
                with st.chat_message("Human"):
                    st.markdown(user_input)
                
                with st.chat_message("AI"):
                    # Iterate through the generator
                    with st.spinner("Thinking..."):
                        for message in st.session_state.chatbot.stream_graph(user_input, input_data):
                            if isinstance(message, AIMessage):
                                st.markdown(message.content)
                        st.rerun()

    else:
        st.info("Please connect to a database first to use the query assistant.")

with tab2:
    if 'chatbot' in st.session_state:
        st.markdown("#### Intermediate Outputs")
        for i, output in enumerate(st.session_state.chatbot.intermediate_outputs):
            with st.expander(f"Step {i+1}"):
                if 'thought' in output:
                    st.markdown("#### Thought Process")
                    st.markdown(output['thought'])
                if 'query' in output:
                    st.markdown("#### SQL Query")
                    st.code(output['query'], language="sql")
                    if 'row_count' in output:
                        st.markdown(f"**Rows Retrieved:** {output['row_count']}")
                    if 'columns' in output:
                        st.markdown("**Columns:**")
                        st.code(", ".join(output['columns']))
                    if 'preview' in output:
                        st.markdown("**Data Preview:**")
                        st.dataframe(pd.DataFrame(output['preview']))
                    if 'message' in output:
                        st.success(output['message'])
                if 'code' in output:
                    st.markdown("#### Python Code")
                    st.code(output['code'], language="python")
                if 'query' not in output:
                    if 'output' in output and output['output'] != "":
                        st.markdown("#### Output")
                        st.text(output['output'])
        if not st.session_state.chatbot.intermediate_outputs:
            st.info("No debug information available yet. Start a conversation to see intermediate outputs.")

