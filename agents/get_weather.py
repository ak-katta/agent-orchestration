from langchain.tools import tool
from langchain_groq import ChatGroq
from langchain.agents import create_agent
from dotenv import load_dotenv
import requests

@tool
def get_weather(location: str) -> str:
    """Get the weather at a City"""

    api_key = "613be52324fe36123f249056195bf88a"
    url = (
        f"https://api.openweathermap.org/data/2.5/weather"
        f"?q={location}&appid={api_key}&units=metric"
    )
    response = requests.get(url)
    data = response.json()
    if data.get("cod") != 200:
        return f"Could not fetch weather for {location}. Error: {data.get('message', 'Unknown error')}"

    temperature = data["main"]["temp"]
    feeling = data["main"]["feels_like"]
    humidity = data["main"]["humidity"]
    pressure = data["main"]["pressure"]
    desc = data["weather"][0]["description"]


    return (
    f"Temperature: {temperature}°C, {feeling}°C, Humidity: {humidity}%, Pressure: {pressure} hPa, Description: {desc}"
    )

llm = ChatGroq(model = "llama-3.3-70b-versatile", temperature = 0)

weather_agent = create_agent(
    model = llm,
    tools = [get_weather],
    system_prompt="""
    You are a weather agent.
    For getting weather at a city, you MUST use the get_weather tool.
    If a tool is unavailable for getting weather at a city, return "Not available"
    """
)


def get_weather_node(state:dict) -> dict:
    user_req = state.get("user_request", "")
    
    result = weather_agent.invoke({
        "messages":[{"role":"user", "content":user_req}]
    })
    return {"messages": [result["messages"][-1]]}


"""
if __name__ == "__main__":
    result = get_weather_node({"user_request": "What is the weather like in Delhi?"})
    print(result["messages"][-1].content)
"""