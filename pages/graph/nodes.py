from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage, ToolMessage, HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from .state import AgentState
import json
from typing import Literal
from .tools import make_sql_query, complete_python_task
from langgraph.prebuilt import ToolNode
import os
from sqlalchemy import inspect
from .db_utils import get_db_session


llm = ChatOpenAI(model="gpt-4o", temperature=0)

tools = [make_sql_query, complete_python_task]

model = llm.bind_tools(tools)
tool_node = ToolNode(tools)

with open(os.path.join(os.path.dirname(__file__), "../prompts/main_prompt.md"), "r") as file:
    prompt = file.read()

chat_template = ChatPromptTemplate.from_messages([
    ("system", prompt),
    ("placeholder", "{messages}"),
])
model = chat_template | model

def get_table_schema(state: AgentState):
    summary = "The following is available to you:"
    if "db_type" in state["input_data"]:
        summary += f"Database Type: {state['input_data']['db_type']}\n"
        
        # Get database schema information
        try:
            with get_db_session(state) as session:
                inspector = inspect(session.get_bind())
                tables = inspector.get_table_names()
                
                summary += "Database Schema:\n"
                for table in tables:
                    summary += f"\nTable: {table}\n"
                    
                    # Get columns
                    columns = inspector.get_columns(table)
                    summary += "Columns:\n"
                    for column in columns:
                        summary += f"  - {column['name']}: {column['type']}"
                        if column.get('nullable') is False:
                            summary += " (NOT NULL)"
                        if column.get('primary_key'):
                            summary += " (PRIMARY KEY)"
                        summary += "\n"
                    
                    # Get foreign keys
                    foreign_keys = inspector.get_foreign_keys(table)
                    if foreign_keys:
                        summary += "Foreign Keys:\n"
                        for fk in foreign_keys:
                            summary += f"  - {', '.join(fk['constrained_columns'])} -> {fk['referred_table']}.{', '.join(fk['referred_columns'])}\n"
                    
                    # Get indexes
                    indexes = inspector.get_indexes(table)
                    if indexes:
                        summary += "Indexes:\n"
                        for idx in indexes:
                            summary += f"  - {idx['name']}: {', '.join(idx['column_names'])}"
                            if idx.get('unique'):
                                summary += " (UNIQUE)"
                            summary += "\n"
                    
                    summary += "\n"
        except Exception as e:
            summary += f"\nNote: Could not retrieve schema information: {str(e)}\n"
    return {"messages": [SystemMessage(content=summary)]}

def brain_node(state: AgentState):
    llm_outputs = model.invoke(state)
    return {"messages": [llm_outputs]}

def route_to_tools(state: AgentState,) -> Literal["tools", "__end__"]:
    """
    Use in the conditional_edge to route to the ToolNode if the last message
    has tool calls. Otherwise, route back to the agent.
    """

    if messages := state.get("messages", []):
        ai_message = messages[-1]
    else:
        raise ValueError(f"No messages found in input state to tool_edge: {state}")
    
    if hasattr(ai_message, "tool_calls") and len(ai_message.tool_calls) > 0:
        return "tools"
    return "__end__"

def handle_tool_output(state: AgentState) -> AgentState:
    """
    Processes the output from the most recent tool calls and updates the state with intermediate outputs
    and current variables. Returns the original state if there's an error processing any tool output.
    """ 
    if not state.get("messages"):
        return state

    try:
        # Initialize state update with empty lists
        state_update = {
            "intermediate_outputs": []
        }
        image_paths = []
        
        # Find the last non-tool message to determine where to start processing
        last_non_tool_idx = -1
        for i, message in enumerate(reversed(state["messages"])):
            if not isinstance(message, ToolMessage):
                last_non_tool_idx = len(state["messages"]) - i - 1
                break
        
        # Process only the messages after the last non-tool message
        for message in state["messages"][last_non_tool_idx + 1:]:
            if not isinstance(message, ToolMessage):
                continue
                
            try:
                tool_output = json.loads(message.content)
                state_update["intermediate_outputs"].append(tool_output)
                
                # Accumulate image paths if present
                if "output_image_paths" in tool_output:
                    image_paths.extend(tool_output["output_image_paths"])
            except (json.JSONDecodeError, TypeError):
                # Skip invalid tool outputs but continue processing other messages
                continue
        
        # Only add output_image_paths to state update if we found any
        if image_paths:
            state_update["output_image_paths"] = image_paths
            
        # Only return state update if we found valid tool outputs
        if state_update["intermediate_outputs"]:
            return state_update
        return state
        
    except Exception:
        # Return original state if there's any error in the overall process
        return state

