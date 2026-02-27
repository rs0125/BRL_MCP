# BRL-CAD MCP Agent

A natural language interface for [BRL-CAD](https://brlcad.org/) solid modeling, powered by the **Model Context Protocol (MCP)**, **LangGraph**, and **OpenAI**. This project allows users to create and manipulate 3D geometry in BRL-CAD through conversational English instead of memorizing MGED command syntax.

---

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Available Tools](#available-tools)
- [Adding New Tools](#adding-new-tools)
- [Project Structure](#project-structure)
- [License](#license)

---

## Overview

BRL-CAD is a powerful open-source Constructive Solid Geometry (CSG) modeling system, but its Tcl-based MGED interface has a steep learning curve. This project bridges that gap by placing a conversational AI agent in front of BRL-CAD. Users describe geometry in plain English, and a GPT-4o-backed agent translates those descriptions into precise MGED commands, executes them against a live BRL-CAD instance, and reports the results.

The system is built on three layers:

1. **Tcl Socket Listener** -- runs inside BRL-CAD's MGED and accepts commands over a TCP socket.
2. **MCP Tool Server** -- a Python FastMCP server that exposes typed, validated tool functions (sphere creation, boolean operations, etc.) to any MCP-compatible client.
3. **LangGraph Agent Client** -- a ReAct agent that reasons about user requests, selects the appropriate tools, and orchestrates multi-step modeling operations.

---

## Architecture

```
+-------------------+       stdio        +-------------------+      TCP/5555      +-------------------+
|                   | ----------------->  |                   | ----------------->  |                   |
|   client.py       |                    |   mcp_server.py   |                    |   listener.tcl    |
|   (LangGraph      |  MCP Protocol      |   (FastMCP Tool   |  Raw MGED         |   (BRL-CAD MGED   |
|    ReAct Agent)   | <-----------------  |    Server)        | <-----------------  |    Socket Bridge) |
|                   |                    |                   |                    |                   |
+-------------------+                    +-------------------+                    +-------------------+
        |                                                                                  |
        | User prompt                                                              MGED commands
        v                                                                          evaluated live
   Terminal CLI                                                                  in BRL-CAD session
```

- **client.py** spawns `mcp_server.py` as a subprocess and communicates over stdio using the MCP protocol.
- **mcp_server.py** opens a TCP connection to `listener.tcl` for each tool invocation.
- **listener.tcl** evaluates MGED commands inside BRL-CAD and returns results over the socket.

---

## Prerequisites

- **Python 3.10+**
- **BRL-CAD** (with MGED) installed and accessible on your system
- **OpenAI API key** with access to the GPT-4o model (or another supported model)
- **Tcl** (bundled with BRL-CAD's MGED)

---

## Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/your-username/brlcad-mcp.git
   cd brlcad-mcp
   ```

2. **Create and activate a virtual environment:**

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

3. **Install Python dependencies:**

   ```bash
   pip install langchain-openai langchain-mcp-adapters langgraph mcp python-dotenv pydantic
   ```

4. **Configure environment variables:**

   ```bash
   cp .env.example .env
   ```

   Edit `.env` and set your OpenAI API key (see [Configuration](#configuration)).

---

## Configuration

All configuration is managed through a `.env` file in the project root. A template is provided in `.env.example`.

| Variable              | Description                                  | Default       |
|-----------------------|----------------------------------------------|---------------|
| `OPENAI_API_KEY`      | Your OpenAI API key (required)               | --            |
| `OPENAI_MODEL`        | The OpenAI model to use                      | `gpt-4o`      |
| `OPENAI_TEMPERATURE`  | Sampling temperature (0 = deterministic)     | `0`           |
| `BRLCAD_HOST`         | Hostname where the Tcl listener is running   | `127.0.0.1`   |
| `BRLCAD_PORT`         | TCP port for the Tcl socket bridge           | `5555`        |

**Important:** Never commit your `.env` file. It is already included in `.gitignore`.

---

## Usage

### Step 1: Start BRL-CAD with the Tcl Listener

Open MGED and create (or open) a database, then source the listener script:

```bash
mged my_model.g
```

Inside the MGED console:

```tcl
source /path/to/brlcad-mcp/listener.tcl
```

You should see:

```
=================================================
 BRL-CAD AI Bridge active.
 Listening for MCP commands on localhost:5555...
=================================================
```

### Step 2: Run the Agent Client

In a separate terminal, activate the virtual environment and start the client:

```bash
source .venv/bin/activate
python client.py
```

You should see:

```
Starting local MCP Client...
Successfully loaded 2 tools from BRL-CAD!

=================================================
 BRL-CAD Terminal Agent Active. Type 'exit' to quit.
=================================================
```

### Step 3: Describe Geometry in Plain English

```
You: Create a sphere named ball.s at the origin with radius 10

AI is calculating geometry...

AI: Created sphere ball.s at (0.0, 0.0, 0.0) with radius 10.0. The sphere is now visible in the MGED viewer.
```

Type `exit` or `quit` to terminate the session.

---

## Available Tools

The MCP server currently exposes the following tools:

### `create_sphere`

Creates a solid sphere primitive in BRL-CAD.

| Parameter | Type    | Description                         |
|-----------|---------|-------------------------------------|
| `name`    | string  | Name of the sphere (e.g., `ball.s`) |
| `x`       | float   | X coordinate of the center          |
| `y`       | float   | Y coordinate of the center          |
| `z`       | float   | Z coordinate of the center          |
| `radius`  | float   | Radius of the sphere                |

### `boolean_combination`

Performs a CSG boolean operation to combine two existing objects.

| Parameter       | Type   | Description                                                        |
|-----------------|--------|--------------------------------------------------------------------|
| `output_name`   | string | Name of the resulting combination (e.g., `result.c`)               |
| `base_object`   | string | The primary object                                                 |
| `operator`      | string | Boolean operator: `u` (union), `-` (subtract), `+` (intersect)    |
| `target_object` | string | The secondary object                                               |

---

## Adding New Tools

The system is designed so that the agent client (`client.py`) never needs modification when new tools are added. Tools are discovered dynamically at startup via the MCP protocol.

To add a new tool:

1. Open `mcp_server.py`.
2. Define a new function decorated with `@mcp.tool()`.
3. Use Pydantic `Field` annotations for all parameters to provide type-safe descriptions for the LLM.
4. Construct the appropriate MGED command string and send it through `send_to_brlcad()`.

**Example -- adding a cylinder tool:**

```python
@mcp.tool()
def create_cylinder(
    name: str = Field(..., description="Name of the cylinder, e.g., 'tube.s'"),
    base_x: float = Field(..., description="X coordinate of the base center"),
    base_y: float = Field(..., description="Y coordinate of the base center"),
    base_z: float = Field(..., description="Z coordinate of the base center"),
    height_x: float = Field(..., description="X component of the height vector"),
    height_y: float = Field(..., description="Y component of the height vector"),
    height_z: float = Field(..., description="Z component of the height vector"),
    radius: float = Field(..., description="Radius of the cylinder")
) -> str:
    """Creates a right circular cylinder (RCC) in BRL-CAD."""
    cmd = f"in {name} rcc {base_x} {base_y} {base_z} {height_x} {height_y} {height_z} {radius}"
    result = send_to_brlcad(cmd)
    send_to_brlcad(f"draw {name}")
    send_to_brlcad("autoview")
    return f"Created cylinder {name}. Output: {result}"
```

The next time `client.py` is started, the agent will automatically discover and be able to use the new tool.

---

## Project Structure

```
brlcad-mcp/
|-- client.py          # LangGraph ReAct agent with interactive CLI
|-- mcp_server.py      # FastMCP tool server exposing BRL-CAD operations
|-- listener.tcl       # Tcl socket bridge sourced inside BRL-CAD MGED
|-- .env               # Local environment configuration (not committed)
|-- .env.example       # Template for environment variables
|-- .gitignore         # Git ignore rules
```

---

## License

This project is provided as-is for educational and research purposes. See the BRL-CAD project for its own licensing terms (LGPL 2.1).
