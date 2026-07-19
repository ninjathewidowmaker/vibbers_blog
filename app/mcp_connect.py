from langchain_mcp_adapters.client import MultiServerMCPClient
import asyncio
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_agent
import os

api_key = os.environ["GOOGLE_API_KEY"]

async def main():
    client = MultiServerMCPClient(
        {
            "vibbers_blog": {
                "transport": "streamable-http",
                "url": "http://localhost:6969/mcp"
            }
        } 
    )

    tools = await client.get_tools()
    raw_model = ChatGoogleGenerativeAI(model="gemini-2.5-flash", api_key=api_key)
    model = raw_model.bind_tools(tools)
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant. You have access to a tool to create blog posts. Use it whenever the user requests a new post."),
        MessagesPlaceholder(variable_name="messages"),
    ]) 
    agent = create_agent(model, prompt=prompt)
    print("--- Turn 1: User Request ---")
    response = await agent.ainvoke({
        "messages": [("user", "Can you use the tool to create a blog with name Rust and write a neet content about What are the tools available and how to use them and is this MCP great or not?")]
    })
    print(response)
if __name__ == "__main__":
    asyncio.run(main())
