from langchain.tools import tool
from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from dotenv import load_dotenv

load_dotenv()

@tool
def add(a:float, b:float) -> float:
    """This returns sum of two floating variables a and b"""
    return a+b

@tool
def subtract(a:float, b:float) -> float:
    """This returns difference of two floating variables a and b"""
    return a-b

@tool 
def multiply(a:float, b:float) -> float:
    """This returns product of two floating variables a and b"""
    return a*b

@tool
def divide(a:float, b:float) -> str:
    """This returns division of two floating-point variables a and b and also check if it is divided by 0, the result should be indefinite"""
    if b == 0:
        return "undefined"
    return str(a/b)
    

math_tools = [add,subtract,multiply,divide]

llm = ChatGroq(model = "llama-3.3-70b-versatile")

maths_agent_executor = create_agent(
    model = llm,
    tools = math_tools,
    system_prompt  = """
    You are a mathematician.
    For addition, subtraction, multiplication, and division,you MUST use the available tools.
    If a tool is unavailable for a mathematical operation,
    For any other mathematical operation
    (exponentiation, logarithms, trigonometry, roots),
    use your own reasoning.
    You also need to provide results directly without any steps how to calculate the results.
    """
)


def maths_node(state: dict) -> dict:
    user_request = state.get("user_request", "")
    result = maths_agent_executor.invoke({
        "messages": [{"role": "user", "content": user_request}]
    })
    return {"messages": [result["messages"][-1]]}


"""
config = {"configurable":{"thread_id":"1"}}
response = maths_agent_executor.invoke(
    {"messages": [("user", "What is e^2 then calculate 2*20")]},
    config
)
print(response["messages"][-1].content)
"""