from langchain_core.messages import HumanMessage
from langchain_groq import ChatGroq

llm = ChatGroq(model = "llama-3.3-70b-versatile")

def polish_result_node(state: dict) -> dict:
    last_message = state["messages"][-1]
    content = last_message.content if hasattr(last_message, "content") else str(last_message)

    polisher_llm = llm

    polish_prompt = f"""
You are a professional response formatter.
Polish the following response to be:
- Well structured with clear headings if needed
- Concise but complete
- Free of raw JSON, tool artifacts, or redundant text
- Friendly and readable for the end user

Response to polish:
{content}

Return only the polished response, nothing else.
"""
    result = polisher_llm.invoke([HumanMessage(content=polish_prompt)])
    return {"messages": state["messages"] + [result]}