import json
import os
import asyncio
import copy
from langchain.chat_models import init_chat_model
from langchain_core.runnables import RunnableConfig
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import ToolMessage
from langchain_mcp_adapters.client import MultiServerMCPClient
from typing import Dict, Any

from mcp_agent.utils.state import AgentState

with open("src/mcp_agent/utils/tools.json", "r") as f:
    tools = json.load(f)
    if os.environ.get("DB_HOST"):
        tools["postgres"]["args"][-1] = f"postgresql://{os.environ.get('DB_USERNAME')}:{os.environ.get('DB_PASSWORD')}@{os.environ.get('DB_HOST')}:{os.environ.get('DB_PORT')}/{os.environ.get('DB_NAME')}"
        print(tools["postgres"]["args"])
        
async def agent_node(state: AgentState, config: RunnableConfig):
    model = init_chat_model(
        model="gpt-4o-mini",
        temperature=0.5,
        configurable_fields=["model", "model_provider", "temperature", "max_tokens"],
        config_prefix="agent",
    )
    
    default_system_prompt = """
    You are a helpful assistant.
    """
    system_prompt = config.get("system_prompt", default_system_prompt)
    
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            ("placeholder", "{messages}"),
        ]
    )
    
    async with MultiServerMCPClient(tools) as client:
        agent = prompt | model.bind_tools(client.get_tools())
        response = await agent.ainvoke(state)
        return {"messages": [response]}

class MCPToolNode:
    async def __call__(self, inputs: dict):
        message = inputs["messages"][-1]
        outputs = []
        async with MultiServerMCPClient(tools) as client:
            tools_by_name = {tool.name: tool for tool in client.get_tools()}
            for tool_call in message.tool_calls:
                try:
                    # Use deepcopy to detach from any non-serializable objects
                    # This breaks any reference to callback managers
                    safe_args = self._sanitize_object(tool_call["args"])
                    
                    tool_result = await tools_by_name[tool_call["name"]].ainvoke(safe_args)
                    safe_result = self._sanitize_object(tool_result)
                    
                    outputs.append(
                        ToolMessage(
                            content=json.dumps(safe_result) if not isinstance(safe_result, str) else safe_result,
                            name=tool_call["name"],
                            tool_call_id=tool_call["id"],
                        )
                    )
                except Exception as e:
                    # Handle errors gracefully
                    error_message = f"Error executing tool {tool_call['name']}: {str(e)}"
                    outputs.append(
                        ToolMessage(
                            content=error_message,
                            name=tool_call["name"],
                            tool_call_id=tool_call["id"],
                        )
                    )
        return {"messages": outputs}
    
    def _sanitize_object(self, obj: Any) -> Any:
        """Sanitize object to ensure it's JSON serializable.
        
        This method attempts to sanitize objects by:
        1. Using deepcopy when possible to break references to non-serializable objects
        2. Converting non-serializable objects to strings
        3. Handling common container types recursively
        """
        try:
            # Try deep copy first - this helps break references to callback managers
            return copy.deepcopy(obj)
        except:
            # If deepcopy fails, handle specific types
            if isinstance(obj, (str, int, float, bool, type(None))):
                return obj
            elif isinstance(obj, dict):
                return {k: self._sanitize_object(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [self._sanitize_object(item) for item in obj]
            elif hasattr(obj, "to_dict") and callable(getattr(obj, "to_dict")):
                # Some LangChain objects have to_dict method
                return self._sanitize_object(obj.to_dict())
            else:
                # Last resort: stringify
                return str(obj)

tool_node = MCPToolNode()
