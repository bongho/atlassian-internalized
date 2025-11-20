"""Tests for the service container."""

from unittest.mock import MagicMock, patch

import pytest

from atlassian_tools._core.container import (
    clear_service_cache,
    get_confluence_service,
    get_jira_service,
)


@pytest.fixture(autouse=True)
def clear_cache():
    """Clear service cache before each test."""
    clear_service_cache()
    yield
    clear_service_cache()


def test_get_jira_service_creates_singleton() -> None:
    """Test that get_jira_service creates a singleton instance."""
    with patch("atlassian_tools._core.http_client.get_jira_client") as mock_client:
        with patch("atlassian_tools.jira.service.JiraService") as mock_service_class:
            mock_client_instance = MagicMock()
            mock_service_instance = MagicMock()
            mock_client.return_value = mock_client_instance
            mock_service_class.return_value = mock_service_instance

            service1 = get_jira_service()
            service2 = get_jira_service()

            assert service1 is service2
            mock_client.assert_called_once()
            mock_service_class.assert_called_once_with(mock_client_instance)


def test_get_confluence_service_creates_singleton() -> None:
    """Test that get_confluence_service creates a singleton instance."""
    with patch(
        "atlassian_tools._core.http_client.get_confluence_client"
    ) as mock_client:
        with patch(
            "atlassian_tools.confluence.service.ConfluenceService"
        ) as mock_service_class:
            mock_client_instance = MagicMock()
            mock_service_instance = MagicMock()
            mock_client.return_value = mock_client_instance
            mock_service_class.return_value = mock_service_instance

            service1 = get_confluence_service()
            service2 = get_confluence_service()

            assert service1 is service2
            mock_client.assert_called_once()
            mock_service_class.assert_called_once_with(mock_client_instance)


def test_clear_service_cache() -> None:
    """Test that clear_service_cache resets singletons."""
    with patch("atlassian_tools._core.http_client.get_jira_client") as mock_jira_client:
        with patch("atlassian_tools.jira.service.JiraService") as mock_jira_service:
            with patch(
                "atlassian_tools._core.http_client.get_confluence_client"
            ) as mock_conf_client:
                with patch(
                    "atlassian_tools.confluence.service.ConfluenceService"
                ) as mock_conf_service:
                    mock_jira_client.return_value = MagicMock()
                    mock_conf_client.return_value = MagicMock()
                    # Create different mock instances for each call
                    mock_jira_service.side_effect = [MagicMock(), MagicMock()]
                    mock_conf_service.side_effect = [MagicMock(), MagicMock()]

                    # Create services
                    service1 = get_jira_service()
                    conf_service1 = get_confluence_service()

                    # Clear cache
                    clear_service_cache()

                    # Create services again
                    service2 = get_jira_service()
                    conf_service2 = get_confluence_service()

                    # Should be different instances after cache clear
                    assert service1 is not service2
                    assert conf_service1 is not conf_service2
                    assert mock_jira_client.call_count == 2
                    assert mock_conf_client.call_count == 2


def test_jira_service_initialization() -> None:
    """Test that JiraService is initialized with correct client."""
    with patch("atlassian_tools._core.http_client.get_jira_client") as mock_client:
        with patch("atlassian_tools.jira.service.JiraService") as mock_service_class:
            mock_client_instance = MagicMock()
            mock_client.return_value = mock_client_instance

            get_jira_service()

            mock_service_class.assert_called_once_with(mock_client_instance)


def test_confluence_service_initialization() -> None:
    """Test that ConfluenceService is initialized with correct client."""
    with patch(
        "atlassian_tools._core.http_client.get_confluence_client"
    ) as mock_client:
        with patch(
            "atlassian_tools.confluence.service.ConfluenceService"
        ) as mock_service_class:
            mock_client_instance = MagicMock()
            mock_client.return_value = mock_client_instance

            get_confluence_service()

            mock_service_class.assert_called_once_with(mock_client_instance)
