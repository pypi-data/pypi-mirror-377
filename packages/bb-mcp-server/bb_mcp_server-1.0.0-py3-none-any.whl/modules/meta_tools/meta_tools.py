"""
Meta-Tool definitions for Bitbucket MCP Server
Provides high-level composed workflows that combine multiple base tools
Implements common patterns documented in bitbucket_api_testing.md
"""

from typing import Optional, Dict, Any, List
from utils.config import WORKSPACE
from modules import tools


async def analyze_pipeline_failure(pipeline_uuid: Optional[str] | None = None) -> Dict[str, Any]:
    """
    Analyzes pipeline failures by combining multiple API calls into a single workflow.

    Workflow: list_pipelines → get_pipeline → list_pipeline_steps → get_pipeline_step_logs

    Args:
        pipeline_uuid: Optional UUID of specific pipeline to analyze.
                      If not provided, analyzes the most recent failed pipeline.

    Returns:
        Dict containing:
        - pipeline_info: Basic pipeline information
        - failure_summary: Analysis of failed steps
        - failed_logs: Logs from each failed step
        - recommendations: Suggested next steps
    """
    # Input validation
    if pipeline_uuid and not isinstance(pipeline_uuid, str):
        return {
            "error": "pipeline_uuid must be a string",
            "pipeline_info": None,
            "failure_summary": None,
            "failed_logs": {},
            "recommendations": ["Provide valid pipeline UUID"]
        }

    # Strip curly braces if present (support both {uuid} and uuid formats)
    if pipeline_uuid:
        pipeline_uuid = pipeline_uuid.strip()
        if pipeline_uuid.startswith('{') and pipeline_uuid.endswith('}'):
            pipeline_uuid = pipeline_uuid[1:-1]

    if pipeline_uuid and (not pipeline_uuid or len(pipeline_uuid) < 10):
        return {
            "error": "pipeline_uuid appears to be invalid (too short)",
            "pipeline_info": None,
            "failure_summary": None,
            "failed_logs": {},
            "recommendations": ["Provide valid pipeline UUID from Bitbucket"]
        }
    
    try:
        # Step 1: Get pipeline to analyze
        if pipeline_uuid:
            pipeline = await tools.get_pipeline(pipeline_uuid)
        else:
            # Find most recent failed pipeline
            pipelines = await tools.list_pipelines(status="FAILED")
            if not pipelines.get("values"):
                return {
                    "error": "No failed pipelines found",
                    "pipeline_info": None,
                    "failure_summary": None,
                    "failed_logs": [],
                    "recommendations": ["Check for recent successful pipelines"]
                }
            pipeline = pipelines["values"][0]
            pipeline_uuid = pipeline["uuid"]
        
        # Step 2: Get detailed pipeline info and steps
        pipeline_details = await tools.get_pipeline(pipeline_uuid)
        steps = await tools.list_pipeline_steps(pipeline_uuid)
        
        # Step 3: Analyze failed steps and collect logs
        failed_steps = []
        failed_logs = {}
        
        if steps.get("values"):
            for step in steps["values"]:
                if step.get("state", {}).get("result", {}).get("name") == "FAILED":
                    failed_steps.append({
                        "name": step.get("name", "Unknown"),
                        "uuid": step.get("uuid", ""),
                        "duration": step.get("duration_in_seconds", 0),
                        "completed_on": step.get("completed_on")
                    })
                    
                    # Get logs for failed step
                    try:
                        logs = await tools.get_pipeline_step_logs(pipeline_uuid, step["uuid"])
                        failed_logs[step.get("name", "Unknown")] = logs
                    except Exception as e:
                        failed_logs[step.get("name", "Unknown")] = f"Could not retrieve logs: {str(e)}"
        
        # Step 4: Generate recommendations
        recommendations = []
        if failed_steps:
            step_names = [step["name"] for step in failed_steps]
            if "Lint Check" in step_names:
                recommendations.append("Run local linting: npm run lint")
            if "Type Check" in step_names:
                recommendations.append("Run local type checking: npm run typecheck")
            if "Test Affected" in step_names:
                recommendations.append("Run affected tests locally: npm run test:affected")
            if "Build Affected" in step_names:
                recommendations.append("Run affected build locally: npm run build:affected")
        
        return {
            "pipeline_info": {
                "uuid": pipeline_details.get("uuid"),
                "build_number": pipeline_details.get("build_number"),
                "state": pipeline_details.get("state", {}).get("name"),
                "created_on": pipeline_details.get("created_on"),
                "completed_on": pipeline_details.get("completed_on"),
                "duration": pipeline_details.get("duration_in_seconds"),
                "trigger": pipeline_details.get("trigger", {}).get("name"),
                "target": pipeline_details.get("target", {})
            },
            "failure_summary": {
                "total_steps": len(steps.get("values", [])),
                "failed_steps": len(failed_steps),
                "failed_step_details": failed_steps
            },
            "failed_logs": failed_logs,
            "recommendations": recommendations or ["Review pipeline configuration and recent changes"]
        }
        
    except Exception as e:
        return {
            "error": f"Failed to analyze pipeline: {str(e)}",
            "pipeline_info": None,
            "failure_summary": None,
            "failed_logs": {},
            "recommendations": ["Check pipeline UUID and try again"]
        }


async def review_pull_request(pull_request_id: int) -> Dict[str, Any]:
    """
    Provides comprehensive pull request review by combining multiple API calls.
    
    Workflow: get_pull_request → list_pr_comments → get_pr_diffstat → get_pr_changes
    
    Args:
        pull_request_id: ID of the pull request to review
        
    Returns:
        Dict containing:
        - pr_info: Basic PR information
        - discussion: Comments and activity
        - changes_summary: Files changed and diff statistics
        - review_status: Current review state
        - tasks: Any tasks/checklist items
    """
    # Input validation
    if not isinstance(pull_request_id, int) or pull_request_id <= 0:
        return {
            "error": "pull_request_id must be a positive integer",
            "pr_info": None,
            "discussion": None,
            "changes_summary": None,
            "review_status": None,
            "tasks": None,
            "merge_ready": False
        }
    
    try:
        # Step 1: Get basic PR information
        pr_details = await tools.get_pull_request(pull_request_id)
        
        # Step 2: Get all related data in parallel-style calls
        comments = await tools.list_pr_comments(pull_request_id)
        diffstat = await tools.get_pr_diffstat(pull_request_id)
        changes = await tools.get_pr_changes(pull_request_id)
        tasks = await tools.list_pr_tasks(pull_request_id)
        
        # Step 3: Process and structure the information
        pr_info = {
            "id": pr_details.get("id"),
            "title": pr_details.get("title"),
            "description": pr_details.get("description", ""),
            "state": pr_details.get("state"),
            "author": pr_details.get("author", {}).get("display_name", "Unknown"),
            "source_branch": pr_details.get("source", {}).get("branch", {}).get("name"),
            "destination_branch": pr_details.get("destination", {}).get("branch", {}).get("name"),
            "created_on": pr_details.get("created_on"),
            "updated_on": pr_details.get("updated_on"),
            "close_source_branch": pr_details.get("close_source_branch", False)
        }
        
        # Process comments for discussion summary
        discussion = {
            "total_comments": len(comments.get("values", [])),
            "participants": [],
            "recent_activity": []
        }
        
        participants = set()
        for comment in comments.get("values", [])[:5]:  # Last 5 comments
            author = comment.get("user", {}).get("display_name", "Unknown")
            participants.add(author)
            discussion["recent_activity"].append({
                "author": author,
                "created_on": comment.get("created_on"),
                "content_preview": comment.get("content", {}).get("raw", "")[:100] + "..." 
                    if len(comment.get("content", {}).get("raw", "")) > 100 
                    else comment.get("content", {}).get("raw", "")
            })
        
        discussion["participants"] = list(participants)
        
        # Process diff statistics
        changes_summary = {
            "files_changed": len(diffstat.get("values", [])),
            "total_additions": sum(file.get("lines_added", 0) for file in diffstat.get("values", [])),
            "total_deletions": sum(file.get("lines_removed", 0) for file in diffstat.get("values", [])),
            "files": [
                {
                    "filename": file.get("new", {}).get("path") or file.get("old", {}).get("path"),
                    "status": file.get("status"),
                    "additions": file.get("lines_added", 0),
                    "deletions": file.get("lines_removed", 0)
                } for file in diffstat.get("values", [])
            ][:10]  # Limit to first 10 files for readability
        }
        
        # Process review status
        reviewers = pr_details.get("reviewers", [])
        review_status = {
            "reviewers_count": len(reviewers),
            "reviewers": [
                {
                    "name": reviewer.get("display_name", "Unknown"),
                    "approved": reviewer.get("approved", False)
                } for reviewer in reviewers
            ],
            "approval_status": "approved" if all(r.get("approved", False) for r in reviewers) and reviewers 
                            else "pending" if reviewers 
                            else "no_reviewers"
        }
        
        # Process tasks
        task_info = {
            "total_tasks": len(tasks.get("values", [])),
            "completed_tasks": len([t for t in tasks.get("values", []) if t.get("state") == "RESOLVED"]),
            "task_list": [
                {
                    "id": task.get("id"),
                    "content": task.get("content", {}).get("raw", ""),
                    "state": task.get("state"),
                    "creator": task.get("creator", {}).get("display_name", "Unknown")
                } for task in tasks.get("values", [])
            ]
        }
        
        return {
            "pr_info": pr_info,
            "discussion": discussion,
            "changes_summary": changes_summary,
            "review_status": review_status,
            "tasks": task_info,
            "merge_ready": (
                pr_info["state"] == "OPEN" and 
                review_status["approval_status"] == "approved" and
                task_info["completed_tasks"] == task_info["total_tasks"]
            )
        }
        
    except Exception as e:
        return {
            "error": f"Failed to review pull request: {str(e)}",
            "pr_info": None,
            "discussion": None,
            "changes_summary": None,
            "review_status": None,
            "tasks": None,
            "merge_ready": False
        }


async def workspace_overview(workspace: Optional[str]| None = None) -> Dict[str, Any]:
    """
    Provides comprehensive workspace overview by combining multiple API calls.
    
    Workflow: get_workspace → list_workspace_repos → list_workspace_projects → list_workspace_members
    
    Args:
        workspace: Optional workspace name. If not provided, uses configured default.
        
    Returns:
        Dict containing:
        - workspace_info: Basic workspace information
        - repositories: Summary of repositories
        - projects: List of projects
        - members: Team members information
        - activity_summary: Recent activity indicators
    """
    # Input validation
    if workspace and (not isinstance(workspace, str) or not workspace.strip()):
        return {
            "error": "workspace must be a non-empty string",
            "workspace_info": None,
            "repositories": None,
            "projects": None,
            "members": None,
            "activity_summary": None
        }
    
    try:
        target_workspace = workspace or WORKSPACE
        
        # Step 1: Get workspace information
        workspace_info = await tools.get_workspace(target_workspace)
        
        # Step 2: Get repositories, projects, and members
        repos = await tools.list_workspace_repos(target_workspace)
        projects = await tools.list_workspace_projects(target_workspace)
        members = await tools.list_workspace_members(target_workspace)
        
        # Step 3: Process workspace information
        workspace_summary = {
            "name": workspace_info.get("name"),
            "display_name": workspace_info.get("display_name"),
            "type": workspace_info.get("type"),
            "uuid": workspace_info.get("uuid"),
            "created_on": workspace_info.get("created_on"),
            "website": workspace_info.get("website"),
            "is_private": workspace_info.get("is_private", True)
        }
        
        # Process repositories
        repo_summary = {
            "total_count": len(repos.get("values", [])),
            "languages": {},
            "recent_repos": []
        }
        
        for repo in repos.get("values", [])[:10]:  # First 10 repos
            # Count languages
            language = repo.get("language", "Unknown")
            repo_summary["languages"][language] = repo_summary["languages"].get(language, 0) + 1
            
            # Add to recent repos
            repo_summary["recent_repos"].append({
                "name": repo.get("name"),
                "full_name": repo.get("full_name"),
                "is_private": repo.get("is_private"),
                "created_on": repo.get("created_on"),
                "updated_on": repo.get("updated_on"),
                "language": language,
                "size": repo.get("size", 0),
                "description": repo.get("description", "")[:100] + "..." 
                    if len(repo.get("description", "")) > 100 
                    else repo.get("description", "")
            })
        
        # Process projects
        project_summary = {
            "total_count": len(projects.get("values", [])),
            "project_list": [
                {
                    "key": project.get("key"),
                    "name": project.get("name"),
                    "description": project.get("description", ""),
                    "is_private": project.get("is_private"),
                    "created_on": project.get("created_on")
                } for project in projects.get("values", [])
            ]
        }
        
        # Process members
        member_summary = {
            "total_count": len(members.get("values", [])),
            "member_list": [
                {
                    "display_name": member.get("display_name"),
                    "nickname": member.get("nickname"),
                    "account_id": member.get("account_id"),
                    "type": member.get("type")
                } for member in members.get("values", [])
            ]
        }
        
        # Generate activity summary
        activity_summary = {
            "total_repositories": repo_summary["total_count"],
            "total_projects": project_summary["total_count"],
            "total_members": member_summary["total_count"],
            "primary_languages": sorted(repo_summary["languages"].items(), 
                                      key=lambda x: x[1], reverse=True)[:5],
            "workspace_health": "active" if repo_summary["total_count"] > 0 and member_summary["total_count"] > 1 else "needs_attention"
        }
        
        return {
            "workspace_info": workspace_summary,
            "repositories": repo_summary,
            "projects": project_summary,
            "members": member_summary,
            "activity_summary": activity_summary
        }
        
    except Exception as e:
        return {
            "error": f"Failed to get workspace overview: {str(e)}",
            "workspace_info": None,
            "repositories": None,
            "projects": None,
            "members": None,
            "activity_summary": None
        }
