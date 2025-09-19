# MCP Jupyter Notebook Server

**A Model Context Protocol (MCP) server for AI agents to interact with a Jupyter server, exposing a single notebook session for code, markdown, and package management.**

---

## Overview

This package provides an MCP server that allows AI agents or other clients to programmatically control a Jupyter notebook session. It exposes tools to add and run code or markdown cells, and to install Python packages in the notebook kernel.

---

## Tools

| Tool Name                | Description                                                        |
|--------------------------|--------------------------------------------------------------------|
| `notebook.markdown.add`  | Add a markdown cell to the notebook and return its index.          |
| `notebook.code.run`      | Add a code cell, execute it, and return the execution result.      |
| `notebook.packages.add`  | Ensure the given Python packages are installed in the kernel.      |

---

## Installation

### With pip

```sh
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
```

### With uv

```sh
uv venv .venv
source .venv/bin/activate
uv pip install -e '.[dev]'
```

---

## Usage

### 1. Select Jupyter Connection Mode (Environment Variables)

Set these environment variables to control how the server connects to Jupyter:

- **MCP_JUPYTER_SESSION_MODE**: `server` (remote Jupyter, default) or `local` (local kernel)
- **MCP_JUPYTER_BASE_URL**: Jupyter server URL (required in `server` mode, e.g., `http://localhost:8888`)
- **MCP_JUPYTER_TOKEN**: Jupyter API token (required in `server` mode)
- **MCP_JUPYTER_KERNEL_NAME**: Kernel name (default: `python3`)
- **MCP_JUPYTER_NOTEBOOK_PATH**: Notebook file path (default: random, e.g., `mcp_<id>.ipynb`)
- **MCP_JUPYTER_NOTEBOOK_LOG_LEVEL**: Log level (default: `INFO`)

**Example:**
```sh
export MCP_JUPYTER_SESSION_MODE=server
export MCP_JUPYTER_BASE_URL=http://localhost:8888
export MCP_JUPYTER_TOKEN=ceb03195-18f5-4138-a24c-5bab7fecb97d
export MCP_JUPYTER_KERNEL_NAME=python3
export MCP_JUPYTER_NOTEBOOK_PATH=mcp_example.ipynb
```

### 2. Select Transport Mode (CLI Argument)

Choose how the MCP server exposes itself to clients:

- **stdio** (default): For local/desktop agent integration (recommended for most MCP clients)
- **sse**: For legacy web/SSE clients
- **streamable-http**: For HTTP API integration

Specify the transport with the `--transport` CLI argument:

```sh
mcp-jupyter-notebook --transport stdio           # (default, for local/desktop)
mcp-jupyter-notebook --transport sse             # (for legacy web/SSE)
mcp-jupyter-notebook --transport streamable-http # (for HTTP API)
```

You can also set host/port for HTTP/SSE modes:

```sh
mcp-jupyter-notebook --transport streamable-http --host 0.0.0.0 --port 8000
```

> **Note:**
> When running the MCP server with `uv` in stdio mode (the default transport), Ctrl+C may not always stop the server due to how `uv` manages process signals and stdio. Use Ctrl+D (EOF) or kill the process from another terminal if needed. For local development, running with `python -m mcp_jupyter_notebook.server` allows Ctrl+C to work as expected.

---

### 3. Launch the Server

After installation, you can launch the MCP Jupyter Notebook server from anywhere using the CLI entrypoint or as a Python module:

```sh
mcp-jupyter-notebook [--transport ...]
```

Or with uv:

```sh
uv run mcp-jupyter-notebook [--transport ...]
```

Or run directly as a module:

```sh
python -m mcp_jupyter_notebook.server [--transport ...]
```

---

### 4. Example MCP Client Configuration

To use with an MCP client (e.g., Claude Desktop, VS Code, etc.):

```json
{
    "mcpServers": {
        "jupyter": {
            "command": "uvx",
            "args": [ "mcp-jupyter-notebook", "--transport", "stdio"  ],
            "env": {
                "MCP_JUPYTER_SESSION_MODE": "server",
                "MCP_JUPYTER_BASE_URL": "http://localhost:8888",
                "MCP_JUPYTER_TOKEN": "<your-jupyter-token>",
                "MCP_JUPYTER_KERNEL_NAME": "python3",
                "MCP_JUPYTER_NOTEBOOK_PATH": "mcp_<id>.ipynb"
            }
        }
    }
}
```

**Note:** Do not reference a script path. Use the CLI entrypoint (`mcp-jupyter-notebook`) after installing the package.

---

## Release Process

To publish a new release to PyPI:

0. Install dev dependencies
    ```sh
    uv pip install -e ".[dev]"
    ``` 
1. Ensure all changes are committed and tests pass:
    ```sh
    uv run pytest tests/
    ```
2. Create and push an **annotated tag** for the release:
    ```sh
    git tag -a v0.1.0 -m "Release 0.1.0"
    git push origin v0.1.0
    ```
3. Checkout the tag to ensure you are building exactly from it:
    ```sh
    git checkout v0.1.0
    ```
4. Clean old build artifacts:
    ```sh
    rm -rf dist
    rm -rf build
    rm -rf src/*.egg-info
    ```
5. Upgrade build and upload tools:
    ```sh
    uv pip install --upgrade build twine packaging setuptools wheel setuptools_scm
    ```
6. Build the package:
    ```sh
    uv run python -m build
    ```
7. (Optional) Check metadata:
    ```sh
    uv run twine check dist/*
    ```
8. Upload to PyPI:
    ```sh
    uv run twine upload dist/*
    ```

**Notes:**
* Twine ≥ 6 and packaging ≥ 24.2 are required for modern metadata support.
* Always build from the tag (`git checkout vX.Y.Z`) so setuptools_scm resolves the exact version.
* `git checkout v0.1.0` puts you in detached HEAD mode; that’s normal. When done, return to your branch with:
    ```sh
    git switch -
    ```
* If you’re building in CI, make sure tags are fetched:
    ```sh
    git fetch --tags --force --prune
    git fetch --unshallow || true
    ```

---