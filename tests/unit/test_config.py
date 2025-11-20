"""Unit tests for configuration management."""

from unittest.mock import MagicMock, patch

import pytest
from pydantic import ValidationError

from atlassian_tools._core.config import (
    ConfluenceConfig,
    JiraConfig,
    clear_config_cache,
    get_confluence_config,
    get_jira_config,
)


@pytest.fixture(autouse=True)
def disable_env_file():
    """Disable .env file loading for all tests."""
    # Mock the pydantic-settings behavior to not load .env files
    original_config = JiraConfig.model_config
    original_confluence_config = ConfluenceConfig.model_config

    JiraConfig.model_config = {
        **original_config,
        "env_file": None,
    }
    ConfluenceConfig.model_config = {
        **original_confluence_config,
        "env_file": None,
    }

    clear_config_cache()
    yield

    JiraConfig.model_config = original_config
    ConfluenceConfig.model_config = original_confluence_config
    clear_config_cache()


class TestJiraConfig:
    """Test Jira configuration."""

    def test_valid_config_from_env(self) -> None:
        """Test creating config with valid environment variables."""
        with patch.dict(
            "os.environ",
            {
                "JIRA_URL": "https://test.atlassian.net",
                "JIRA_USERNAME": "test@example.com",
                "JIRA_API_TOKEN": "test-token",
            },
        ):
            clear_config_cache()
            config = JiraConfig()
            assert config.url == "https://test.atlassian.net"
            assert config.username == "test@example.com"
            assert config.api_token == "test-token"
            assert config.timeout == 30  # default
            assert config.max_retries == 3  # default

    def test_missing_url_raises_error(self) -> None:
        """Test missing JIRA_URL raises ValidationError."""
        with patch.dict(
            "os.environ",
            {
                "JIRA_USERNAME": "test@example.com",
                "JIRA_API_TOKEN": "test-token",
            },
            clear=True,
        ):
            clear_config_cache()
            with pytest.raises(ValidationError, match="url"):
                JiraConfig()

    def test_missing_username_raises_error(self) -> None:
        """Test missing JIRA_USERNAME raises ValidationError."""
        with patch.dict(
            "os.environ",
            {
                "JIRA_URL": "https://test.atlassian.net",
                "JIRA_API_TOKEN": "test-token",
            },
            clear=True,
        ):
            clear_config_cache()
            with pytest.raises(ValidationError, match="username"):
                JiraConfig()

    def test_missing_api_token_raises_error(self) -> None:
        """Test missing JIRA_API_TOKEN raises ValidationError."""
        with patch.dict(
            "os.environ",
            {
                "JIRA_URL": "https://test.atlassian.net",
                "JIRA_USERNAME": "test@example.com",
            },
            clear=True,
        ):
            clear_config_cache()
            with pytest.raises(ValidationError, match="api_token"):
                JiraConfig()

    def test_default_timeout_value(self) -> None:
        """Test default timeout value when not specified."""
        with patch.dict(
            "os.environ",
            {
                "JIRA_URL": "https://test.atlassian.net",
                "JIRA_USERNAME": "test@example.com",
                "JIRA_API_TOKEN": "test-token",
            },
        ):
            clear_config_cache()
            config = JiraConfig()
            assert config.timeout == 30

    def test_custom_timeout_value(self) -> None:
        """Test custom timeout value from environment."""
        with patch.dict(
            "os.environ",
            {
                "JIRA_URL": "https://test.atlassian.net",
                "JIRA_USERNAME": "test@example.com",
                "JIRA_API_TOKEN": "test-token",
                "JIRA_TIMEOUT": "60",
            },
        ):
            clear_config_cache()
            config = JiraConfig()
            assert config.timeout == 60

    def test_custom_max_retries(self) -> None:
        """Test custom max_retries value from environment."""
        with patch.dict(
            "os.environ",
            {
                "JIRA_URL": "https://test.atlassian.net",
                "JIRA_USERNAME": "test@example.com",
                "JIRA_API_TOKEN": "test-token",
                "JIRA_MAX_RETRIES": "5",
            },
        ):
            clear_config_cache()
            config = JiraConfig()
            assert config.max_retries == 5

    def test_extra_fields_ignored(self) -> None:
        """Test extra environment variables are ignored."""
        with patch.dict(
            "os.environ",
            {
                "JIRA_URL": "https://test.atlassian.net",
                "JIRA_USERNAME": "test@example.com",
                "JIRA_API_TOKEN": "test-token",
                "JIRA_EXTRA_FIELD": "should-be-ignored",
            },
        ):
            clear_config_cache()
            config = JiraConfig()
            assert not hasattr(config, "extra_field")


class TestConfluenceConfig:
    """Test Confluence configuration."""

    def test_valid_config_from_env(self) -> None:
        """Test creating config with valid environment variables."""
        with patch.dict(
            "os.environ",
            {
                "CONFLUENCE_URL": "https://test.atlassian.net/wiki",
                "CONFLUENCE_USERNAME": "test@example.com",
                "CONFLUENCE_API_TOKEN": "test-token",
            },
        ):
            clear_config_cache()
            config = ConfluenceConfig()
            assert config.url == "https://test.atlassian.net/wiki"
            assert config.username == "test@example.com"
            assert config.api_token == "test-token"
            assert config.timeout == 30  # default
            assert config.max_retries == 3  # default

    def test_missing_url_raises_error(self) -> None:
        """Test missing CONFLUENCE_URL raises ValidationError."""
        with patch.dict(
            "os.environ",
            {
                "CONFLUENCE_USERNAME": "test@example.com",
                "CONFLUENCE_API_TOKEN": "test-token",
            },
            clear=True,
        ):
            clear_config_cache()
            with pytest.raises(ValidationError, match="url"):
                ConfluenceConfig()

    def test_missing_username_raises_error(self) -> None:
        """Test missing CONFLUENCE_USERNAME raises ValidationError."""
        with patch.dict(
            "os.environ",
            {
                "CONFLUENCE_URL": "https://test.atlassian.net/wiki",
                "CONFLUENCE_API_TOKEN": "test-token",
            },
            clear=True,
        ):
            clear_config_cache()
            with pytest.raises(ValidationError, match="username"):
                ConfluenceConfig()

    def test_missing_api_token_raises_error(self) -> None:
        """Test missing CONFLUENCE_API_TOKEN raises ValidationError."""
        with patch.dict(
            "os.environ",
            {
                "CONFLUENCE_URL": "https://test.atlassian.net/wiki",
                "CONFLUENCE_USERNAME": "test@example.com",
            },
            clear=True,
        ):
            clear_config_cache()
            with pytest.raises(ValidationError, match="api_token"):
                ConfluenceConfig()

    def test_custom_timeout_value(self) -> None:
        """Test custom timeout value from environment."""
        with patch.dict(
            "os.environ",
            {
                "CONFLUENCE_URL": "https://test.atlassian.net/wiki",
                "CONFLUENCE_USERNAME": "test@example.com",
                "CONFLUENCE_API_TOKEN": "test-token",
                "CONFLUENCE_TIMEOUT": "45",
            },
        ):
            clear_config_cache()
            config = ConfluenceConfig()
            assert config.timeout == 45


class TestConfigCaching:
    """Test configuration caching behavior."""

    def test_jira_config_caching(self) -> None:
        """Test get_jira_config returns cached instance."""
        with patch.dict(
            "os.environ",
            {
                "JIRA_URL": "https://test.atlassian.net",
                "JIRA_USERNAME": "test@example.com",
                "JIRA_API_TOKEN": "test-token",
            },
        ):
            clear_config_cache()
            config1 = get_jira_config()
            config2 = get_jira_config()
            assert config1 is config2  # Same instance due to caching

    def test_confluence_config_caching(self) -> None:
        """Test get_confluence_config returns cached instance."""
        with patch.dict(
            "os.environ",
            {
                "CONFLUENCE_URL": "https://test.atlassian.net/wiki",
                "CONFLUENCE_USERNAME": "test@example.com",
                "CONFLUENCE_API_TOKEN": "test-token",
            },
        ):
            clear_config_cache()
            config1 = get_confluence_config()
            config2 = get_confluence_config()
            assert config1 is config2  # Same instance due to caching

    def test_clear_jira_config_cache(self) -> None:
        """Test clear_config_cache reloads Jira config."""
        with patch.dict(
            "os.environ",
            {
                "JIRA_URL": "https://test1.atlassian.net",
                "JIRA_USERNAME": "test@example.com",
                "JIRA_API_TOKEN": "test-token",
            },
        ):
            clear_config_cache()
            config1 = get_jira_config()
            assert config1.url == "https://test1.atlassian.net"

        with patch.dict(
            "os.environ",
            {
                "JIRA_URL": "https://test2.atlassian.net",
                "JIRA_USERNAME": "test@example.com",
                "JIRA_API_TOKEN": "test-token",
            },
        ):
            # Without clearing cache, should return old cached value
            config2 = get_jira_config()
            assert config2.url == "https://test1.atlassian.net"  # Still cached

            # After clearing cache, should get new value
            clear_config_cache()
            config3 = get_jira_config()
            assert config3.url == "https://test2.atlassian.net"

    def test_clear_confluence_config_cache(self) -> None:
        """Test clear_config_cache reloads Confluence config."""
        with patch.dict(
            "os.environ",
            {
                "CONFLUENCE_URL": "https://test1.atlassian.net/wiki",
                "CONFLUENCE_USERNAME": "test@example.com",
                "CONFLUENCE_API_TOKEN": "test-token",
            },
        ):
            clear_config_cache()
            config1 = get_confluence_config()
            assert config1.url == "https://test1.atlassian.net/wiki"

        with patch.dict(
            "os.environ",
            {
                "CONFLUENCE_URL": "https://test2.atlassian.net/wiki",
                "CONFLUENCE_USERNAME": "test@example.com",
                "CONFLUENCE_API_TOKEN": "test-token",
            },
        ):
            clear_config_cache()
            config2 = get_confluence_config()
            assert config2.url == "https://test2.atlassian.net/wiki"
