import pytest
import os
import json
import urllib.request
import urllib.error
from unittest.mock import Mock, patch, MagicMock
from io import StringIO
import sys

from dfdrift.alerters import SlackAlerter


class TestSlackAlerter:
    def test_init_with_token_argument(self):
        """Test SlackAlerter initialization with token argument"""
        with patch('dfdrift.alerters.SlackAlerter._import_slack_sdk') as mock_import:
            mock_client = Mock()
            mock_import.return_value = mock_client
            
            alerter = SlackAlerter(channel="#alerts", token="test-token")
            
            assert alerter.token == "test-token"
            assert alerter.channel == "#alerts"
            assert alerter.client == mock_client

    def test_init_with_env_token(self):
        """Test SlackAlerter initialization with environment variable token"""
        with patch.dict(os.environ, {'SLACK_BOT_TOKEN': 'env-token'}):
            with patch('dfdrift.alerters.SlackAlerter._import_slack_sdk') as mock_import:
                mock_client = Mock()
                mock_import.return_value = mock_client
                
                alerter = SlackAlerter(channel="#general")
                
                assert alerter.token == "env-token"
                assert alerter.channel == "#general"

    def test_init_no_token_raises_error(self):
        """Test SlackAlerter raises error when no token provided"""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError) as exc_info:
                SlackAlerter(channel="#test")
            
            assert "Either SLACK_WEBHOOK_URL or SLACK_BOT_TOKEN must be provided" in str(exc_info.value)

    def test_init_no_channel_raises_error(self):
        """Test SlackAlerter raises error when no channel provided"""
        with patch.dict(os.environ, {}, clear=True):  # Clear environment variables
            with pytest.raises(ValueError) as exc_info:
                SlackAlerter(token="test-token")  # No channel argument or env var
            
            assert "SLACK_CHANNEL must be provided when using bot token" in str(exc_info.value)

    def test_init_with_env_channel(self):
        """Test SlackAlerter initialization with environment variable channel"""
        with patch.dict(os.environ, {'SLACK_CHANNEL': '#env-channel'}):
            with patch('dfdrift.alerters.SlackAlerter._import_slack_sdk') as mock_import:
                mock_client = Mock()
                mock_import.return_value = mock_client
                
                alerter = SlackAlerter(token="test-token")
                
                assert alerter.token == "test-token"
                assert alerter.channel == "#env-channel"
                assert alerter.client == mock_client
    
    def test_init_with_both_env_vars(self):
        """Test SlackAlerter initialization with both token and channel from environment"""
        with patch.dict(os.environ, {'SLACK_BOT_TOKEN': 'env-token', 'SLACK_CHANNEL': '#env-channel'}):
            with patch('dfdrift.alerters.SlackAlerter._import_slack_sdk') as mock_import:
                mock_client = Mock()
                mock_import.return_value = mock_client
                
                alerter = SlackAlerter()  # No arguments, use env vars
                
                assert alerter.token == "env-token"
                assert alerter.channel == "#env-channel"
                assert alerter.client == mock_client

    def test_init_missing_slack_sdk_raises_import_error(self):
        """Test SlackAlerter raises ImportError when slack-sdk not installed"""
        with patch('dfdrift.alerters.SlackAlerter._import_slack_sdk') as mock_import:
            mock_import.side_effect = ImportError("No module named 'slack_sdk'")
            
            with pytest.raises(ImportError) as exc_info:
                SlackAlerter(channel="#test", token="test-token")
            
            # The actual ImportError from the mock is re-raised
            assert "No module named 'slack_sdk'" in str(exc_info.value)

    def test_alert_success(self):
        """Test successful Slack alert"""
        with patch('dfdrift.alerters.SlackAlerter._import_slack_sdk') as mock_import:
            mock_client = Mock()
            mock_client.chat_postMessage.return_value = {"ok": True}
            mock_import.return_value = mock_client
            
            alerter = SlackAlerter(channel="#alerts", token="test-token")
            
            old_schema = {"columns": {"name": {"dtype": "object"}}, "shape": [3, 1]}
            new_schema = {"columns": {"name": {"dtype": "int64"}}, "shape": [3, 1]}
            
            alerter.alert("Test message", "test.py:10", old_schema, new_schema)
            
            mock_client.chat_postMessage.assert_called_once()
            call_args = mock_client.chat_postMessage.call_args
            
            assert call_args[1]["channel"] == "#alerts"
            assert "DataFrame Schema Drift Detected" in call_args[1]["text"]
            assert "test.py:10" in call_args[1]["text"]
            assert "Test message" in call_args[1]["text"]

    def test_alert_with_column_changes(self):
        """Test Slack alert with column additions and removals"""
        with patch('dfdrift.alerters.SlackAlerter._import_slack_sdk') as mock_import:
            mock_client = Mock()
            mock_client.chat_postMessage.return_value = {"ok": True}
            mock_import.return_value = mock_client
            
            alerter = SlackAlerter(channel="#alerts", token="test-token")
            
            old_schema = {
                "columns": {"name": {"dtype": "object"}, "age": {"dtype": "int64"}},
                "shape": [3, 2]
            }
            new_schema = {
                "columns": {"name": {"dtype": "object"}, "email": {"dtype": "object"}},
                "shape": [3, 2]
            }
            
            alerter.alert("Schema changed", "test.py:15", old_schema, new_schema)
            
            call_args = mock_client.chat_postMessage.call_args
            message_text = call_args[1]["text"]
            
            assert "Added columns:" in message_text
            assert "`email`" in message_text
            assert "Removed columns:" in message_text
            assert "`age`" in message_text

    def test_alert_slack_api_error_fallback(self):
        """Test fallback to stderr when Slack API returns error"""
        with patch('dfdrift.alerters.SlackAlerter._import_slack_sdk') as mock_import:
            mock_client = Mock()
            mock_client.chat_postMessage.return_value = {"ok": False, "error": "channel_not_found"}
            mock_import.return_value = mock_client
            
            alerter = SlackAlerter(channel="#alerts", token="test-token")
            
            captured_output = StringIO()
            with patch('sys.stderr', captured_output):
                alerter.alert("Test message", "test.py:20", {}, {})
            
            output = captured_output.getvalue()
            assert "Error sending Slack notification:" in output
            assert "Bot message failed: channel_not_found" in output
            assert "WARNING: Test message" in output
            assert "Location: test.py:20" in output

    def test_alert_exception_fallback(self):
        """Test fallback to stderr when exception occurs"""
        with patch('dfdrift.alerters.SlackAlerter._import_slack_sdk') as mock_import:
            mock_client = Mock()
            mock_client.chat_postMessage.side_effect = Exception("Network error")
            mock_import.return_value = mock_client
            
            alerter = SlackAlerter(channel="#alerts", token="test-token")
            
            captured_output = StringIO()
            with patch('sys.stderr', captured_output):
                alerter.alert("Test message", "test.py:25", {}, {})
            
            output = captured_output.getvalue()
            assert "Error sending Slack notification: Network error" in output
            assert "WARNING: Test message" in output
            assert "Location: test.py:25" in output

    def test_channel_is_required(self):
        """Test channel parameter is required"""
        with patch('dfdrift.alerters.SlackAlerter._import_slack_sdk') as mock_import:
            mock_client = Mock()
            mock_import.return_value = mock_client
            
            alerter = SlackAlerter(channel="#custom-channel", token="test-token")
            assert alerter.channel == "#custom-channel"

    # Webhook tests
    def test_init_with_webhook_url(self):
        """Test SlackAlerter initialization with webhook URL"""
        webhook_url = "https://hooks.slack.com/services/test/webhook"
        alerter = SlackAlerter(webhook_url=webhook_url)
        
        assert alerter.webhook_url == webhook_url
        assert alerter.client is None  # No client needed for webhooks

    def test_init_with_env_webhook_url(self):
        """Test SlackAlerter initialization with environment variable webhook URL"""
        webhook_url = "https://hooks.slack.com/services/env/webhook"
        with patch.dict(os.environ, {'SLACK_WEBHOOK_URL': webhook_url}):
            alerter = SlackAlerter()
            
            assert alerter.webhook_url == webhook_url
            assert alerter.client is None

    def test_webhook_priority_over_token(self):
        """Test webhook URL takes priority over bot token"""
        webhook_url = "https://hooks.slack.com/services/priority/test"
        with patch.dict(os.environ, {'SLACK_WEBHOOK_URL': webhook_url, 'SLACK_BOT_TOKEN': 'token'}):
            alerter = SlackAlerter()
            
            assert alerter.webhook_url == webhook_url
            assert alerter.client is None  # Should not create client when webhook is available

    def test_webhook_alert_success(self):
        """Test successful webhook alert"""
        webhook_url = "https://hooks.slack.com/services/test/webhook"
        
        with patch('urllib.request.urlopen') as mock_urlopen:
            mock_response = Mock()
            mock_response.status = 200
            mock_urlopen.return_value.__enter__.return_value = mock_response
            
            alerter = SlackAlerter(webhook_url=webhook_url)
            
            old_schema = {"columns": {"name": {"dtype": "object"}}, "shape": [3, 1]}
            new_schema = {"columns": {"name": {"dtype": "int64"}}, "shape": [3, 1]}
            
            alerter.alert("Test webhook message", "test.py:10", old_schema, new_schema)
            
            # Verify the request was made
            mock_urlopen.assert_called_once()
            call_args = mock_urlopen.call_args[0][0]  # Get the Request object
            
            assert call_args.full_url == webhook_url
            assert call_args.headers['Content-type'] == 'application/json'
            
            # Verify the payload
            data = json.loads(call_args.data.decode('utf-8'))
            assert "DataFrame Schema Drift Detected" in data["text"]
            assert "test.py:10" in data["text"]
            assert "Test webhook message" in data["text"]
            assert data["mrkdwn"] is True

    def test_webhook_alert_with_column_changes(self):
        """Test webhook alert with column changes"""
        webhook_url = "https://hooks.slack.com/services/test/webhook"
        
        with patch('urllib.request.urlopen') as mock_urlopen:
            mock_response = Mock()
            mock_response.status = 200
            mock_urlopen.return_value.__enter__.return_value = mock_response
            
            alerter = SlackAlerter(webhook_url=webhook_url)
            
            old_schema = {
                "columns": {"name": {"dtype": "object"}, "age": {"dtype": "int64"}},
                "shape": [3, 2]
            }
            new_schema = {
                "columns": {"name": {"dtype": "object"}, "email": {"dtype": "object"}},
                "shape": [3, 2]
            }
            
            alerter.alert("Schema changed", "test.py:15", old_schema, new_schema)
            
            # Verify the payload contains column change information
            call_args = mock_urlopen.call_args[0][0]
            data = json.loads(call_args.data.decode('utf-8'))
            message_text = data["text"]
            
            assert "Added columns:" in message_text
            assert "`email`" in message_text
            assert "Removed columns:" in message_text
            assert "`age`" in message_text

    def test_webhook_alert_http_error_fallback(self):
        """Test fallback to stderr when webhook returns HTTP error"""
        webhook_url = "https://hooks.slack.com/services/test/webhook"
        
        with patch('urllib.request.urlopen') as mock_urlopen:
            mock_response = Mock()
            mock_response.status = 404
            mock_urlopen.return_value.__enter__.return_value = mock_response
            
            alerter = SlackAlerter(webhook_url=webhook_url)
            
            captured_output = StringIO()
            with patch('sys.stderr', captured_output):
                alerter.alert("Test message", "test.py:20", {}, {})
            
            output = captured_output.getvalue()
            assert "Error sending Slack notification:" in output
            assert "WARNING: Test message" in output
            assert "Location: test.py:20" in output

    def test_webhook_alert_network_error_fallback(self):
        """Test fallback to stderr when network error occurs"""
        webhook_url = "https://hooks.slack.com/services/test/webhook"
        
        with patch('urllib.request.urlopen') as mock_urlopen:
            mock_urlopen.side_effect = urllib.error.URLError("Network unreachable")
            
            alerter = SlackAlerter(webhook_url=webhook_url)
            
            captured_output = StringIO()
            with patch('sys.stderr', captured_output):
                alerter.alert("Test message", "test.py:25", {}, {})
            
            output = captured_output.getvalue()
            assert "Error sending Slack notification:" in output
            assert "WARNING: Test message" in output
            assert "Location: test.py:25" in output

    def test_no_webhook_no_token_raises_error(self):
        """Test SlackAlerter raises error when neither webhook nor token provided"""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError) as exc_info:
                SlackAlerter()
            
            assert "Either SLACK_WEBHOOK_URL or SLACK_BOT_TOKEN must be provided" in str(exc_info.value)