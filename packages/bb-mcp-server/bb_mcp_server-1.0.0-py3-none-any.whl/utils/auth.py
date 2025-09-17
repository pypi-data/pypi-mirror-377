"""
Authentication module for Bitbucket MCP Server
Handles Basic Authentication for Bitbucket API
"""

from base64 import b64encode
from typing import Dict
from .config import BITBUCKET_USERNAME, BITBUCKET_APP_PASSWORD


def get_auth_headers() -> Dict[str, str]:
    """
    Generate Basic Auth headers for Bitbucket API
    
    Returns:
        Dict containing Authorization and Content-Type headers
        
    Raises:
        ValueError: If required environment variables are not set
    """
    if not BITBUCKET_USERNAME or not BITBUCKET_APP_PASSWORD:
        raise ValueError(
            "BITBUCKET_USERNAME and BITBUCKET_APP_PASSWORD environment variables must be set"
        )
    
    credentials = f"{BITBUCKET_USERNAME}:{BITBUCKET_APP_PASSWORD}"
    encoded = b64encode(credentials.encode()).decode('ascii')
    
    return {
        "Authorization": f"Basic {encoded}",
        "Accept": "application/json",
        "Content-Type": "application/json"
    }