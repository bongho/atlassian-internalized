"""Confluence tool implementations.

This module contains the actual implementation of Confluence tools that interact
with the Confluence API using the service layer.
"""

from atlassian_tools._core.container import get_confluence_service
from atlassian_tools._core.exceptions import AtlassianError, NotFoundError
from atlassian_tools.confluence.models import (
    ConfluenceAddCommentInput,
    ConfluenceAddCommentOutput,
    ConfluenceAddLabelInput,
    ConfluenceAddLabelOutput,
    ConfluenceCreatePageInput,
    ConfluenceCreatePageOutput,
    ConfluenceDeletePageInput,
    ConfluenceDeletePageOutput,
    ConfluenceGetCommentsInput,
    ConfluenceGetCommentsOutput,
    ConfluenceGetLabelsInput,
    ConfluenceGetLabelsOutput,
    ConfluenceGetPageAncestorsInput,
    ConfluenceGetPageAncestorsOutput,
    ConfluenceGetPageChildrenInput,
    ConfluenceGetPageChildrenOutput,
    ConfluenceGetPageInput,
    ConfluenceGetPageOutput,
    ConfluenceSearchInput,
    ConfluenceSearchOutput,
    ConfluenceUpdatePageInput,
    ConfluenceUpdatePageOutput,
)

# =============================================================================
# Read Tools
# =============================================================================


async def confluence_get_page(
    input: ConfluenceGetPageInput,
) -> ConfluenceGetPageOutput:
    """Get a Confluence page by ID."""
    try:
        service = get_confluence_service()
        page = await service.get_page(
            page_id=input.page_id,
            expand=input.expand,
        )
        return ConfluenceGetPageOutput(success=True, page=page)
    except NotFoundError:
        return ConfluenceGetPageOutput(
            success=False,
            error=f"Page {input.page_id} not found",
        )
    except AtlassianError as e:
        return ConfluenceGetPageOutput(success=False, error=str(e))


confluence_get_page.tool_name = "confluence_get_page"  # type: ignore
confluence_get_page.input_schema = ConfluenceGetPageInput  # type: ignore
confluence_get_page.output_schema = ConfluenceGetPageOutput  # type: ignore


async def confluence_search(
    input: ConfluenceSearchInput,
) -> ConfluenceSearchOutput:
    """Search Confluence using CQL."""
    try:
        service = get_confluence_service()
        result = await service.search(
            cql=input.cql,
            limit=input.limit,
            start=input.start,
        )
        return ConfluenceSearchOutput(
            success=True,
            results=result.get("results", []),
            total=result.get("total", 0),
        )
    except AtlassianError as e:
        return ConfluenceSearchOutput(success=False, error=str(e))


confluence_search.tool_name = "confluence_search"  # type: ignore
confluence_search.input_schema = ConfluenceSearchInput  # type: ignore
confluence_search.output_schema = ConfluenceSearchOutput  # type: ignore


async def confluence_get_page_children(
    input: ConfluenceGetPageChildrenInput,
) -> ConfluenceGetPageChildrenOutput:
    """Get child pages of a Confluence page."""
    try:
        service = get_confluence_service()
        children = await service.get_page_children(
            page_id=input.page_id,
            limit=input.limit,
        )
        return ConfluenceGetPageChildrenOutput(
            success=True,
            children=children,
        )
    except NotFoundError:
        return ConfluenceGetPageChildrenOutput(
            success=False,
            error=f"Page {input.page_id} not found",
        )
    except AtlassianError as e:
        return ConfluenceGetPageChildrenOutput(success=False, error=str(e))


confluence_get_page_children.tool_name = "confluence_get_page_children"  # type: ignore
confluence_get_page_children.input_schema = ConfluenceGetPageChildrenInput  # type: ignore
confluence_get_page_children.output_schema = ConfluenceGetPageChildrenOutput  # type: ignore


async def confluence_get_page_ancestors(
    input: ConfluenceGetPageAncestorsInput,
) -> ConfluenceGetPageAncestorsOutput:
    """Get ancestor pages of a Confluence page."""
    try:
        service = get_confluence_service()
        ancestors = await service.get_page_ancestors(page_id=input.page_id)
        return ConfluenceGetPageAncestorsOutput(
            success=True,
            ancestors=ancestors,
        )
    except NotFoundError:
        return ConfluenceGetPageAncestorsOutput(
            success=False,
            error=f"Page {input.page_id} not found",
        )
    except AtlassianError as e:
        return ConfluenceGetPageAncestorsOutput(success=False, error=str(e))


confluence_get_page_ancestors.tool_name = "confluence_get_page_ancestors"  # type: ignore
confluence_get_page_ancestors.input_schema = ConfluenceGetPageAncestorsInput  # type: ignore
confluence_get_page_ancestors.output_schema = ConfluenceGetPageAncestorsOutput  # type: ignore


async def confluence_get_labels(
    input: ConfluenceGetLabelsInput,
) -> ConfluenceGetLabelsOutput:
    """Get labels for a Confluence page."""
    try:
        service = get_confluence_service()
        labels = await service.get_labels(page_id=input.page_id)
        return ConfluenceGetLabelsOutput(success=True, labels=labels)
    except NotFoundError:
        return ConfluenceGetLabelsOutput(
            success=False,
            error=f"Page {input.page_id} not found",
        )
    except AtlassianError as e:
        return ConfluenceGetLabelsOutput(success=False, error=str(e))


confluence_get_labels.tool_name = "confluence_get_labels"  # type: ignore
confluence_get_labels.input_schema = ConfluenceGetLabelsInput  # type: ignore
confluence_get_labels.output_schema = ConfluenceGetLabelsOutput  # type: ignore


async def confluence_get_comments(
    input: ConfluenceGetCommentsInput,
) -> ConfluenceGetCommentsOutput:
    """Get comments for a Confluence page."""
    try:
        service = get_confluence_service()
        comments = await service.get_comments(
            page_id=input.page_id,
            limit=input.limit,
        )
        return ConfluenceGetCommentsOutput(success=True, comments=comments)
    except NotFoundError:
        return ConfluenceGetCommentsOutput(
            success=False,
            error=f"Page {input.page_id} not found",
        )
    except AtlassianError as e:
        return ConfluenceGetCommentsOutput(success=False, error=str(e))


confluence_get_comments.tool_name = "confluence_get_comments"  # type: ignore
confluence_get_comments.input_schema = ConfluenceGetCommentsInput  # type: ignore
confluence_get_comments.output_schema = ConfluenceGetCommentsOutput  # type: ignore


# =============================================================================
# Write Tools
# =============================================================================


async def confluence_create_page(
    input: ConfluenceCreatePageInput,
) -> ConfluenceCreatePageOutput:
    """Create a new Confluence page."""
    try:
        service = get_confluence_service()
        result = await service.create_page(
            space_key=input.space_key,
            title=input.title,
            body=input.body,
            parent_id=input.parent_id,
        )
        return ConfluenceCreatePageOutput(
            success=True,
            page_id=result.get("id"),
            page_url=result.get("url"),
        )
    except AtlassianError as e:
        return ConfluenceCreatePageOutput(success=False, error=str(e))


confluence_create_page.tool_name = "confluence_create_page"  # type: ignore
confluence_create_page.input_schema = ConfluenceCreatePageInput  # type: ignore
confluence_create_page.output_schema = ConfluenceCreatePageOutput  # type: ignore


async def confluence_update_page(
    input: ConfluenceUpdatePageInput,
) -> ConfluenceUpdatePageOutput:
    """Update an existing Confluence page."""
    try:
        service = get_confluence_service()
        new_version = await service.update_page(
            page_id=input.page_id,
            version_number=input.version_number,
            title=input.title,
            body=input.body,
        )
        return ConfluenceUpdatePageOutput(
            success=True,
            new_version=new_version,
        )
    except NotFoundError:
        return ConfluenceUpdatePageOutput(
            success=False,
            error=f"Page {input.page_id} not found",
        )
    except AtlassianError as e:
        return ConfluenceUpdatePageOutput(success=False, error=str(e))


confluence_update_page.tool_name = "confluence_update_page"  # type: ignore
confluence_update_page.input_schema = ConfluenceUpdatePageInput  # type: ignore
confluence_update_page.output_schema = ConfluenceUpdatePageOutput  # type: ignore


async def confluence_delete_page(
    input: ConfluenceDeletePageInput,
) -> ConfluenceDeletePageOutput:
    """Delete a Confluence page."""
    try:
        service = get_confluence_service()
        await service.delete_page(page_id=input.page_id)
        return ConfluenceDeletePageOutput(success=True)
    except NotFoundError:
        return ConfluenceDeletePageOutput(
            success=False,
            error=f"Page {input.page_id} not found",
        )
    except AtlassianError as e:
        return ConfluenceDeletePageOutput(success=False, error=str(e))


confluence_delete_page.tool_name = "confluence_delete_page"  # type: ignore
confluence_delete_page.input_schema = ConfluenceDeletePageInput  # type: ignore
confluence_delete_page.output_schema = ConfluenceDeletePageOutput  # type: ignore


async def confluence_add_label(
    input: ConfluenceAddLabelInput,
) -> ConfluenceAddLabelOutput:
    """Add a label to a Confluence page."""
    try:
        service = get_confluence_service()
        await service.add_label(
            page_id=input.page_id,
            label=input.label,
        )
        return ConfluenceAddLabelOutput(success=True)
    except NotFoundError:
        return ConfluenceAddLabelOutput(
            success=False,
            error=f"Page {input.page_id} not found",
        )
    except AtlassianError as e:
        return ConfluenceAddLabelOutput(success=False, error=str(e))


confluence_add_label.tool_name = "confluence_add_label"  # type: ignore
confluence_add_label.input_schema = ConfluenceAddLabelInput  # type: ignore
confluence_add_label.output_schema = ConfluenceAddLabelOutput  # type: ignore


async def confluence_add_comment(
    input: ConfluenceAddCommentInput,
) -> ConfluenceAddCommentOutput:
    """Add a comment to a Confluence page."""
    try:
        service = get_confluence_service()
        result = await service.add_comment(
            page_id=input.page_id,
            body=input.body,
        )
        return ConfluenceAddCommentOutput(
            success=True,
            comment_id=result.get("id"),
        )
    except AtlassianError as e:
        return ConfluenceAddCommentOutput(success=False, error=str(e))


confluence_add_comment.tool_name = "confluence_add_comment"  # type: ignore
confluence_add_comment.input_schema = ConfluenceAddCommentInput  # type: ignore
confluence_add_comment.output_schema = ConfluenceAddCommentOutput  # type: ignore
