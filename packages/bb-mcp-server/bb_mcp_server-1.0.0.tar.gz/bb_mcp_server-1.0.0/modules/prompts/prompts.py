from utils.api_client import make_request


async def commit_push_and_create_pr() -> str:
    """Generates a prompt to commit all changes, push to remote, and create a PR. Includes default reviewers."""
    reviewers = await make_request(
        "GET",
        f"repositories/busie/fe-main/default-reviewers",
        accept_type="application/json")
    user = await make_request("GET", "user", accept_type="application/json")
    reviewers["values"] = [
        r for r in reviewers["values"] if r["uuid"] != user["uuid"]
    ]
    if not reviewers["values"]:
        return "Commit all changes, push to remote, and create a pull request with no default reviewers. Use the create_pull_request tool."
    reviewers["values"] = [
        f"{r['display_name']} ({r['uuid']})" for r in reviewers["values"]
    ]
    return f"Commit all changes, push to remote, and create a pull request. Available default reviewers: {reviewers['values']}. Use the create_pull_request tool."


async def create_markdown_from_latest_failed_pipeline() -> str:
    """Generates a prompt based on data that needs to be fetched."""
    pipeline = await make_request(
        "GET",
        f"repositories/busie/fe-main/pipelines/?sort=-created_on&pagelen=1&status=FAILED",
        accept_type="application/json")
    return f"Create a markdown report based on the latest failed pipeline: {pipeline}"
