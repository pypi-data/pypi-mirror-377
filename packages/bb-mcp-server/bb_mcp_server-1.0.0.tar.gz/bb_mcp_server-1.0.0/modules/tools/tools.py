"""
Tool definitions for Bitbucket MCP Server
Contains all 26 tool functions for interacting with Bitbucket API
"""

from typing import Literal
from utils.config import WORKSPACE, REPO_SLUG
from utils.api_client import make_request


# Pipeline Operations (5 tools)

async def list_pipelines(created_on: str | None = "", sort: str | None = "-created_on", creator_uuid: str | None = "", status: Literal["SUCCESSFUL", "FAILED", "INPROGRESS", "STOPPED"] = "FAILED", limit: int = 10) -> dict:
    """List pipelines for busie/fe-main repository with filtering options"""
    params = {}
    # Filter out None and empty string values
    if created_on and created_on.strip():
        params["created_on"] = created_on
    if sort and sort.strip():
        params["sort"] = sort
    if creator_uuid and creator_uuid.strip():
        params["creator.uuid"] = creator_uuid
    if status and status.strip():
        params["status.name"] = status
    if limit and limit > 0:
        params["pagelen"] = limit
    
    return await make_request(
        "GET",
        f"repositories/{WORKSPACE}/{REPO_SLUG}/pipelines",
        params=params
    )


async def create_pipeline(pipeline_config: dict) -> dict:
    """Create a new pipeline for busie/fe-main repository"""
    return await make_request(
        "POST",
        f"repositories/{WORKSPACE}/{REPO_SLUG}/pipelines",
        json_data=pipeline_config
    )


async def get_pipeline(pipeline_uuid: str) -> dict:
    """Get details of a specific pipeline"""
    return await make_request(
        "GET",
        f"repositories/{WORKSPACE}/{REPO_SLUG}/pipelines/{pipeline_uuid}"
    )


async def list_pipeline_steps(pipeline_uuid: str) -> dict:
    """Get steps for a specific pipeline"""
    return await make_request(
        "GET",
        f"repositories/{WORKSPACE}/{REPO_SLUG}/pipelines/{pipeline_uuid}/steps"
    )


async def get_pipeline_step_logs(pipeline_uuid: str, step_uuid: str, range_header: str | None = None) -> str:
    """Get logs for a specific pipeline step, supports Range requests"""
    headers = {}
    # Filter out None and empty string values
    if range_header and range_header.strip():
        headers["Range"] = range_header
    
    result = await make_request(
        "GET",
        f"repositories/{WORKSPACE}/{REPO_SLUG}/pipelines/{pipeline_uuid}/steps/{step_uuid}/log",
        headers=headers,
        accept_type="application/octet-stream"
    )
    return result.get("content", "")


# Pull Request Operations (9 tools)

async def list_pull_requests(state: Literal["OPEN", "MERGED", "DECLINED", "SUPERSEDED", None] | None = None, limit: int = 10, sort: str | None = None) -> dict:
    """List pull requests for busie/fe-main repository"""
    params = {}
    # Always include limit if it's a valid positive integer
    if limit and limit > 0:
        params["pagelen"] = limit
    # Filter out None and empty string values for optional params
    if state and state.strip():
        params["state"] = state
    if sort and sort.strip():
        params["sort"] = sort
    
    return await make_request(
        "GET",
        f"repositories/{WORKSPACE}/{REPO_SLUG}/pullrequests",
        params=params
    )


async def create_pull_request(
    title: str, 
    source_branch: str, 
    destination_branch: str | None = None, 
    description: str | None = None, 
    reviewers: list = [], 
    close_source_branch: bool = False, 
    state: Literal["OPEN", "DRAFT"] = "OPEN"
) -> dict:
    """Create a new pull request in busie/fe-main repository
    
    Args:
        reviewers: List of reviewer UUIDs (e.g., ["{f9d7e044-a0b9-41e4-be3e-a8be9512ae95}"])
                   Query bitbucket://busie/workspace-members resource to get valid UUIDs
    """
    pr_data = {
        "title": title,
        "source": {
            "branch": {"name": source_branch},
            "repository": {"full_name": f"{WORKSPACE}/{REPO_SLUG}"}
        },
        "destination": {
            "branch": {"name": destination_branch or "main"}
        },
        "close_source_branch": close_source_branch
    }
    
    # Filter out None and empty values for optional fields
    if description and description.strip():
        pr_data["description"] = description
    if reviewers and len(reviewers) > 0:
        pr_data["reviewers"] = [{"uuid": r} for r in reviewers if r and r.strip()]
    if state and state.strip() and state != "OPEN":  # OPEN is default, only set if different
        pr_data["state"] = state
    
    return await make_request(
        "POST",
        f"repositories/{WORKSPACE}/{REPO_SLUG}/pullrequests",
        json_data=pr_data
    )


async def get_pull_request(pull_request_id: int) -> dict:
    """Get details of a specific pull request"""
    return await make_request(
        "GET",
        f"repositories/{WORKSPACE}/{REPO_SLUG}/pullrequests/{pull_request_id}"
    )


async def update_pull_request(pull_request_id: int, update_data: dict) -> dict:
    """Update an existing pull request"""
    return await make_request(
        "PUT",
        f"repositories/{WORKSPACE}/{REPO_SLUG}/pullrequests/{pull_request_id}",
        json_data=update_data
    )


async def list_pr_comments(pull_request_id: int) -> dict:
    """List comments on a pull request"""
    return await make_request(
        "GET",
        f"repositories/{WORKSPACE}/{REPO_SLUG}/pullrequests/{pull_request_id}/comments"
    )


async def create_pr_comment(pull_request_id: int, content: str) -> dict:
    """Create a comment on a pull request"""
    return await make_request(
        "POST",
        f"repositories/{WORKSPACE}/{REPO_SLUG}/pullrequests/{pull_request_id}/comments",
        json_data={"content": {"raw": content}}
    )


async def get_pr_changes(pull_request_id: int) -> dict:
    """List file changes in a pull request"""
    return await make_request(
        "GET",
        f"repositories/{WORKSPACE}/{REPO_SLUG}/pullrequests/{pull_request_id}/diff"
    )


async def get_pr_diffstat(pull_request_id: int) -> dict:
    """Get the diffstat for a pull request"""
    return await make_request(
        "GET",
        f"repositories/{WORKSPACE}/{REPO_SLUG}/pullrequests/{pull_request_id}/diffstat"
    )


async def list_pr_tasks(pull_request_id: int) -> dict:
    """List tasks on a pull request"""
    return await make_request(
        "GET",
        f"repositories/{WORKSPACE}/{REPO_SLUG}/pullrequests/{pull_request_id}/tasks"
    )


# PR Task Operations (2 tools)

async def create_pr_task(pull_request_id: int, task_data: dict) -> dict:
    """Create a task on a pull request"""
    return await make_request(
        "POST",
        f"repositories/{WORKSPACE}/{REPO_SLUG}/pullrequests/{pull_request_id}/tasks",
        json_data=task_data
    )


async def update_pr_task(pull_request_id: int, task_id: int, task_data: dict) -> dict:
    """Update a task on a pull request"""
    return await make_request(
        "PUT",
        f"repositories/{WORKSPACE}/{REPO_SLUG}/pullrequests/{pull_request_id}/tasks/{task_id}",
        json_data=task_data
    )


# Repository Operations (1 tool)

async def get_repository() -> dict:
    """Get details of busie/fe-main repository"""
    return await make_request(
        "GET",
        f"repositories/{WORKSPACE}/{REPO_SLUG}"
    )


# Workspace Operations (6 tools)

async def list_workspace_repos(workspace: str, role: str | None = None) -> dict:
    """List repositories in a workspace"""
    params = {}
    # Filter out None and empty string values
    if role and role.strip():
        params["role"] = role
    
    return await make_request(
        "GET",
        f"repositories/{workspace}",
        params=params
    )


async def get_workspace(workspace: str) -> dict:
    """Get details of a workspace"""
    return await make_request(
        "GET",
        f"workspaces/{workspace}"
    )


async def list_workspace_members(workspace: str) -> dict:
    """List users in a workspace"""
    return await make_request(
        "GET",
        f"workspaces/{workspace}/members"
    )


async def list_workspace_projects(workspace: str) -> dict:
    """List projects in a workspace"""
    return await make_request(
        "GET",
        f"workspaces/{workspace}/projects"
    )


async def list_workspace_prs(workspace: str, query: str | None = None) -> dict:
    """List all pull requests in a workspace, filterable by query"""
    params = {}
    # Filter out None and empty string values
    if query and query.strip():
        params["q"] = query
    
    return await make_request(
        "GET",
        f"pullrequests/{workspace}",
        params=params
    )


async def list_project_default_reviewers(workspace: str, project_key: str) -> dict:
    """List default reviewers for a repository (project_key is used as repo name)"""
    return await make_request(
        "GET",
        f"repositories/{workspace}/{project_key}/default-reviewers"
    )


# User Operations (2 tools)

async def get_current_user() -> dict:
    """Get information about the authenticated user"""
    return await make_request(
        "GET",
        "user"
    )


async def get_user(username: str) -> dict:
    """Get information about a specific user"""
    return await make_request(
        "GET",
        f"users/{username}"
    )
