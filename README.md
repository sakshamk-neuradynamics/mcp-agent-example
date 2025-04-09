# MCP Agent (LangGraph Example)

This project implements an agent using LangGraph and LangChain that leverages the Multi-Server Communication Protocol (MCP) via the `langchain-mcp-adapters` library to interact with external tools running as separate processes or servers.

It's designed primarily to be run and interacted with via the LangGraph development server.

## Key Features

*   **LangGraph Agent:** Built using `langgraph.graph.StateGraph` for robust state management and execution flow.
*   **MCP Integration:** Uses `MultiServerMCPClient` to dynamically connect to and use tools defined in a configuration file.
*   **Configurable Tools:** External tools (like math operations, database queries, etc.) are defined in `src/mcp_agent/utils/tools.json`.
*   **Serialization Handling:** Includes specific logic (`MCPToolNode` with `_sanitize_object`) to handle common JSON serialization issues encountered when passing complex objects (like callback managers) within LangChain/LangGraph tool calls.

## Prerequisites

*   Python 3.12+
*   A virtual environment tool (like `venv` or `uv`)
*   Access to any required external tool servers (e.g., the math server defined in `mcp-test/server.py`).

## Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/sakshamk-neuradynamics/mcp-agent-example.git
    cd mcp-agent
    ```

2.  **Create and activate a virtual environment:**
    *   Using `venv`:
        ```bash
        python -m venv .venv
        source .venv/bin/activate  # On Windows use `.venv\Scripts\activate`
        ```
    *   Using `uv`:
        ```bash
        uv venv
        source .venv/bin/activate # On Windows use `.venv\Scripts\activate`
        ```

3.  **Install dependencies:**
    *   Using `pip`:
        ```bash
        pip install -e .
        ```
    *   Using `uv`:
        ```bash
        uv pip install -e .
        ```
    *(The `-e .` installs the project in editable mode, which is useful for development).*

4.  **Configure Environment Variables:** Some tool configurations (like database connection strings) are dynamically updated based on environment variables.
    *   Copy the example environment file: `cp .env.example .env`.
    *   Edit the `.env` file and fill in the necessary values (e.g., database credentials).
    *   The LangGraph development server (`uv run langgraph dev`) and potentially other scripts will automatically load these variables.
    *   See the logic in `src/mcp_agent/utils/nodes.py` for details on which variables are used (e.g., `DB_HOST`, `DB_USERNAME`, etc.).
    *   External tools are configured in `src/mcp_agent/utils/tools.json`. This file specifies the command, arguments, transport mechanism (stdio, sse, etc.), and other details needed to connect to each tool server. You might need to adjust this file depending on your setup.

## Running the Agent (Recommended Method)

The primary way to run and interact with this agent is through the LangGraph development server:

1.  **Start the server:**
    Make sure your virtual environment is active.
    ```bash
    uv run langgraph dev
    ```
    *(If you don't have `uv`, you might need `pip install uv` first, or adapt the command based on your preferred ASGI server like `uivcorn`).*

2.  **Interact via LangGraph Playground:**
    Open your web browser and navigate to the LangGraph playground URL (usually `http://localhost:1984`). You can send messages to the agent and observe the execution steps and state changes.

## Running the Test Client

A test client is provided in `mcp-test/client.py` to demonstrate direct interaction with the configured tools via the MCP client.

1.  **Ensure Tool Servers are Running:** Make sure any servers required by the `client.py` script (like the weather server) are running in separate terminals. For example:
    ```bash
    # In a separate terminal (with venv activated)
    python mcp-test/weather_server.py
    ```

2.  **Run the client:**
    ```bash
    # In your main terminal (with venv activated)
    python mcp-test/client.py
    ```
    This script will invoke the agent with predefined messages to test specific tool interactions.

## Configuration

*   **Environment Variables:** Some tool configurations (like database connection strings) are dynamically updated based on environment variables.
    *   Copy the example environment file: `cp .env.example .env`
    *   Edit the `.env` file and fill in the necessary values (e.g., database credentials).
    *   The LangGraph development server (`uv run langgraph dev`) and potentially other scripts will automatically load these variables.
    *   See the logic in `src/mcp_agent/utils/nodes.py` for details on which variables are used (e.g., `DB_HOST`, `DB_USERNAME`, etc.).
*   **Tools:** External tools are configured in `src/mcp_agent/utils/tools.json`. This file specifies the command, arguments, transport mechanism (stdio, sse, etc.), and other details needed to connect to each tool server.

## Project Structure

```
.
├── mcp-test/             # Example tool server and client scripts
│   ├── client.py
│   └── server.py
├── src/
│   └── mcp_agent/        # Main agent package source code
│       ├── __init__.py
│       ├── agent.py      # LangGraph graph definition
│       └── utils/
│           ├── __init__.py
│           ├── nodes.py    # Agent/Tool node logic, MCP client setup
│           ├── state.py    # AgentState definition
│           └── tools.json  # Tool configuration file
├── .gitignore
├── .python-version       # (Optional) Python version specifier
├── pyproject.toml        # Project metadata and dependencies (for pip/uv)
└── README.md             # This file
```
