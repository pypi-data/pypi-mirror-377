"""
Configuration module for Bitbucket MCP Server
Handles environment variables and application settings
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Bitbucket Configuration - can be set via environment or .env file
WORKSPACE = os.getenv("BITBUCKET_WORKSPACE", "busie")
REPO_SLUG = os.getenv("BITBUCKET_REPO", "fe-main")
BITBUCKET_USERNAME = os.getenv("BITBUCKET_USERNAME")
BITBUCKET_APP_PASSWORD = os.getenv("BITBUCKET_APP_PASSWORD")

# API Configuration
BASE_URL = "https://api.bitbucket.org/2.0"
DEFAULT_TIMEOUT = 30.0

# Server Configuration
SERVER_NAME = "bitbucket_mcp"
SERVER_INSTRUCTIONS = """An essential toolset for common Bitbucket workflows including pipelines, pull requests, and repository management"""
