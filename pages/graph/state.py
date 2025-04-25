from typing import TypedDict, Annotated, Sequence, List
from langchain_core.messages import BaseMessage
from langgraph.graph import add_messages
import operator

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    intermediate_outputs: Annotated[List[dict], operator.add]
    input_data: dict
    output_image_paths: Annotated[List[str], operator.add]