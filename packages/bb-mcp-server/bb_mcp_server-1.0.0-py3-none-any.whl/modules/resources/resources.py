"""
Resource definitions for Bitbucket MCP Server
Contains all 3 resource functions for accessing common Bitbucket data
"""

from utils.config import WORKSPACE, REPO_SLUG
from utils.api_client import make_request
from modules import tools
from fastmcp.utilities.logging import get_logger

logger = get_logger(__name__)


async def get_repository_info() -> dict:
    """Current repository information and configuration"""
    try:
        repo_data = await make_request(
            "GET", f"repositories/{WORKSPACE}/{REPO_SLUG}")
        return {
            "uri": f"bitbucket://{WORKSPACE}/{REPO_SLUG}/info",
            "mimeType": "application/json",
            "data": repo_data
        }
    except Exception as e:
        return {
            "uri": f"bitbucket://{WORKSPACE}/{REPO_SLUG}/info",
            "mimeType": "application/json",
            "data": {
                "error": str(e)
            }
        }


async def get_recent_pipelines() -> dict:
    """List of recent pipeline runs with their status"""
    try:
        pipelines = await make_request(
            "GET",
            f"repositories/{WORKSPACE}/{REPO_SLUG}/pipelines",
            params={
                "pagelen": 10,
                "sort": "-created_on"
            })
        return {
            "uri": f"bitbucket://{WORKSPACE}/{REPO_SLUG}/recent-pipelines",
            "mimeType": "application/json",
            "data": pipelines
        }
    except Exception as e:
        return {
            "uri": f"bitbucket://{WORKSPACE}/{REPO_SLUG}/recent-pipelines",
            "mimeType": "application/json",
            "data": {
                "error": str(e)
            }
        }


async def get_open_prs() -> dict:
    """List of currently open pull requests"""
    try:
        prs = await make_request(
            "GET",
            f"repositories/{WORKSPACE}/{REPO_SLUG}/pullrequests",
            params={
                "state": "OPEN",
                "pagelen": 20
            })
        return {
            "uri": f"bitbucket://{WORKSPACE}/{REPO_SLUG}/open-prs",
            "mimeType": "application/json",
            "data": prs
        }
    except Exception as e:
        return {
            "uri": f"bitbucket://{WORKSPACE}/{REPO_SLUG}/open-prs",
            "mimeType": "application/json",
            "data": {
                "error": str(e)
            }
        }


async def get_workspace_members() -> dict:
    """List of workspace members available as reviewers (from repository default reviewers)"""
    try:
        # Use repository default reviewers as the source since workspace members might be empty
        default_reviewers = await make_request(
            "GET", f"repositories/{WORKSPACE}/{REPO_SLUG}/default-reviewers")

        # Also try to get workspace members as backup
        workspace_members = []
        try:
            members_response = await make_request(
                "GET", f"workspaces/{WORKSPACE}/members")
            workspace_members = members_response.get("values", [])
        except Exception:
            # If workspace members fails, we'll just use default reviewers
            pass

        # Combine default reviewers (primary) with workspace members (backup)
        simplified = []
        seen_accounts = set()

        # First add default reviewers
        for reviewer in default_reviewers.get("values", []):
            account_id = reviewer.get("account_id", "")
            uuid = reviewer.get("uuid", "")
            if account_id and account_id not in seen_accounts:
                simplified.append({
                    "username":
                    reviewer.get("nickname", ""),
                    "display_name":
                    reviewer.get("display_name", ""),
                    "account_id":
                    account_id,
                    "uuid":
                    uuid,  # Include UUID for API calls
                    "source":
                    "default_reviewer"
                })
                seen_accounts.add(account_id)

        # Then add any additional workspace members not already included
        for member in workspace_members:
            account_id = member.get("account_id", "")
            uuid = member.get("uuid", "")
            if account_id and account_id not in seen_accounts:
                member_data = {
                    "username": member.get("nickname", ""),
                    "display_name": member.get("display_name", ""),
                    "account_id": account_id,
                    "uuid": uuid,  # Include UUID for API calls
                    "source": "workspace_member"
                }
                # Only include if we have at least username or display_name
                if member_data["username"] or member_data["display_name"]:
                    simplified.append(member_data)
                    seen_accounts.add(account_id)

        return {
            "uri": f"bitbucket://{WORKSPACE}/workspace-members",
            "mimeType": "application/json",
            "data": {
                "members": simplified,
                "count": len(simplified),
                "sources":
                ["repository_default_reviewers", "workspace_members"]
            }
        }
    except Exception as e:
        return {
            "uri": f"bitbucket://{WORKSPACE}/workspace-members",
            "mimeType": "application/json",
            "data": {
                "error": str(e)
            }
        }


async def get_repository_branches() -> dict:
    """List of available branches in the repository"""
    try:
        branches = await make_request(
            "GET",
            f"repositories/{WORKSPACE}/{REPO_SLUG}/refs/branches",
            params={"pagelen": 50}  # Get more branches than default
        )
        # Simplify branch data for easier consumption
        simplified = []
        for branch in branches.get("values", []):
            branch_data = {
                "name":
                branch.get("name", ""),
                "target_hash":
                branch.get("target", {}).get("hash", "")[:8],
                "last_commit_date":
                branch.get("target", {}).get("date"),
                "author":
                branch.get("target", {}).get("author",
                                             {}).get("user",
                                                     {}).get("display_name")
            }
            # Only include branches with names
            if branch_data["name"]:
                simplified.append(branch_data)

        return {
            "uri": f"bitbucket://{WORKSPACE}/{REPO_SLUG}/branches",
            "mimeType": "application/json",
            "data": {
                "branches": simplified,
                "count": len(simplified),
                "repository": f"{WORKSPACE}/{REPO_SLUG}"
            }
        }
    except Exception as e:
        return {
            "uri": f"bitbucket://{WORKSPACE}/{REPO_SLUG}/branches",
            "mimeType": "application/json",
            "data": {
                "error": str(e)
            }
        }


async def get_workspace_projects_with_reviewers() -> dict:
    """List of workspace projects with their default reviewers"""
    try:
        projects = await make_request("GET",
                                      f"workspaces/{WORKSPACE}/projects")

        # For each project, try to get default reviewers (limit to avoid too many API calls)
        enhanced = []
        for project in projects.get("values",
                                    [])[:10]:  # Limit to first 10 projects
            project_key = project.get("key")
            if not project_key:
                continue

            try:
                # Try to get default reviewers for this project (using repository endpoint)
                reviewers = await make_request(
                    "GET",
                    f"repositories/{WORKSPACE}/{project_key}/default-reviewers"
                )
                default_reviewer_names = [
                    reviewer.get("display_name", reviewer.get("nickname", ""))
                    for reviewer in reviewers.get("values", [])
                    if reviewer.get("display_name") or reviewer.get("nickname")
                ]
            except Exception:
                # If we can't get reviewers for this project, just skip them
                default_reviewer_names = []

            enhanced.append({
                "key":
                project.get("key"),
                "name":
                project.get("name", ""),
                "description":
                project.get("description", ""),
                "is_private":
                project.get("is_private", True),
                "default_reviewers":
                default_reviewer_names,
                "default_reviewer_count":
                len(default_reviewer_names)
            })

        return {
            "uri": f"bitbucket://{WORKSPACE}/workspace-projects",
            "mimeType": "application/json",
            "data": {
                "projects": enhanced,
                "count": len(enhanced),
                "workspace": WORKSPACE
            }
        }
    except Exception as e:
        return {
            "uri": f"bitbucket://{WORKSPACE}/workspace-projects",
            "mimeType": "application/json",
            "data": {
                "error": str(e)
            }
        }


async def get_common_patterns() -> dict:
    """Common usage patterns and workflow examples for Bitbucket tools"""
    return {
        "uri":
        "bitbucket://common-patterns",
        "mimeType":
        "text/markdown",
        "data":
        """# Bitbucket MCP Common Patterns

## Quick Reference

### Pipeline Analysis
- Use `analyze_pipeline_failure` for comprehensive failure analysis
- Lists failed steps, retrieves logs, provides recommendations
- Omit pipeline_uuid to analyze most recent failure

### Pull Request Workflows
- Use `review_pull_request` for complete PR analysis
- Includes changes, comments, tasks, approval status
- Returns merge_ready boolean for quick status

### Creating Pull Requests
1. Get available branches: `bitbucket://busie/fe-main/branches`
2. Get reviewers: `bitbucket://busie/workspace-members`  
3. Create PR with reviewer UUIDs (not usernames)

### Status Filtering
- Pipelines: SUCCESSFUL, FAILED, INPROGRESS, STOPPED
- PRs: OPEN, MERGED, DECLINED, SUPERSEDED

### Meta-Tools Priority
Use high-level workflows over individual tools:
- `analyze_pipeline_failure` > individual pipeline tools
- `review_pull_request` > individual PR tools  
- `workspace_overview` > individual workspace tools

### Resource Usage
- workspace-members: Get reviewer UUIDs for PR creation
- branches: Get valid branch names
- workspace-projects: Get project context
"""
    }


async def pipeline_resource_iterator(mcp):
    """
    Dynamically register recent pipeline runs as individual resources.
    Each pipeline becomes accessible as a resource for detailed inspection.
    """
    logger.info("Fetching recent pipelines for resource registration...")

    try:
        # Fetch the 25 most recent pipeline runs
        pipelines_response = await tools.list_pipelines(limit=25,
                                                        sort="-created_on")

        pipelines = pipelines_response.get("values", [])

        for pipeline in pipelines:
            pipeline_uuid = pipeline.get("uuid")
            build_number = pipeline.get("build_number")
            state = pipeline.get("state", {}).get("name", "UNKNOWN")

            if not pipeline_uuid or not build_number:
                continue

            # Create a descriptive resource name
            resource_name = f"Pipeline #{build_number} [{state}]"
            resource_uri = f"bitbucket://{WORKSPACE}/{REPO_SLUG}/pipelines/{build_number}"
            resource_description = (
                f"Pipeline #{build_number} - {state} - "
                f"Created: {pipeline.get('created_on', 'Unknown')[:19]}")

            logger.info(
                f"Registered resource for pipeline #{build_number} [{state}]")

            def create_pipeline_reader(uuid, number, status, uri, name, desc):
                """Closure to capture pipeline details for the resource"""

                @mcp.resource(uri,
                              name=name,
                              description=desc,
                              mime_type="application/json")
                async def read_pipeline_resource() -> dict:
                    """Read detailed pipeline information"""
                    try:
                        # Get full pipeline details using the UUID
                        pipeline_details = await tools.get_pipeline(uuid)

                        # Also get pipeline steps for additional context
                        steps = await tools.list_pipeline_steps(uuid)

                        return {
                            "data": {
                                "pipeline": pipeline_details,
                                "steps": steps.get("values", []),
                                "build_number": number,
                                "status": status
                            }
                        }
                    except Exception as e:
                        return {
                            "uri": uri,
                            "mimeType": "application/json",
                            "data": {
                                "error": str(e),
                                "build_number": number,
                                "status": status
                            }
                        }

                return read_pipeline_resource

            # Create and register the resource reader - pass ALL variables as arguments
            create_pipeline_reader(pipeline_uuid, build_number, state,
                                   resource_uri, resource_name,
                                   resource_description)

        logger.info(
            f"Successfully registered {len(pipelines)} pipeline resources")

    except Exception as e:
        logger.error(f"Failed to register pipeline resources: {str(e)}")


async def pr_resource_iterator(mcp):
    """
    Dynamically register recent PRs created by the current user as individual resources.
    Each PR becomes accessible as a resource for detailed inspection.
    """
    logger.info(
        "Fetching recent PRs created by current user for resource registration..."
    )

    try:
        # First get the current user to filter PRs
        current_user = await make_request("GET", "user")
        user_uuid = current_user.get("uuid")

        if not user_uuid:
            logger.warning(
                "Could not get current user UUID, skipping PR resource registration"
            )
            return

        # Fetch PRs created by the current user (most recent 10)
        prs_response = await make_request(
            "GET",
            f"repositories/{WORKSPACE}/{REPO_SLUG}/pullrequests",
            params={
                "q": f'author.uuid="{user_uuid}"',
                "sort": "-created_on",
                "pagelen": 10
            })

        prs = prs_response.get("values", [])

        for pr in prs:
            pr_id = pr.get("id")
            pr_title = pr.get("title", "Untitled")
            pr_state = pr.get("state", "UNKNOWN")
            source_branch = pr.get("source",
                                   {}).get("branch",
                                           {}).get("name", "unknown")
            destination_branch = pr.get("destination",
                                        {}).get("branch",
                                                {}).get("name", "unknown")

            if not pr_id:
                continue

            # Create a descriptive resource name
            resource_name = f"PR #{pr_id} [{pr_state}] - {pr_title[:50]}"
            resource_uri = f"bitbucket://{WORKSPACE}/{REPO_SLUG}/pull-requests/{pr_id}"
            resource_description = (
                f"PR #{pr_id} - {pr_state} - "
                f"{source_branch} → {destination_branch} - "
                f"Created: {pr.get('created_on', 'Unknown')[:19]}")

            logger.info(f"Registered resource for PR #{pr_id} [{pr_state}]")

            def create_pr_reader(id, title, state, uri, name, desc):
                """Closure to capture PR details for the resource"""

                @mcp.resource(uri,
                              name=name,
                              description=desc,
                              mime_type="application/json")
                async def read_pr_resource() -> dict:
                    """Read detailed PR information"""
                    try:
                        # Get full PR details
                        pr_details = await tools.get_pull_request(id)

                        # Also get PR comments for additional context
                        comments = await tools.list_pr_comments(id)

                        # Get PR diffstat for change summary
                        diffstat = await tools.get_pr_diffstat(id)

                        return {
                            "data": {
                                "pull_request": pr_details,
                                "comments": comments.get("values", []),
                                "diffstat": diffstat,
                                "pr_id": id,
                                "title": title,
                                "state": state
                            }
                        }
                    except Exception as e:
                        return {
                            "uri": uri,
                            "mimeType": "application/json",
                            "data": {
                                "error": str(e),
                                "pr_id": id,
                                "title": title,
                                "state": state
                            }
                        }

                return read_pr_resource

            # Create and register the resource reader - pass ALL variables as arguments
            create_pr_reader(pr_id, pr_title, pr_state, resource_uri,
                             resource_name, resource_description)

        logger.info(f"Successfully registered {len(prs)} PR resources")

    except Exception as e:
        logger.error(f"Failed to register PR resources: {str(e)}")
