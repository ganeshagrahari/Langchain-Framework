from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver # we are using ram to store the states in producntion we are using the database 
from langgraph.graph.message import add_messages
from dotenv import load_dotenv

load_dotenv()

llm = ChatOpenAI()

class ChatState(TypedDict):
    messages : Annotated[list[BaseMessage], add_messages]

def chat_node(state:ChatState):
    #take user query from user 
    messages = state['messages']

    #Send to llm 
    response = llm.invoke(messages)

    #response store in state
    return {'messages': [response]} 

checkpointer = InMemorySaver()   

graph = StateGraph(ChatState)

#add nodes 
graph.add_node('chat_node', chat_node)

#add edges 
graph.add_edge(START, 'chat_node')
graph.add_edge('chat_node', END)

chatbot = graph.compile(checkpointer=checkpointer)