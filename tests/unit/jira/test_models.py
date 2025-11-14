"""Tests for Jira models."""

import pytest
from pydantic import ValidationError

from atlassian_tools.jira.models import JiraGetIssueInput, JiraGetIssueOutput


class TestJiraGetIssueInput:
    """Test suite for JiraGetIssueInput model."""

    def test_valid_input_minimal(self) -> None:
        """Test creating input with only required field."""
        input_data = JiraGetIssueInput(issue_key="PROJ-123")

        assert input_data.issue_key == "PROJ-123"
        assert input_data.fields is None
        assert input_data.expand is None
        assert input_data.comment_limit == 10  # Default value

    def test_valid_input_full(self) -> None:
        """Test creating input with all fields."""
        input_data = JiraGetIssueInput(
            issue_key="TASK-789",
            fields="summary,status,assignee",
            expand="changelog,transitions",
            comment_limit=25,
        )

        assert input_data.issue_key == "TASK-789"
        assert input_data.fields == "summary,status,assignee"
        assert input_data.expand == "changelog,transitions"
        assert input_data.comment_limit == 25

    def test_valid_input_all_fields(self) -> None:
        """Test creating input with *all fields selector."""
        input_data = JiraGetIssueInput(
            issue_key="BUG-456",
            fields="*all",
            comment_limit=0,  # No comments
        )

        assert input_data.issue_key == "BUG-456"
        assert input_data.fields == "*all"
        assert input_data.comment_limit == 0

    def test_invalid_empty_issue_key(self) -> None:
        """Test that empty issue key is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            JiraGetIssueInput(issue_key="")

        errors = exc_info.value.errors()
        assert any(
            error["loc"] == ("issue_key",) and "at least 1 character" in error["msg"]
            for error in errors
        )

    def test_invalid_comment_limit_negative(self) -> None:
        """Test that negative comment limit is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            JiraGetIssueInput(issue_key="PROJ-123", comment_limit=-1)

        errors = exc_info.value.errors()
        assert any(
            error["loc"] == ("comment_limit",)
            and "greater than or equal to 0" in error["msg"]
            for error in errors
        )

    def test_invalid_comment_limit_too_high(self) -> None:
        """Test that comment limit over 100 is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            JiraGetIssueInput(issue_key="PROJ-123", comment_limit=101)

        errors = exc_info.value.errors()
        assert any(
            error["loc"] == ("comment_limit",)
            and "less than or equal to 100" in error["msg"]
            for error in errors
        )

    def test_serialization(self) -> None:
        """Test that input can be serialized to dict."""
        input_data = JiraGetIssueInput(
            issue_key="PROJ-123", fields="summary", comment_limit=5
        )

        serialized = input_data.model_dump()
        assert isinstance(serialized, dict)
        assert serialized["issue_key"] == "PROJ-123"
        assert serialized["fields"] == "summary"
        assert serialized["comment_limit"] == 5


class TestJiraGetIssueOutput:
    """Test suite for JiraGetIssueOutput model."""

    def test_success_output(self) -> None:
        """Test creating successful output."""
        output = JiraGetIssueOutput(
            success=True,
            issue={
                "key": "PROJ-123",
                "summary": "Test issue",
                "status": {"name": "Open"},
            },
        )

        assert output.success is True
        assert output.issue is not None
        assert output.issue["key"] == "PROJ-123"
        assert output.error is None

    def test_error_output(self) -> None:
        """Test creating error output."""
        output = JiraGetIssueOutput(
            success=False, error="Issue PROJ-999 not found"
        )

        assert output.success is False
        assert output.issue is None
        assert output.error == "Issue PROJ-999 not found"

    def test_serialization_success(self) -> None:
        """Test that successful output can be serialized."""
        output = JiraGetIssueOutput(
            success=True, issue={"key": "PROJ-123", "summary": "Test"}
        )

        serialized = output.model_dump()
        assert isinstance(serialized, dict)
        assert serialized["success"] is True
        assert serialized["issue"]["key"] == "PROJ-123"
        assert serialized["error"] is None

    def test_serialization_error(self) -> None:
        """Test that error output can be serialized."""
        output = JiraGetIssueOutput(success=False, error="API error")

        serialized = output.model_dump()
        assert isinstance(serialized, dict)
        assert serialized["success"] is False
        assert serialized["issue"] is None
        assert serialized["error"] == "API error"

    def test_exclude_none_values(self) -> None:
        """Test that None values can be excluded from serialization."""
        output = JiraGetIssueOutput(
            success=True, issue={"key": "PROJ-123"}
        )

        serialized = output.model_dump(exclude_none=True)
        assert "error" not in serialized  # None values excluded
        assert "issue" in serialized
        assert "success" in serialized
