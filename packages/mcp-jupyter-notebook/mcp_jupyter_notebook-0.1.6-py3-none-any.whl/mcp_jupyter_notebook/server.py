from __future__ import annotations

import argparse
import asyncio
import json
import logging
import os
import signal
import uuid
from contextlib import asynccontextmanager, suppress
from typing import Dict

import uvicorn
from fastmcp import FastMCP
from starlette.applications import Starlette
from starlette.responses import Response
from starlette.routing import Mount, Route
from mcp_jupyter_notebook.tools import register_all_tools

from jupyter_agent_toolkit.notebook import NotebookSession
from jupyter_agent_toolkit.utils import create_kernel, create_notebook_transport


def _init_logging() -> logging.Logger:
    """Initialize logging from env."""
    level = getattr(
        logging,
        os.getenv("MCP_JUPYTER_NOTEBOOK_LOG_LEVEL", "INFO").upper(),
        logging.INFO,
    )
    logging.basicConfig(
        level=level, format="%(asctime)s %(levelname)s %(name)s: %(message)s"
    )
    return logging.getLogger("mcp-jupyter")


log = _init_logging()


# ───────────────────── headers / env parsing ─────────────────────


def _parse_headers_env(var: str = "MCP_JUPYTER_HEADERS_JSON") -> Dict[str, str]:
    """Optional extra headers (Cookie/XSRF) as a JSON object."""
    raw = os.getenv(var)
    if not raw:
        return {}
    try:
        h = json.loads(raw)
        if not isinstance(h, dict):
            raise ValueError("headers JSON must be an object")
        return {str(k): str(v) for k, v in h.items()}
    except Exception as e:
        log.warning("Ignoring invalid %s: %s", var, e)
        return {}


# ────────────────────── session construction ──────────────────────


def _make_session_from_env() -> NotebookSession:
    """
    Build a NotebookSession from env in modern toolkit style.

    Modes:
      - server (remote Jupyter): remote kernel + collab transport
      - local: local kernel + local transport
    """
    mode = os.getenv("MCP_JUPYTER_SESSION_MODE", "server").lower()
    kernel_name = os.getenv("MCP_JUPYTER_KERNEL_NAME", "python3")
    notebook_path = (
        os.getenv("MCP_JUPYTER_NOTEBOOK_PATH") or f"mcp_{uuid.uuid4().hex[:8]}.ipynb"
    )

    if mode == "server":
        base_url = os.getenv("MCP_JUPYTER_BASE_URL")
        if not base_url:
            raise RuntimeError("MCP_JUPYTER_BASE_URL is required in server mode")
        token = os.getenv("MCP_JUPYTER_TOKEN")
        headers = _parse_headers_env()

        kernel = create_kernel(
            "remote",
            base_url=base_url,
            token=token,
            headers=headers or None,
            kernel_name=kernel_name,
        )
        doc = create_notebook_transport(
            "remote",
            notebook_path,
            base_url=base_url,
            token=token,
            headers=headers or None,
            prefer_collab=True,
            create_if_missing=True,
        )
        return NotebookSession(kernel=kernel, doc=doc)

    # local mode
    kernel = create_kernel("local", kernel_name=kernel_name)
    doc = create_notebook_transport(
        "local",
        notebook_path,
        prefer_collab=False,
        create_if_missing=True,
    )
    return NotebookSession(kernel=kernel, doc=doc)


# ───────────────────────── MCP server core ─────────────────────────


def get_server_and_session():
    """Create the FastMCP server and NotebookSession, and register tools."""
    server = FastMCP("mcp-jupyter")
    session: NotebookSession = _make_session_from_env()
    register_all_tools(server, session)
    return server, session



async def _graceful_stop(session=None) -> None:
    """Close collab websocket, kernel, and underlying clients safely."""
    try:
        if session:
            await session.stop()
            log.info("NotebookSession stopped.")
    except Exception as e:
        log.warning("Error during shutdown: %s", e)


# ──────────────────────── stdio transport ─────────────────────────



def run_stdio() -> None:
    log.info("Starting MCP in stdio mode.")
    server, session = get_server_and_session()
    # Optional: best-effort signal logging on Unix (no loop control here)
    with suppress(Exception):
        loop = asyncio.get_event_loop()
        for sig in (signal.SIGINT, signal.SIGTERM):
            with suppress(NotImplementedError):
                loop.add_signal_handler(
                    sig, lambda s=sig: log.info("Received signal %s", s)
                )
    try:
        server.run("stdio")  # blocking until EOF / Ctrl-C
    except KeyboardInterrupt:
        log.info("Interrupted by user.")
    finally:
        asyncio.run(_graceful_stop(session))


# ────────────────────────── SSE transport ──────────────────────────


def run_sse(host: str = "127.0.0.1", port: int = 8000) -> None:
    """
    SSE endpoint at /sse and POST message endpoint mounted by SseServerTransport.
    """
    log.info("Starting MCP in SSE mode on http://%s:%d", host, port)
    from mcp.server.sse import SseServerTransport  # lazy import

    server, _ = get_server_and_session()
    sse = SseServerTransport("/messages/")

    async def handle_sse(request):
        log.info("🔌 SSE connection established")
        async with sse.connect_sse(request.scope, request.receive, request._send) as (
            read_stream,
            write_stream,
        ):
            await server._mcp_server.run(
                read_stream,
                write_stream,
                server._mcp_server.create_initialization_options(),
            )
        return Response(status_code=200)

    app = Starlette(
        debug=False,
        routes=[
            Route("/sse", endpoint=handle_sse),
            Mount("/messages/", app=sse.handle_post_message),
        ],
    )

    try:
        uvicorn.run(app, host=host, port=port, log_level="info")
    finally:
        asyncio.run(_graceful_stop())


# ─────────────────── streamable HTTP transport ────────────────────


def run_streamable_http(
    host: str = "127.0.0.1",
    port: int = 8000,
    *,
    stateless: bool = False,
    json_response: bool = False,
) -> None:
    """
    Streamable HTTP transport at /mcp.
    - stateless: each request is isolated (no server-side session state)
    - json_response: return JSON envelopes instead of SSE
    """
    log.info(
        "Starting MCP in streamable HTTP mode at http://%s:%d (stateless=%s json_response=%s)",
        host,
        port,
        stateless,
        json_response,
    )
    from mcp.server.streamable_http_manager import (
        StreamableHTTPSessionManager,  # lazy import
    )

    server, _ = get_server_and_session()
    mgr = StreamableHTTPSessionManager(
        server._mcp_server,
        event_store=None,  # resumability removed
        json_response=json_response,
        stateless=stateless,
    )

    async def handle_streamable_http(scope, receive, send):
        log.info("🔌 Streamable HTTP request")
        await mgr.handle_request(scope, receive, send)

    app = Starlette(
        debug=False,
        routes=[Mount("/mcp", app=handle_streamable_http)],
    )

    @asynccontextmanager
    async def _lifespan():
        async with mgr.run():
            try:
                yield
            finally:
                await _graceful_stop()

    async def _serve():
        async with _lifespan():
            config = uvicorn.Config(app, host=host, port=port, log_level="info")
            srv = uvicorn.Server(config)
            await srv.serve()

    asyncio.run(_serve())


# ─────────────────────────── CLI & entry ───────────────────────────


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Run the MCP Jupyter server.")
    p.add_argument(
        "--transport", choices=["stdio", "sse", "streamable-http"], default="stdio"
    )

    p.add_argument("--host", default=os.getenv("MCP_HTTP_HOST", "127.0.0.1"))
    p.add_argument("--port", type=int, default=int(os.getenv("MCP_HTTP_PORT", "8000")))
    p.add_argument(
        "--stateless",
        action="store_true",
        default=False,
        help="Streamable HTTP: stateless mode",
    )
    p.add_argument(
        "--json-response",
        action="store_true",
        default=False,
        help="Streamable HTTP: JSON envelopes",
    )
    return p.parse_args()


def main() -> None:
    log.info(
        "mcp-jupyter launching… mode=%s",
        os.getenv("MCP_JUPYTER_SESSION_MODE", "server"),
    )
    args = _parse_args()
    if args.transport == "stdio":
        run_stdio()
    elif args.transport == "sse":
        run_sse(host=args.host, port=args.port)
    elif args.transport == "streamable-http":
        run_streamable_http(
            host=args.host,
            port=args.port,
            stateless=args.stateless,
            json_response=args.json_response,
        )
    else:
        raise SystemExit(f"Unknown transport: {args.transport}")


if __name__ == "__main__":
    main()
