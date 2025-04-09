from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent

from pprint import pprint

from langchain_openai import ChatOpenAI
model = ChatOpenAI(model="gpt-4o-mini")

async def main():
    async with MultiServerMCPClient(
        {
            "math": {
                "command": "python",
                # Make sure to update to the full absolute path to your math_server.py file
                "args": ["./mcp-test/server.py"],
                "transport": "stdio",
            },
            "weather": {
                # make sure you start your weather server on port 8000
                "url": "http://localhost:8000/sse",
                "transport": "sse",
            },
            "postgres": {
                "command": "docker",
                "args": [
                    "run", 
                    "-i", 
                    "--rm", 
                    "mcp/postgres", 
                    "<your-connection-string>"
                ],
                "env": {
                    "NODE_TLS_REJECT_UNAUTHORIZED": "0"
                },
                "transport": "stdio",
            }
        }
    ) as client:
        agent = create_react_agent(model, client.get_tools())
        
        while True:
            user_input = input("Enter your query (or type 'exit' to quit): ")
            if user_input.lower() == 'exit':
                break
            response = await agent.ainvoke({"messages": user_input})
            pprint(response["messages"][-1].content)

import asyncio
asyncio.run(main())