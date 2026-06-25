from typing import Annotated, Sequence
from typing_extensions import TypedDict
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

class TeamState(TypedDict):
    """add_messages will always be used to store previous chat history in lists
        and always append to the message instead of updating it"""
    messages : Annotated[Sequence[BaseMessage], add_messages]
    
    """ Tracks which agent supervisor agent want to run"""
    next : str