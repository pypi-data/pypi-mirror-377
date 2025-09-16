"""Tests for CLI module - focusing on core utility functions."""

import json
import os
from unittest.mock import Mock, patch

import pytest


# Now import CLI functions
from reprompt.cli import get_client, output_result

# RepromptAPIError removed - no longer in client module


class TestGetClient:
    """Test the get_client function which handles auth and client creation."""

    def test_get_client_with_explicit_params(self):
        """Test client creation with explicit API key and org slug."""
        with patch("reprompt.cli.RepromptClient") as mock_client_class:
            mock_client = Mock()
            mock_client_class.return_value = mock_client

            result = get_client(
                api_key="test-key", org_slug="test-org", base_url="https://api.test.com/v1", timeout=60.0
            )

            mock_client_class.assert_called_once_with(
                api_key="test-key", org_slug="test-org", base_url="https://api.test.com/v1", timeout=60.0
            )
            assert result == mock_client

    def test_get_client_from_env_vars(self):
        """Test client creation using environment variables."""
        with patch.dict(os.environ, {"REPROMPT_API_KEY": "env-key", "REPROMPT_ORG_SLUG": "env-org"}):
            with patch("reprompt.cli.RepromptClient") as mock_client_class:
                mock_client = Mock()
                mock_client_class.return_value = mock_client

                result = get_client()

                mock_client_class.assert_called_once_with(
                    api_key="env-key", org_slug="env-org", base_url="https://api.repromptai.com/v1", timeout=30.0
                )
                assert result == mock_client

    def test_get_client_missing_api_key(self):
        """Test that missing API key causes sys.exit(3)."""
        with patch.dict(os.environ, {}, clear=True):
            with patch("reprompt.cli.console") as mock_console:
                with pytest.raises(SystemExit) as exc_info:
                    get_client()

                assert exc_info.value.code == 3
                mock_console.print.assert_called_once_with(
                    "[red]Error: API key is required. Use --api-key or set REPROMPT_API_KEY environment variable.[/red]"
                )

    def test_get_client_missing_org_slug(self):
        """Test that missing org slug causes sys.exit(3)."""
        with patch.dict(os.environ, {"REPROMPT_API_KEY": "test-key"}, clear=True):
            with patch("reprompt.cli.console") as mock_console:
                with pytest.raises(SystemExit) as exc_info:
                    get_client()

                assert exc_info.value.code == 3
                mock_console.print.assert_called_once_with(
                    "[red]Error: Organization slug is required. "
                    "Use --org-slug or set REPROMPT_ORG_SLUG environment variable.[/red]"
                )

    def test_get_client_creation_error(self):
        """Test that client creation errors cause sys.exit(1)."""
        with patch.dict(os.environ, {"REPROMPT_API_KEY": "test-key", "REPROMPT_ORG_SLUG": "test-org"}):
            with patch("reprompt.cli.RepromptClient") as mock_client_class:
                mock_client_class.side_effect = ValueError("Connection failed")

                with patch("reprompt.cli.console") as mock_console:
                    with pytest.raises(SystemExit) as exc_info:
                        get_client()

                    assert exc_info.value.code == 1
                    mock_console.print.assert_called_once_with("[red]Configuration error: Connection failed[/red]")


# TestHandleApiError class removed - handle_api_error function no longer exists in cli.py
# TestLoadJsonInput class removed - load_json_input function no longer exists in cli.py


class TestOutputResult:
    """Test the output_result function."""

    def test_output_dict_json_mode(self):
        """Test outputting dict in JSON mode."""
        test_data = {"key": "value", "number": 42}

        with patch("builtins.print") as mock_print:
            output_result(test_data, output_format="json")

            mock_print.assert_called_once()
            # Should print JSON string
            printed_json = mock_print.call_args[0][0]
            assert json.loads(printed_json) == test_data

    def test_output_list_json_mode(self):
        """Test outputting list in JSON mode."""
        test_data = [{"key": "value"}, {"number": 42}]

        with patch("builtins.print") as mock_print:
            output_result(test_data, output_format="json")

            mock_print.assert_called_once()
            # Should print JSON string
            printed_json = mock_print.call_args[0][0]
            assert json.loads(printed_json) == test_data

    def test_output_pydantic_model_json_mode(self):
        """Test outputting Pydantic model in JSON mode."""
        mock_model = Mock()
        mock_model.model_dump.return_value = {"field": "value"}

        with patch("builtins.print") as mock_print:
            output_result(mock_model, output_format="json")

            mock_print.assert_called_once()
            # Should call model_dump() on the model and print as JSON
            printed_json = mock_print.call_args[0][0]
            assert json.loads(printed_json) == {"field": "value"}

    def test_output_dict_normal_mode_not_quiet(self):
        """Test outputting dict in normal mode (not quiet)."""
        test_data = {"key": "value", "number": 42}

        with patch("reprompt.cli.console") as mock_console:
            output_result(test_data, output_format="pretty", quiet=False)

            mock_console.print.assert_called_once()

    def test_output_pydantic_model_normal_mode(self):
        """Test outputting Pydantic model in pretty mode."""
        mock_model = Mock()
        mock_model.model_dump_json.return_value = '{"field": "value"}'

        with patch("reprompt.cli.console") as mock_console:
            output_result(mock_model, output_format="pretty", quiet=False)

            mock_console.print.assert_called_once()
            # Should call model_dump_json() on the model

    def test_output_quiet_mode(self):
        """Test that quiet mode suppresses output."""
        test_data = {"key": "value"}

        with patch("reprompt.cli.console") as mock_console:
            output_result(test_data, output_format="pretty", quiet=True)

            # Should not call console.print in quiet mode
            mock_console.print.assert_not_called()

    def test_output_string_fallback(self):
        """Test outputting non-dict, non-model objects."""
        test_data = "plain string"

        with patch("reprompt.cli.console") as mock_console:
            output_result(test_data, output_format="pretty", quiet=False)

            mock_console.print.assert_called_once_with(test_data)


if __name__ == "__main__":
    # Simple validation that we can import the functions
    print("CLI module imported successfully")
