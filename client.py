import asyncio
import os
from langchain_openai import ChatOpenAI
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent

async def run_agent():
    # 1. Verify the API Key exists in the environment
    if not os.getenv("OPENAI_API_KEY"):
        print("ERROR: OPENAI_API_KEY environment variable not set.")
        return

    # 2. Initialize the "Brain" (OpenAI)
    # Temperature is 0 because we want strict, deterministic CAD math, not creative writing
    model = ChatOpenAI(model="gpt-4o", temperature=0)
    
    # 3. Initialize the MCP Client and connect to your FastMCP server
    print("Starting local MCP Client...")
    client = MultiServerMCPClient(
        {
            "brlcad_server": {
                "command": "python", 
                "args": ["mcp_server.py"], # This tells LangChain to run your server script
                "transport": "stdio",
            }
        }
    )
    
    # Fetch the Pydantic tools we defined in the server
    tools = await client.get_tools()
    print(f"Successfully loaded {len(tools)} tools from BRL-CAD!")
    
    # 4. Create the LangGraph Agent equipped with the BRL-CAD tools
    agent = create_react_agent(model, tools) #
    
    # 5. Start the CLI Chat Loop
    print("\n=================================================")
    print(" BRL-CAD Terminal Agent Active. Type 'exit' to quit.")
    print("=================================================")
    
    while True:
        user_input = input("\nYou: ")
        if user_input.lower() in ["exit", "quit"]:
            break
            
        print("AI is calculating geometry...")
        
        # Invoke the agent with the user's prompt
        response = await agent.ainvoke({"messages": [("user", user_input)]})
        
        # Print the final AI response
        print(f"\nAI: {response['messages'][-1].content}")

if __name__ == "__main__":
    # LangChain MCP clients require an asynchronous event loop to manage the connections
    asyncio.run(run_agent())
