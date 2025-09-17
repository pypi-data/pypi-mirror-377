"""
API Client module for Bitbucket MCP Server
Handles HTTP requests to Bitbucket API with authentication
"""

import httpx
from typing import Optional, Dict, Any
from .config import BASE_URL, DEFAULT_TIMEOUT
from .auth import get_auth_headers
from fastmcp.utilities.logging import get_logger

logger = get_logger(__name__)


async def make_request(method: str,
                       endpoint: str,
                       params: Optional[Dict] = None,
                       json_data: Optional[Dict] = None,
                       headers: Optional[Dict] = None,
                       accept_type: Optional[str] = None) -> Dict[str, Any]:
    """
    Make authenticated request to Bitbucket API
    
    Args:
        method: HTTP method (GET, POST, PUT, DELETE)
        endpoint: API endpoint path
        params: Query parameters
        json_data: JSON body data
        headers: Additional headers
        accept_type: Override Accept header for specific content types
        
    Returns:
        Dict containing response data
        
    Raises:
        httpx.HTTPStatusError: If request fails
    """
    url = f"{BASE_URL}/{endpoint}"
    auth_headers = get_auth_headers()

    # Override Accept header if specified (needed for pipeline logs)
    if accept_type:
        auth_headers["Accept"] = accept_type

    # Merge additional headers
    if headers:
        auth_headers.update(headers)

    # Create client with redirect following enabled (needed for diffstat)
    async with httpx.AsyncClient(follow_redirects=True) as client:
        response = await client.request(method=method,
                                        url=url,
                                        params=params,
                                        json=json_data,
                                        headers=auth_headers,
                                        timeout=DEFAULT_TIMEOUT)
        response.raise_for_status()

        content_type = response.headers.get("content-type", "")
        if content_type.startswith(("text/", "application/octet-stream")):

            return {"content": response.text}

        return response.json()
