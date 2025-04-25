from langchain_core.tools import tool
from typing import Tuple, Annotated
from .state import AgentState
import pandas as pd
from .db_utils import get_db_engine
import uuid
from langgraph.prebuilt import InjectedState
import plotly.graph_objects as go
import plotly.io as pio
import plotly.express as px
import pandas as pd
import sklearn
import os
import sys
from io import StringIO
import pickle
import json


dataframe_store = {}
persistent_vars = {}

code_to_save_plotly = """import pickle
import uuid
import plotly

for figure in plotly_figures:
    pickle_filename = f"images/plotly_figures/pickle/{uuid.uuid4()}.pickle"
    with open(pickle_filename, 'wb') as f:
        pickle.dump(figure, f)
"""
@tool(parse_docstring = True)
def complete_python_task(
        graph_state: Annotated[dict, InjectedState],
        thought: str,
        python_code: str
    ) -> Tuple[str, dict]:
    """
    Completes a Python task.

    Args:
        thought: Internal thought about the next action to be taken, and the reasoning behind it. This should be formatted in MARKDOWN and be high quality.
        python_code: Python code to be executed to perform analyses, create a new dataset or create a visualization.
    """
    if not os.path.exists("images/plotly_figures/pickle"):
        os.makedirs("images/plotly_figures/pickle")
    
    current_image_pickle_files = os.listdir("images/plotly_figures/pickle")
    
    # Capture stdout
    old_stdout = sys.stdout
    sys.stdout = StringIO()

    # Execute the code and capture the result
    exec_globals = globals().copy()
    exec_globals.update(persistent_vars)
    exec_globals.update({"plotly_figures": []})

    exec(python_code, exec_globals)
    persistent_vars.update({k: v for k, v in exec_globals.items() if k not in globals()})

    # Get the captured stdout
    output = sys.stdout.getvalue()

    # Restore stdout
    sys.stdout = old_stdout

    message = {
        "thought": thought,
        "code": python_code,
        "output": output
    }

    if 'plotly_figures' in exec_globals:
        exec(code_to_save_plotly, exec_globals)
        # Check if any images were created
        new_image_folder_contents = os.listdir("images/plotly_figures/pickle")
        new_image_files = [file for file in new_image_folder_contents if file not in current_image_pickle_files]
        if new_image_files:
            message["output_image_paths"] = new_image_files
        
        persistent_vars["plotly_figures"] = []
    
    return message

@tool(parse_docstring = True)
def make_sql_query(
    graph_state: Annotated[dict, InjectedState],
    thought: str,
    sql_query: str
) -> Tuple[str, dict]:
    """
    Complete a SQL task.

    Args:
        thought: Internal thought about the next action to be taken, and the reasoning behind it. This should be formatted in MARKDOWN and be high quality.
        sql_query: The SQL query to complete in order to retrieve data from the database.
    """
    engine = get_db_engine(graph_state)
    df = pd.read_sql_query(sql_query, engine)
    # Store the DataFrame with a unique identifier
    query_id = f"query_{hash(sql_query)}"
    dataframe_store[query_id] = df

    # Convert DataFrame to dict for JSON serialization
    preview_dict = df.head(10).to_dict(orient="records")
    
    message = {
        "thought": thought,
        "query": sql_query,
        "query_id": query_id,
        "row_count": len(df),
        "columns": list(df.columns),
        "preview": preview_dict,
        "message": "SQL query executed successfully."
    }
    return message

def get_dataframe(query_id: str) -> pd.DataFrame:
    return dataframe_store[query_id]