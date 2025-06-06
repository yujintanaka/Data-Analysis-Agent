# Third-party imports
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph
import json
# Local imports
from pages.graph.state import AgentState
from pages.graph.nodes import (
    brain_node,
    tool_node,
    route_to_tools,
    handle_tool_output,
    get_table_schema
)



class PythonChatBot:
    def __init__(self):
        super().__init__()
        self.reset_chat()   
        self.graph = self.build_graph()
    
    def invoke_graph(self, user_query, input_data):
        starting_image_paths_set = set(sum(self.output_image_paths.values(), []))
        # Clear intermediate outputs before each new graph execution
        input_state = {
            "messages": self.chat_history + [HumanMessage(content=user_query)],
            "input_data": input_data,
            "intermediate_outputs": self.intermediate_outputs
        }
        result = self.graph.invoke(input_state, {"recursion_limit": 15})
        self.chat_history = result["messages"]
        new_image_paths = set(result["output_image_paths"]) - starting_image_paths_set
        self.output_image_paths[len(self.chat_history) - 1] = list(new_image_paths)
        if "intermediate_outputs" in result:
            self.intermediate_outputs = result["intermediate_outputs"]
        
    def reset_chat(self):
        self.chat_history = []
        self.intermediate_outputs = []
        self.output_image_paths = {}
    
    def build_graph(self):
        builder =  StateGraph(AgentState)
        builder.add_node('get_table_schema', get_table_schema)
        builder.add_node('agent', brain_node)
        builder.add_node('tools', tool_node)
        builder.add_node('handle_tool_output', handle_tool_output)

        builder.add_edge('get_table_schema', 'agent')
        builder.add_conditional_edges('agent', route_to_tools)
        builder.add_edge('tools', 'handle_tool_output')
        builder.add_edge('handle_tool_output', 'agent')

        builder.set_entry_point('get_table_schema')

        return builder.compile()
    
    def stream_graph(self, user_query, input_data):
        starting_image_paths_set = set(sum(self.output_image_paths.values(), []))
        # Clear intermediate outputs before each new graph execution
        input_state = {
            "messages": self.chat_history + [HumanMessage(content=user_query)],
            "input_data": input_data,
            "intermediate_outputs": self.intermediate_outputs
        }
        response = self.graph.stream(input_state, {"recursion_limit": 15}, stream_mode="values")
        for state in response:
            # Update chat history with any new messages
            if "messages" in state and len(state["messages"]) > len(self.chat_history):
                self.chat_history = state["messages"]
                last_message = state["messages"][-1]
                yield last_message

            # Update intermediate outputs with any new outputs
            if "intermediate_outputs" in state and len(state["intermediate_outputs"]) > len(self.intermediate_outputs):
                self.intermediate_outputs = state["intermediate_outputs"]
                
            # Update output image paths with any new paths
            if "output_image_paths" in state:
                new_image_paths = set(state["output_image_paths"]) - starting_image_paths_set
                if new_image_paths:
                    self.output_image_paths[len(self.chat_history) - 1] = list(new_image_paths)