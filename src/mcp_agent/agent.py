from langgraph.graph import StateGraph, START, END

from mcp_agent.utils.state import AgentState
from mcp_agent.utils.nodes import agent_node, tool_node

graph_builder = StateGraph(AgentState)

graph_builder.add_node("agent", agent_node)
graph_builder.add_node("tool", tool_node)

graph_builder.add_edge(START, "agent")
graph_builder.add_conditional_edges(
    "agent",
    lambda state: "tool" if state["messages"][-1].tool_calls else "end",
    {
        "tool": "tool",
        "end": END,
    },
)
graph_builder.add_edge("tool", "agent")
graph_builder.add_edge("agent", END)

graph = graph_builder.compile()

import asyncio
from langchain_core.messages import HumanMessage

async def main():
    # Initialize conversation state
    current_state = AgentState(messages=[])
    config = {}  # Add any necessary configuration here

    print("Agent: Hello! How can I help you today? (Type 'exit' to quit)")

    while True:
        user_input = input("You: ")
        if user_input.lower() == "exit":
            print("Agent: Goodbye!")
            break

        # Add user message to state
        current_state["messages"].append(HumanMessage(content=user_input))

        try:
            # Invoke the graph
            result = await graph.ainvoke(current_state, config)

            # Extract the latest AI message
            ai_message = result["messages"][-1]

            # Print AI response
            if hasattr(ai_message, 'content') and ai_message.content:
                print(f"Agent: {ai_message.content}")
            if hasattr(ai_message, 'tool_calls') and ai_message.tool_calls:
                print(f"Agent: (Executing tools: {', '.join([tc['name'] for tc in ai_message.tool_calls])})")

            # Update state with the full result for the next turn
            current_state = result

        except Exception as e:
            print(f"An error occurred: {e}")
            # Optionally reset state or handle error recovery
            current_state = AgentState(messages=[]) # Example: Reset state on error


if __name__ == "__main__":
    asyncio.run(main())
