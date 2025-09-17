from fastmcp.server.middleware import Middleware, MiddlewareContext
from utils.api_client import make_request
from fastmcp.utilities.logging import get_logger

logger = get_logger(__name__)

class LoggingMiddleware(Middleware):
    """Middleware that logs all MCP operations."""

    async def on_message(self, context: MiddlewareContext, call_next):
        """Called for all MCP messages."""
        logger.info(f"Processing {context.method} from {context.source}")
        user = await make_request(
            "GET",
            "user",
            headers={"Accept": "application/json"}
        )
        pipelines = await make_request(
            "GET",
            f"repositories/busie/fe-main/pipelines/",
            params={"sort": "-created_on", "pagelen": 1}
        )
        result = await call_next(context)
        context.fastmcp_context.set_state("user_id", user["uuid"] if user else "unknown")
        logger.info(f"Completed {context.method}")
        return result

# Note: mcp.add_middleware(LoggingMiddleware()) should be called in server.py
