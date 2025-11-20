"""Jira tools - Refactored to use Service Layer.

This module provides tool functions that wrap the JiraService,
following the tool protocol with Pydantic input/output models.
"""

from atlassian_tools._core.container import get_jira_service
from atlassian_tools._core.exceptions import AtlassianError, NotFoundError
from atlassian_tools.jira.models import (
    # Write tool models
    JiraAddCommentInput,
    JiraAddCommentOutput,
    JiraAddWatcherInput,
    JiraAddWatcherOutput,
    JiraAddWorklogInput,
    JiraAddWorklogOutput,
    JiraAssignIssueInput,
    JiraAssignIssueOutput,
    JiraBatchCreateIssuesInput,
    JiraBatchCreateIssuesOutput,
    JiraCreateIssueInput,
    JiraCreateIssueOutput,
    JiraDeleteCommentInput,
    JiraDeleteCommentOutput,
    JiraDeleteIssueInput,
    JiraDeleteIssueOutput,
    # Read tool models
    JiraGetAllProjectsInput,
    JiraGetAllProjectsOutput,
    JiraGetBoardIssuesInput,
    JiraGetBoardIssuesOutput,
    JiraGetCommentsInput,
    JiraGetCommentsOutput,
    JiraGetEpicIssuesInput,
    JiraGetEpicIssuesOutput,
    JiraGetFieldsInput,
    JiraGetFieldsOutput,
    JiraGetIssueInput,
    JiraGetIssueOutput,
    JiraGetLinkTypesInput,
    JiraGetLinkTypesOutput,
    JiraGetPrioritiesInput,
    JiraGetPrioritiesOutput,
    JiraGetProjectIssuesInput,
    JiraGetProjectIssuesOutput,
    JiraGetResolutionsInput,
    JiraGetResolutionsOutput,
    JiraGetSprintIssuesInput,
    JiraGetSprintIssuesOutput,
    JiraGetTransitionsInput,
    JiraGetTransitionsOutput,
    JiraGetUserProfileInput,
    JiraGetUserProfileOutput,
    JiraGetWatchersInput,
    JiraGetWatchersOutput,
    JiraGetWorklogInput,
    JiraGetWorklogOutput,
    JiraLinkIssuesInput,
    JiraLinkIssuesOutput,
    JiraRemoveWatcherInput,
    JiraRemoveWatcherOutput,
    JiraSearchInput,
    JiraSearchOutput,
    JiraTransitionIssueInput,
    JiraTransitionIssueOutput,
    JiraUnlinkIssuesInput,
    JiraUnlinkIssuesOutput,
    JiraUpdateCommentInput,
    JiraUpdateCommentOutput,
    JiraUpdateIssueInput,
    JiraUpdateIssueOutput,
)

# =============================================================================
# Read Tools
# =============================================================================


async def jira_get_issue(input: JiraGetIssueInput) -> JiraGetIssueOutput:
    """Get details of a specific Jira issue."""
    try:
        service = get_jira_service()
        issue = await service.get_issue(
            issue_key=input.issue_key,
            fields=input.fields or "*all",
            expand=input.expand,
        )
        return JiraGetIssueOutput(success=True, issue=issue)
    except NotFoundError:
        return JiraGetIssueOutput(
            success=False,
            error=f"Issue {input.issue_key} not found",
        )
    except AtlassianError as e:
        return JiraGetIssueOutput(success=False, error=str(e))
    except Exception as e:
        return JiraGetIssueOutput(success=False, error=str(e))


jira_get_issue.tool_name = "jira_get_issue"  # type: ignore
jira_get_issue.input_schema = JiraGetIssueInput  # type: ignore
jira_get_issue.output_schema = JiraGetIssueOutput  # type: ignore


async def jira_search(input: JiraSearchInput) -> JiraSearchOutput:
    """Search for Jira issues using JQL."""
    try:
        service = get_jira_service()
        results = await service.search(
            jql=input.jql,
            max_results=input.max_results,
            start_at=input.start_at,
            fields=input.fields or "*navigable",
        )
        return JiraSearchOutput(
            success=True,
            issues=results["issues"],
            total=results["total"],
        )
    except AtlassianError as e:
        return JiraSearchOutput(success=False, error=str(e))


jira_search.tool_name = "jira_search"  # type: ignore
jira_search.input_schema = JiraSearchInput  # type: ignore
jira_search.output_schema = JiraSearchOutput  # type: ignore


async def jira_get_all_projects(
    input: JiraGetAllProjectsInput,
) -> JiraGetAllProjectsOutput:
    """Get all accessible Jira projects."""
    try:
        service = get_jira_service()
        projects = await service.get_projects()
        return JiraGetAllProjectsOutput(success=True, projects=projects)
    except AtlassianError as e:
        return JiraGetAllProjectsOutput(success=False, error=str(e))


jira_get_all_projects.tool_name = "jira_get_all_projects"  # type: ignore
jira_get_all_projects.input_schema = JiraGetAllProjectsInput  # type: ignore
jira_get_all_projects.output_schema = JiraGetAllProjectsOutput  # type: ignore


async def jira_get_transitions(
    input: JiraGetTransitionsInput,
) -> JiraGetTransitionsOutput:
    """Get available transitions for a Jira issue."""
    try:
        service = get_jira_service()
        transitions = await service.get_transitions(input.issue_key)
        return JiraGetTransitionsOutput(success=True, transitions=transitions)
    except NotFoundError:
        return JiraGetTransitionsOutput(
            success=False,
            error=f"Issue {input.issue_key} not found",
        )
    except AtlassianError as e:
        return JiraGetTransitionsOutput(success=False, error=str(e))


jira_get_transitions.tool_name = "jira_get_transitions"  # type: ignore
jira_get_transitions.input_schema = JiraGetTransitionsInput  # type: ignore
jira_get_transitions.output_schema = JiraGetTransitionsOutput  # type: ignore


async def jira_get_user_profile(
    input: JiraGetUserProfileInput,
) -> JiraGetUserProfileOutput:
    """Get current user's profile."""
    try:
        service = get_jira_service()
        user = await service.get_user_profile()
        return JiraGetUserProfileOutput(success=True, user=user)
    except AtlassianError as e:
        return JiraGetUserProfileOutput(success=False, error=str(e))


jira_get_user_profile.tool_name = "jira_get_user_profile"  # type: ignore
jira_get_user_profile.input_schema = JiraGetUserProfileInput  # type: ignore
jira_get_user_profile.output_schema = JiraGetUserProfileOutput  # type: ignore


async def jira_get_comments(
    input: JiraGetCommentsInput,
) -> JiraGetCommentsOutput:
    """Get comments for a Jira issue."""
    try:
        service = get_jira_service()
        comments = await service.get_comments(
            issue_key=input.issue_key,
            max_results=input.max_results,
        )
        return JiraGetCommentsOutput(success=True, comments=comments)
    except NotFoundError:
        return JiraGetCommentsOutput(
            success=False,
            error=f"Issue {input.issue_key} not found",
        )
    except AtlassianError as e:
        return JiraGetCommentsOutput(success=False, error=str(e))


jira_get_comments.tool_name = "jira_get_comments"  # type: ignore
jira_get_comments.input_schema = JiraGetCommentsInput  # type: ignore
jira_get_comments.output_schema = JiraGetCommentsOutput  # type: ignore


async def jira_get_worklog(input: JiraGetWorklogInput) -> JiraGetWorklogOutput:
    """Get worklog entries for a Jira issue."""
    try:
        service = get_jira_service()
        # Use HTTP client directly for worklog
        client = service._client
        response = await client.get(
            f"/rest/api/3/issue/{input.issue_key}/worklog",
            params={"maxResults": input.max_results},
        )
        data = response.json()
        worklogs = [
            {
                "id": w.get("id"),
                "author": w.get("author", {}).get("displayName"),
                "time_spent": w.get("timeSpent"),
                "started": w.get("started"),
                "comment": w.get("comment"),
            }
            for w in data.get("worklogs", [])
        ]
        return JiraGetWorklogOutput(success=True, worklogs=worklogs)
    except NotFoundError:
        return JiraGetWorklogOutput(
            success=False,
            error=f"Issue {input.issue_key} not found",
        )
    except AtlassianError as e:
        return JiraGetWorklogOutput(success=False, error=str(e))


jira_get_worklog.tool_name = "jira_get_worklog"  # type: ignore
jira_get_worklog.input_schema = JiraGetWorklogInput  # type: ignore
jira_get_worklog.output_schema = JiraGetWorklogOutput  # type: ignore


async def jira_get_watchers(
    input: JiraGetWatchersInput,
) -> JiraGetWatchersOutput:
    """Get watchers for a Jira issue."""
    try:
        service = get_jira_service()
        client = service._client
        response = await client.get(
            f"/rest/api/3/issue/{input.issue_key}/watchers"
        )
        data = response.json()
        watchers = [
            {
                "account_id": w.get("accountId"),
                "display_name": w.get("displayName"),
            }
            for w in data.get("watchers", [])
        ]
        return JiraGetWatchersOutput(
            success=True,
            watchers=watchers,
            watch_count=data.get("watchCount", 0),
        )
    except NotFoundError:
        return JiraGetWatchersOutput(
            success=False,
            error=f"Issue {input.issue_key} not found",
        )
    except AtlassianError as e:
        return JiraGetWatchersOutput(success=False, error=str(e))


jira_get_watchers.tool_name = "jira_get_watchers"  # type: ignore
jira_get_watchers.input_schema = JiraGetWatchersInput  # type: ignore
jira_get_watchers.output_schema = JiraGetWatchersOutput  # type: ignore


async def jira_get_sprint_issues(
    input: JiraGetSprintIssuesInput,
) -> JiraGetSprintIssuesOutput:
    """Get issues in a sprint."""
    try:
        service = get_jira_service()
        client = service._client
        response = await client.get(
            f"/rest/agile/1.0/sprint/{input.sprint_id}/issue",
            params={"maxResults": input.max_results},
        )
        data = response.json()
        issues = [
            {
                "key": i.get("key"),
                "summary": i.get("fields", {}).get("summary"),
                "status": i.get("fields", {}).get("status", {}).get("name"),
            }
            for i in data.get("issues", [])
        ]
        return JiraGetSprintIssuesOutput(success=True, issues=issues)
    except NotFoundError:
        return JiraGetSprintIssuesOutput(
            success=False,
            error=f"Sprint {input.sprint_id} not found",
        )
    except AtlassianError as e:
        return JiraGetSprintIssuesOutput(success=False, error=str(e))


jira_get_sprint_issues.tool_name = "jira_get_sprint_issues"  # type: ignore
jira_get_sprint_issues.input_schema = JiraGetSprintIssuesInput  # type: ignore
jira_get_sprint_issues.output_schema = JiraGetSprintIssuesOutput  # type: ignore


async def jira_get_board_issues(
    input: JiraGetBoardIssuesInput,
) -> JiraGetBoardIssuesOutput:
    """Get issues on a board."""
    try:
        service = get_jira_service()
        client = service._client
        response = await client.get(
            f"/rest/agile/1.0/board/{input.board_id}/issue",
            params={"maxResults": input.max_results},
        )
        data = response.json()
        issues = [
            {
                "key": i.get("key"),
                "summary": i.get("fields", {}).get("summary"),
                "status": i.get("fields", {}).get("status", {}).get("name"),
            }
            for i in data.get("issues", [])
        ]
        return JiraGetBoardIssuesOutput(success=True, issues=issues)
    except NotFoundError:
        return JiraGetBoardIssuesOutput(
            success=False,
            error=f"Board {input.board_id} not found",
        )
    except AtlassianError as e:
        return JiraGetBoardIssuesOutput(success=False, error=str(e))


jira_get_board_issues.tool_name = "jira_get_board_issues"  # type: ignore
jira_get_board_issues.input_schema = JiraGetBoardIssuesInput  # type: ignore
jira_get_board_issues.output_schema = JiraGetBoardIssuesOutput  # type: ignore


async def jira_get_epic_issues(
    input: JiraGetEpicIssuesInput,
) -> JiraGetEpicIssuesOutput:
    """Get issues in an epic."""
    try:
        service = get_jira_service()
        client = service._client
        response = await client.get(
            f"/rest/agile/1.0/epic/{input.epic_key}/issue",
            params={"maxResults": input.max_results},
        )
        data = response.json()
        issues = [
            {
                "key": i.get("key"),
                "summary": i.get("fields", {}).get("summary"),
                "status": i.get("fields", {}).get("status", {}).get("name"),
            }
            for i in data.get("issues", [])
        ]
        return JiraGetEpicIssuesOutput(success=True, issues=issues)
    except NotFoundError:
        return JiraGetEpicIssuesOutput(
            success=False,
            error=f"Epic {input.epic_key} not found",
        )
    except AtlassianError as e:
        return JiraGetEpicIssuesOutput(success=False, error=str(e))


jira_get_epic_issues.tool_name = "jira_get_epic_issues"  # type: ignore
jira_get_epic_issues.input_schema = JiraGetEpicIssuesInput  # type: ignore
jira_get_epic_issues.output_schema = JiraGetEpicIssuesOutput  # type: ignore


async def jira_get_project_issues(
    input: JiraGetProjectIssuesInput,
) -> JiraGetProjectIssuesOutput:
    """Get issues in a project."""
    try:
        service = get_jira_service()
        jql = f"project = {input.project_key}"
        if input.status:
            jql += f" AND status = '{input.status}'"
        jql += " ORDER BY created DESC"

        results = await service.search(
            jql=jql,
            max_results=input.max_results,
        )
        return JiraGetProjectIssuesOutput(
            success=True,
            issues=results["issues"],
            total=results["total"],
        )
    except AtlassianError as e:
        return JiraGetProjectIssuesOutput(success=False, error=str(e))


jira_get_project_issues.tool_name = "jira_get_project_issues"  # type: ignore
jira_get_project_issues.input_schema = JiraGetProjectIssuesInput  # type: ignore
jira_get_project_issues.output_schema = JiraGetProjectIssuesOutput  # type: ignore


async def jira_get_fields(input: JiraGetFieldsInput) -> JiraGetFieldsOutput:
    """Get all available Jira fields."""
    try:
        service = get_jira_service()
        fields = await service.get_fields()
        return JiraGetFieldsOutput(success=True, fields=fields)
    except AtlassianError as e:
        return JiraGetFieldsOutput(success=False, error=str(e))


jira_get_fields.tool_name = "jira_get_fields"  # type: ignore
jira_get_fields.input_schema = JiraGetFieldsInput  # type: ignore
jira_get_fields.output_schema = JiraGetFieldsOutput  # type: ignore


async def jira_get_link_types(
    input: JiraGetLinkTypesInput,
) -> JiraGetLinkTypesOutput:
    """Get all available issue link types."""
    try:
        service = get_jira_service()
        client = service._client
        response = await client.get("/rest/api/3/issueLinkType")
        data = response.json()
        link_types = [
            {
                "id": lt.get("id"),
                "name": lt.get("name"),
                "inward": lt.get("inward"),
                "outward": lt.get("outward"),
            }
            for lt in data.get("issueLinkTypes", [])
        ]
        return JiraGetLinkTypesOutput(success=True, link_types=link_types)
    except AtlassianError as e:
        return JiraGetLinkTypesOutput(success=False, error=str(e))


jira_get_link_types.tool_name = "jira_get_link_types"  # type: ignore
jira_get_link_types.input_schema = JiraGetLinkTypesInput  # type: ignore
jira_get_link_types.output_schema = JiraGetLinkTypesOutput  # type: ignore


async def jira_get_priorities(
    input: JiraGetPrioritiesInput,
) -> JiraGetPrioritiesOutput:
    """Get all available priorities."""
    try:
        service = get_jira_service()
        priorities = await service.get_priorities()
        return JiraGetPrioritiesOutput(success=True, priorities=priorities)
    except AtlassianError as e:
        return JiraGetPrioritiesOutput(success=False, error=str(e))


jira_get_priorities.tool_name = "jira_get_priorities"  # type: ignore
jira_get_priorities.input_schema = JiraGetPrioritiesInput  # type: ignore
jira_get_priorities.output_schema = JiraGetPrioritiesOutput  # type: ignore


async def jira_get_resolutions(
    input: JiraGetResolutionsInput,
) -> JiraGetResolutionsOutput:
    """Get all available resolutions."""
    try:
        service = get_jira_service()
        resolutions = await service.get_resolutions()
        return JiraGetResolutionsOutput(success=True, resolutions=resolutions)
    except AtlassianError as e:
        return JiraGetResolutionsOutput(success=False, error=str(e))


jira_get_resolutions.tool_name = "jira_get_resolutions"  # type: ignore
jira_get_resolutions.input_schema = JiraGetResolutionsInput  # type: ignore
jira_get_resolutions.output_schema = JiraGetResolutionsOutput  # type: ignore


# =============================================================================
# Write Tools
# =============================================================================


async def jira_create_issue(
    input: JiraCreateIssueInput,
) -> JiraCreateIssueOutput:
    """Create a new Jira issue."""
    try:
        service = get_jira_service()
        result = await service.create_issue(
            project_key=input.project_key,
            summary=input.summary,
            issue_type=input.issue_type,
            description=input.description,
            priority=input.priority,
            assignee=input.assignee_id,
            labels=input.labels,
            components=input.components,
        )
        return JiraCreateIssueOutput(
            success=True,
            issue_key=result["key"],
            issue_id=result["id"],
        )
    except AtlassianError as e:
        return JiraCreateIssueOutput(success=False, error=str(e))


jira_create_issue.tool_name = "jira_create_issue"  # type: ignore
jira_create_issue.input_schema = JiraCreateIssueInput  # type: ignore
jira_create_issue.output_schema = JiraCreateIssueOutput  # type: ignore


async def jira_update_issue(
    input: JiraUpdateIssueInput,
) -> JiraUpdateIssueOutput:
    """Update an existing Jira issue."""
    try:
        service = get_jira_service()
        await service.update_issue(
            issue_key=input.issue_key,
            summary=input.summary,
            description=input.description,
            priority=input.priority,
            assignee=input.assignee_id,
            labels=input.labels,
        )
        return JiraUpdateIssueOutput(success=True)
    except NotFoundError:
        return JiraUpdateIssueOutput(
            success=False,
            error=f"Issue {input.issue_key} not found",
        )
    except AtlassianError as e:
        return JiraUpdateIssueOutput(success=False, error=str(e))


jira_update_issue.tool_name = "jira_update_issue"  # type: ignore
jira_update_issue.input_schema = JiraUpdateIssueInput  # type: ignore
jira_update_issue.output_schema = JiraUpdateIssueOutput  # type: ignore


async def jira_add_comment(input: JiraAddCommentInput) -> JiraAddCommentOutput:
    """Add a comment to a Jira issue."""
    try:
        service = get_jira_service()
        result = await service.add_comment(
            issue_key=input.issue_key,
            body=input.body,
        )
        return JiraAddCommentOutput(
            success=True,
            comment_id=result["id"],
        )
    except NotFoundError:
        return JiraAddCommentOutput(
            success=False,
            error=f"Issue {input.issue_key} not found",
        )
    except AtlassianError as e:
        return JiraAddCommentOutput(success=False, error=str(e))


jira_add_comment.tool_name = "jira_add_comment"  # type: ignore
jira_add_comment.input_schema = JiraAddCommentInput  # type: ignore
jira_add_comment.output_schema = JiraAddCommentOutput  # type: ignore


async def jira_transition_issue(
    input: JiraTransitionIssueInput,
) -> JiraTransitionIssueOutput:
    """Transition a Jira issue to a new status."""
    try:
        service = get_jira_service()
        await service.transition_issue(
            issue_key=input.issue_key,
            transition_id=input.transition_id,
            comment=input.comment,
        )
        return JiraTransitionIssueOutput(success=True)
    except NotFoundError:
        return JiraTransitionIssueOutput(
            success=False,
            error=f"Issue {input.issue_key} not found",
        )
    except AtlassianError as e:
        return JiraTransitionIssueOutput(success=False, error=str(e))


jira_transition_issue.tool_name = "jira_transition_issue"  # type: ignore
jira_transition_issue.input_schema = JiraTransitionIssueInput  # type: ignore
jira_transition_issue.output_schema = JiraTransitionIssueOutput  # type: ignore


async def jira_assign_issue(
    input: JiraAssignIssueInput,
) -> JiraAssignIssueOutput:
    """Assign a Jira issue to a user."""
    try:
        service = get_jira_service()
        await service.assign_issue(
            issue_key=input.issue_key,
            account_id=input.account_id,
        )
        return JiraAssignIssueOutput(success=True)
    except NotFoundError:
        return JiraAssignIssueOutput(
            success=False,
            error=f"Issue {input.issue_key} not found",
        )
    except AtlassianError as e:
        return JiraAssignIssueOutput(success=False, error=str(e))


jira_assign_issue.tool_name = "jira_assign_issue"  # type: ignore
jira_assign_issue.input_schema = JiraAssignIssueInput  # type: ignore
jira_assign_issue.output_schema = JiraAssignIssueOutput  # type: ignore


async def jira_add_watcher(input: JiraAddWatcherInput) -> JiraAddWatcherOutput:
    """Add a watcher to a Jira issue."""
    try:
        service = get_jira_service()
        client = service._client
        await client.post(
            f"/rest/api/3/issue/{input.issue_key}/watchers",
            data=f'"{input.account_id}"',
        )
        return JiraAddWatcherOutput(success=True)
    except NotFoundError:
        return JiraAddWatcherOutput(
            success=False,
            error=f"Issue {input.issue_key} not found",
        )
    except AtlassianError as e:
        return JiraAddWatcherOutput(success=False, error=str(e))


jira_add_watcher.tool_name = "jira_add_watcher"  # type: ignore
jira_add_watcher.input_schema = JiraAddWatcherInput  # type: ignore
jira_add_watcher.output_schema = JiraAddWatcherOutput  # type: ignore


async def jira_remove_watcher(
    input: JiraRemoveWatcherInput,
) -> JiraRemoveWatcherOutput:
    """Remove a watcher from a Jira issue."""
    try:
        service = get_jira_service()
        client = service._client
        await client.delete(
            f"/rest/api/3/issue/{input.issue_key}/watchers",
            params={"accountId": input.account_id},
        )
        return JiraRemoveWatcherOutput(success=True)
    except NotFoundError:
        return JiraRemoveWatcherOutput(
            success=False,
            error=f"Issue {input.issue_key} not found",
        )
    except AtlassianError as e:
        return JiraRemoveWatcherOutput(success=False, error=str(e))


jira_remove_watcher.tool_name = "jira_remove_watcher"  # type: ignore
jira_remove_watcher.input_schema = JiraRemoveWatcherInput  # type: ignore
jira_remove_watcher.output_schema = JiraRemoveWatcherOutput  # type: ignore


async def jira_add_worklog(input: JiraAddWorklogInput) -> JiraAddWorklogOutput:
    """Add a worklog entry to a Jira issue."""
    try:
        service = get_jira_service()
        client = service._client
        response = await client.post(
            f"/rest/api/3/issue/{input.issue_key}/worklog",
            json={
                "timeSpent": input.time_spent,
                "started": input.started,
                "comment": service._create_adf(input.comment)
                if input.comment
                else None,
            },
        )
        data = response.json()
        return JiraAddWorklogOutput(
            success=True,
            worklog_id=data.get("id"),
        )
    except NotFoundError:
        return JiraAddWorklogOutput(
            success=False,
            error=f"Issue {input.issue_key} not found",
        )
    except AtlassianError as e:
        return JiraAddWorklogOutput(success=False, error=str(e))


jira_add_worklog.tool_name = "jira_add_worklog"  # type: ignore
jira_add_worklog.input_schema = JiraAddWorklogInput  # type: ignore
jira_add_worklog.output_schema = JiraAddWorklogOutput  # type: ignore


async def jira_link_issues(input: JiraLinkIssuesInput) -> JiraLinkIssuesOutput:
    """Create a link between two Jira issues."""
    try:
        service = get_jira_service()
        client = service._client
        await client.post(
            "/rest/api/3/issueLink",
            json={
                "type": {"name": input.link_type},
                "inwardIssue": {"key": input.inward_issue},
                "outwardIssue": {"key": input.outward_issue},
            },
        )
        return JiraLinkIssuesOutput(success=True)
    except NotFoundError as e:
        return JiraLinkIssuesOutput(success=False, error=str(e))
    except AtlassianError as e:
        return JiraLinkIssuesOutput(success=False, error=str(e))


jira_link_issues.tool_name = "jira_link_issues"  # type: ignore
jira_link_issues.input_schema = JiraLinkIssuesInput  # type: ignore
jira_link_issues.output_schema = JiraLinkIssuesOutput  # type: ignore


async def jira_delete_issue(
    input: JiraDeleteIssueInput,
) -> JiraDeleteIssueOutput:
    """Delete a Jira issue."""
    try:
        service = get_jira_service()
        await service.delete_issue(
            issue_key=input.issue_key,
            delete_subtasks=input.delete_subtasks,
        )
        return JiraDeleteIssueOutput(success=True)
    except NotFoundError:
        return JiraDeleteIssueOutput(
            success=False,
            error=f"Issue {input.issue_key} not found",
        )
    except AtlassianError as e:
        return JiraDeleteIssueOutput(success=False, error=str(e))


jira_delete_issue.tool_name = "jira_delete_issue"  # type: ignore
jira_delete_issue.input_schema = JiraDeleteIssueInput  # type: ignore
jira_delete_issue.output_schema = JiraDeleteIssueOutput  # type: ignore


async def jira_batch_create_issues(
    input: JiraBatchCreateIssuesInput,
) -> JiraBatchCreateIssuesOutput:
    """Create multiple Jira issues in batch."""
    try:
        service = get_jira_service()
        created_issues = []
        errors = []

        for i, issue_data in enumerate(input.issues):
            try:
                result = await service.create_issue(
                    project_key=issue_data.get("project_key", ""),
                    summary=issue_data.get("summary", ""),
                    issue_type=issue_data.get("issue_type", "Task"),
                    description=issue_data.get("description"),
                    priority=issue_data.get("priority"),
                    assignee=issue_data.get("assignee"),
                    labels=issue_data.get("labels"),
                    components=issue_data.get("components"),
                )
                created_issues.append(result)
            except AtlassianError as e:
                errors.append({"index": i, "error": str(e)})

        return JiraBatchCreateIssuesOutput(
            success=len(errors) == 0,
            created_issues=created_issues,
            errors=errors if errors else None,
        )
    except AtlassianError as e:
        return JiraBatchCreateIssuesOutput(success=False, error=str(e))


jira_batch_create_issues.tool_name = "jira_batch_create_issues"  # type: ignore
jira_batch_create_issues.input_schema = JiraBatchCreateIssuesInput  # type: ignore
jira_batch_create_issues.output_schema = JiraBatchCreateIssuesOutput  # type: ignore


async def jira_update_comment(
    input: JiraUpdateCommentInput,
) -> JiraUpdateCommentOutput:
    """Update a comment on a Jira issue."""
    try:
        service = get_jira_service()
        await service.update_comment(
            issue_key=input.issue_key,
            comment_id=input.comment_id,
            body=input.body,
        )
        return JiraUpdateCommentOutput(success=True)
    except NotFoundError:
        return JiraUpdateCommentOutput(
            success=False,
            error="Issue or comment not found",
        )
    except AtlassianError as e:
        return JiraUpdateCommentOutput(success=False, error=str(e))


jira_update_comment.tool_name = "jira_update_comment"  # type: ignore
jira_update_comment.input_schema = JiraUpdateCommentInput  # type: ignore
jira_update_comment.output_schema = JiraUpdateCommentOutput  # type: ignore


async def jira_delete_comment(
    input: JiraDeleteCommentInput,
) -> JiraDeleteCommentOutput:
    """Delete a comment from a Jira issue."""
    try:
        service = get_jira_service()
        await service.delete_comment(
            issue_key=input.issue_key,
            comment_id=input.comment_id,
        )
        return JiraDeleteCommentOutput(success=True)
    except NotFoundError:
        return JiraDeleteCommentOutput(
            success=False,
            error="Issue or comment not found",
        )
    except AtlassianError as e:
        return JiraDeleteCommentOutput(success=False, error=str(e))


jira_delete_comment.tool_name = "jira_delete_comment"  # type: ignore
jira_delete_comment.input_schema = JiraDeleteCommentInput  # type: ignore
jira_delete_comment.output_schema = JiraDeleteCommentOutput  # type: ignore


async def jira_unlink_issues(
    input: JiraUnlinkIssuesInput,
) -> JiraUnlinkIssuesOutput:
    """Delete an issue link."""
    try:
        service = get_jira_service()
        client = service._client
        await client.delete(f"/rest/api/3/issueLink/{input.link_id}")
        return JiraUnlinkIssuesOutput(success=True)
    except NotFoundError:
        return JiraUnlinkIssuesOutput(
            success=False,
            error=f"Link {input.link_id} not found",
        )
    except AtlassianError as e:
        return JiraUnlinkIssuesOutput(success=False, error=str(e))


jira_unlink_issues.tool_name = "jira_unlink_issues"  # type: ignore
jira_unlink_issues.input_schema = JiraUnlinkIssuesInput  # type: ignore
jira_unlink_issues.output_schema = JiraUnlinkIssuesOutput  # type: ignore
