#!/usr/bin/env python3
"""
Bitbucket Curated MCP Server
Main entry point that registers all tools and resources
Version: 1.0.0
"""

import asyncio
from typing import Literal, Annotated
from contextlib import asynccontextmanager
from fastmcp import FastMCP
from utils.config import SERVER_NAME, SERVER_INSTRUCTIONS, WORKSPACE, REPO_SLUG
from modules import tools, resources, meta_tools, prompts
from fastmcp.utilities.logging import get_logger

logger = get_logger(__name__)
from utils.api_client import make_request
from fastmcp import Context


# Application lifespan context manager
@asynccontextmanager
async def lifespan(app):
    # Startup: Register dynamic resources
    await resources.pipeline_resource_iterator(mcp)
    logger.info("Dynamic pipeline resources registered")

    await resources.pr_resource_iterator(mcp)
    logger.info("Dynamic PR resources registered")

    yield
    # Shutdown: Any cleanup if needed


# Initialize the MCP server with lifespan
mcp = FastMCP(SERVER_NAME, instructions=SERVER_INSTRUCTIONS, lifespan=lifespan)


# Register Pipeline Tools (5)
@mcp.tool(annotations={
    "title": "List Pipelines",
    "readOnlyHint": True,
    "category": "pipeline"
})
async def list_pipelines(
        created_on: Annotated[str, "Filter by creation date"] = "",
        sort: Annotated[str, "Sort order for results"] = "-created_on",
        creator_uuid: Annotated[str, "Filter by creator UUID"] = "",
        status: Annotated[Literal["SUCCESSFUL", "FAILED", "INPROGRESS",
                                  "STOPPED"],
                          "Filter by pipeline status"] = "FAILED",
        limit: Annotated[int, "Number of results to return"] = 10) -> dict:
    """List pipelines"""
    return await tools.list_pipelines(created_on, sort, creator_uuid, status,
                                      limit)


list_pipelines.disable()


@mcp.tool(annotations={
    "title": "Create Pipeline",
    "destructiveHint": False,
    "category": "pipeline"
})
async def create_pipeline(
        pipeline_config: Annotated[dict, "Pipeline configuration"]) -> dict:
    """Create pipeline"""
    return await tools.create_pipeline(pipeline_config)


create_pipeline.disable()


@mcp.tool(annotations={
    "title": "Get Pipeline Details",
    "readOnlyHint": True,
    "category": "pipeline"
})
async def get_pipeline(pipeline_uuid: Annotated[str, "Pipeline UUID"]) -> dict:
    """Get pipeline details"""
    return await tools.get_pipeline(pipeline_uuid)


@mcp.tool(annotations={
    "title": "Get Pipeline Steps",
    "readOnlyHint": True,
    "category": "pipeline"
})
async def list_pipeline_steps(
        pipeline_uuid: Annotated[str, "Pipeline UUID"]) -> dict:
    """Get pipeline steps"""
    return await tools.list_pipeline_steps(pipeline_uuid)


@mcp.tool(
    annotations={
        "title": "Get Pipeline Step Logs",
        "readOnlyHint": True,
        "category": "pipeline"
    })
async def get_pipeline_step_logs(
    pipeline_uuid: Annotated[str, "Pipeline UUID"],
    step_uuid: Annotated[str, "Step UUID"],
    range_header: Annotated[str, "HTTP Range header for partial logs"] = None
) -> str:
    """Get step logs"""
    return await tools.get_pipeline_step_logs(pipeline_uuid, step_uuid,
                                              range_header)


# Register Pull Request Tools (9)
@mcp.tool(annotations={
    "title": "List Pull Requests",
    "readOnlyHint": True,
    "category": "pr"
})
async def list_pull_requests(
        state: Annotated[Literal["OPEN", "MERGED", "DECLINED", "SUPERSEDED"],
                         "Filter by PR state"] = None,
        limit: Annotated[int, "Number of results to return"] = 10,
        sort: Annotated[str, "Sort order for results"] = None) -> dict:
    """List pull requests"""
    return await tools.list_pull_requests(state, limit, sort)


list_pull_requests.disable()


@mcp.tool(
    annotations={
        "title": "Create Pull Request",
        "destructiveHint": False,
        "category": "pr",
        "help": "Reviewers: UUIDs from workspace-members resource"
    })
async def create_pull_request(
    title: Annotated[str, "PR title"],
    source_branch: Annotated[str, "Source branch name"],
    destination_branch: Annotated[str,
                                  "Target branch (defaults to main)"] = None,
    description: Annotated[str, "PR description"] = None,
    reviewers: Annotated[list, "List of reviewer UUIDs"] = [],
    close_source_branch: Annotated[bool,
                                   "Delete source branch after merge"] = False,
    state: Annotated[Literal["OPEN", "DRAFT"], "Initial PR state"] = "OPEN"
) -> dict:
    """Create pull request"""
    return await tools.create_pull_request(title, source_branch,
                                           destination_branch, description,
                                           reviewers, close_source_branch,
                                           state)


@mcp.tool(annotations={
    "title": "Get Pull Request Details",
    "readOnlyHint": True,
    "category": "pr"
})
async def get_pull_request(pull_request_id: Annotated[int, "PR ID"]) -> dict:
    """Get PR details"""
    return await tools.get_pull_request(pull_request_id)


@mcp.tool(annotations={
    "title": "Update Pull Request",
    "destructiveHint": False,
    "category": "pr"
})
async def update_pull_request(
        pull_request_id: Annotated[int, "PR ID to update"],
        update_data: Annotated[dict, "Fields to update"]) -> dict:
    """Update PR"""
    return await tools.update_pull_request(pull_request_id, update_data)


@mcp.tool(annotations={
    "title": "List PR Comments",
    "readOnlyHint": True,
    "category": "pr"
})
async def list_pr_comments(pull_request_id: Annotated[int, "PR ID"]) -> dict:
    """List PR comments"""
    return await tools.list_pr_comments(pull_request_id)


@mcp.tool(annotations={
    "title": "Create PR Comment",
    "destructiveHint": False,
    "category": "pr"
})
async def create_pr_comment(
        pull_request_id: Annotated[int, "PR ID"],
        content: Annotated[str, "Comment content"]) -> dict:
    """Create PR comment"""
    return await tools.create_pr_comment(pull_request_id, content)


@mcp.tool(annotations={
    "title": "Get PR File Changes",
    "readOnlyHint": True,
    "category": "pr"
})
async def get_pr_changes(pull_request_id: Annotated[int, "PR ID"]) -> dict:
    """List PR changes"""
    return await tools.get_pr_changes(pull_request_id)


@mcp.tool(annotations={
    "title": "Get PR Diff Statistics",
    "readOnlyHint": True,
    "category": "pr"
})
async def get_pr_diffstat(pull_request_id: Annotated[int, "PR ID"]) -> dict:
    """Get PR diffstat"""
    return await tools.get_pr_diffstat(pull_request_id)


@mcp.tool(annotations={
    "title": "List PR Tasks",
    "readOnlyHint": True,
    "category": "pr"
})
async def list_pr_tasks(pull_request_id: Annotated[int, "PR ID"]) -> dict:
    """List PR tasks"""
    return await tools.list_pr_tasks(pull_request_id)


# Register PR Task Tools (2)
@mcp.tool(annotations={
    "title": "Create PR Task",
    "destructiveHint": False,
    "category": "pr"
})
async def create_pr_task(
        pull_request_id: Annotated[int, "PR ID"],
        task_data: Annotated[dict, "Task definition"]) -> dict:
    """Create PR task"""
    return await tools.create_pr_task(pull_request_id, task_data)


@mcp.tool(annotations={
    "title": "Update PR Task",
    "destructiveHint": False,
    "category": "pr"
})
async def update_pr_task(
        pull_request_id: Annotated[int,
                                   "PR ID"], task_id: Annotated[int,
                                                                "Task ID"],
        task_data: Annotated[dict, "Updated task data"]) -> dict:
    """Update PR task"""
    return await tools.update_pr_task(pull_request_id, task_id, task_data)


# Register Repository Tools (1)
@mcp.tool(
    annotations={
        "title": "Get Repository Information",
        "readOnlyHint": True,
        "category": "repository"
    })
async def get_repository() -> dict:
    """Get repository info"""
    return await tools.get_repository()


# Register Workspace Tools (6)
@mcp.tool()
async def list_workspace_repos(workspace: str, role: str = None) -> dict:
    """List repositories in a workspace"""
    return await tools.list_workspace_repos(workspace, role)


@mcp.tool()
async def get_workspace(workspace: str) -> dict:
    """Get details of a workspace"""
    return await tools.get_workspace(workspace)


@mcp.tool()
async def list_workspace_members(workspace: str) -> dict:
    """List users in a workspace"""
    return await tools.list_workspace_members(workspace)


@mcp.tool(
    annotations={
        "title": "List Workspace Projects",
        "readOnlyHint": True,
        "category": "workspace",
        "workspace": "busie"
    })
async def list_workspace_projects(
        workspace: Annotated[str, "Workspace name"]) -> dict:
    """List workspace projects"""
    return await tools.list_workspace_projects(workspace)


list_workspace_projects.disable()


@mcp.tool()
async def list_workspace_prs(workspace: str, query: str = None) -> dict:
    """List all pull requests in a workspace, filterable by query"""
    return await tools.list_workspace_prs(workspace, query)


@mcp.tool()
async def list_project_default_reviewers(workspace: str,
                                         project_key: str) -> dict:
    """List default reviewers for a project"""
    return await tools.list_project_default_reviewers(workspace, project_key)


# Register User Tools (2)
@mcp.tool()
async def get_current_user() -> dict:
    """Get information about the authenticated user"""
    return await tools.get_current_user()


@mcp.tool()
async def get_user(username: str) -> dict:
    """Get information about a specific user"""
    return await tools.get_user(username)


# Register Meta-Tools (3) - High-level workflow composition tools
@mcp.tool(annotations={
    "title": "Analyze Pipeline Failures",
    "readOnlyHint": True,
    "category": "meta-workflow",
    "repository": "busie/fe-main",
    "help": "Combines multiple pipeline tools for failure analysis"
},
          meta={
              "version": "1.0.0",
              "category": "meta-tools",
              "workflow": "pipeline-analysis"
          })
async def analyze_pipeline_failure(
    pipeline_uuid: Annotated[str,
                             "Pipeline UUID (auto-detects if omitted)"] = None
) -> dict:
    """Analyze pipeline failures"""
    return await meta_tools.analyze_pipeline_failure(pipeline_uuid)


@mcp.tool(annotations={
    "title": "Complete PR Review",
    "readOnlyHint": True,
    "category": "meta-workflow",
    "repository": "busie/fe-main",
    "help": "Combines multiple PR tools for comprehensive review"
},
          meta={
              "version": "1.0.0",
              "category": "meta-tools",
              "workflow": "pr-review"
          })
async def review_pull_request(
        pull_request_id: Annotated[int, "PR ID to review"]) -> dict:
    """Review pull request"""
    return await meta_tools.review_pull_request(pull_request_id)


@mcp.tool(annotations={
    "title":
    "Workspace Overview",
    "readOnlyHint":
    True,
    "category":
    "meta-workflow",
    "workspace":
    "busie",
    "help":
    "Combines multiple workspace tools for comprehensive overview"
},
          meta={
              "version": "1.0.0",
              "category": "meta-tools",
              "workflow": "workspace-overview"
          })
async def workspace_overview(
    workspace: Annotated[str,
                         "Workspace name (uses default if omitted)"] = None
) -> dict:
    """Workspace overview"""
    return await meta_tools.workspace_overview(workspace)


# Register Resources (6)
@mcp.resource(f"bitbucket://{WORKSPACE}/{REPO_SLUG}/info",
              name="Repository Information",
              description="Current repository configuration and metadata")
async def get_repository_info() -> dict:
    """Repository info"""
    return await resources.get_repository_info()


@mcp.resource(f"bitbucket://{WORKSPACE}/{REPO_SLUG}/recent-pipelines",
              name="Recent Pipelines",
              description="Recent pipeline runs with status")
async def get_recent_pipelines() -> dict:
    """Recent pipelines"""
    return await resources.get_recent_pipelines()


@mcp.resource(f"bitbucket://{WORKSPACE}/{REPO_SLUG}/open-prs",
              name="Open Pull Requests",
              description="Currently open pull requests")
async def get_open_prs() -> dict:
    """Open pull requests"""
    return await resources.get_open_prs()


# Register Workspace Data Resources (3) - Helper resources for tool parameters
@mcp.resource(f"bitbucket://{WORKSPACE}/workspace-members")
async def get_workspace_members() -> dict:
    """Available reviewers"""
    return await resources.get_workspace_members()


@mcp.resource(f"bitbucket://{WORKSPACE}/{REPO_SLUG}/branches")
async def get_repository_branches() -> dict:
    """Available branches"""
    return await resources.get_repository_branches()


@mcp.resource(f"bitbucket://{WORKSPACE}/workspace-projects")
async def get_workspace_projects_with_reviewers() -> dict:
    """Projects with reviewers"""
    return await resources.get_workspace_projects_with_reviewers()


@mcp.resource(
    "bitbucket://common-patterns",
    name="Common Usage Patterns",
    description="Workflow examples and best practices for using Bitbucket tools"
)
async def get_common_patterns() -> dict:
    """Usage patterns"""
    return await resources.get_common_patterns()


# Register Custom Prompts
@mcp.prompt
async def commit_push_and_create_pr(ctx: Context) -> str:
    """Generates a prompt to commit all changes, push to remote, and create a PR. Includes default reviewers."""
    return await prompts.commit_push_and_create_pr(ctx)


@mcp.prompt
async def create_markdown_from_latest_failed_pipeline(ctx: Context) -> str:
    """Generates a prompt based on data that needs to be fetched."""
    return await prompts.create_markdown_from_latest_failed_pipeline(ctx)


# Disable tools that shouldn't be exposed to LLM
get_current_user.disable()
list_project_default_reviewers.disable()
list_workspace_prs.disable()
get_user.disable()
list_workspace_members.disable()
get_workspace.disable()
list_workspace_repos.disable()
create_pipeline.disable()


def main():
    """Entry point for the application."""
    mcp.run()


if __name__ == "__main__":
    main()
