from langgraph.graph import StateGraph, START,END 
from typing import TypedDict,Sequence, Annotated
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, HumanMessage ,ToolMessage,SystemMessage
from langchain.tools import tool
from langgraph.prebuilt import tool_node , ToolNode
from langgraph.graph.message import add_messages # add message is reducer function to provide metadata
from dotenv import load_dotenv

load_dotenv()

class AgentState(TypedDict):
    messages : Annotated[Sequence[BaseMessage],add_messages] #sequence[basemessage] is datatype


@tool
def add(a:int, b:int):
    """ this function add the two numbers"""
    return a + b


@tool
def subtract(a:int, b:int):
    """this for to subtract the two numbers"""
    return a - b

@tool
def multiply(a: int, b: int):
    """Multiplication function"""
    return a * b


tools = [add,subtract,multiply]

model = ChatOpenAI(model ='gpt-4o').bind_tools(tools)

def model_call(state:AgentState)->AgentState:
    systemprompt = systemprompt(content = "you are the my ai assistant so reply me with your best bilities")
    response  = model.invoke([systemprompt] + state['messages'])
    return {'messages':[response]}

def should_continue(state: AgentState): 
    messages = state["messages"]
    last_message = messages[-1]
    if not last_message.tool_calls: 
        return "end"
    else:
        return "continue"

graph = StateGraph(AgentState)
graph.add_node("our_agent", model_call)


tool_node = ToolNode(tools=tools)
graph.add_node("tools", tool_node)

graph.set_entry_point("our_agent")

graph.add_conditional_edges(
    "our_agent",
    should_continue,
    {
        "continue": "tools",
        "end": END,
    },
)

graph.add_edge("tools", "our_agent")

app = graph.compile()
