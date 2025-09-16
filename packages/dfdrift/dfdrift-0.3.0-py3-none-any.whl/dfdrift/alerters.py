import os
import sys
import json
import urllib.request
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class Alerter(ABC):
    @abstractmethod
    def alert(self, message: str, location_key: str, old_schema: Dict[str, Any], new_schema: Dict[str, Any]) -> None:
        pass


class StderrAlerter(Alerter):
    def alert(self, message: str, location_key: str, old_schema: Dict[str, Any], new_schema: Dict[str, Any]) -> None:
        print(f"WARNING: {message}", file=sys.stderr)
        print(f"Location: {location_key}", file=sys.stderr)


class SlackAlerter(Alerter):
    def __init__(self, webhook_url: Optional[str] = None, channel: Optional[str] = None, token: Optional[str] = None):
        # Priority: webhook_url > token
        self.webhook_url = webhook_url or os.getenv("SLACK_WEBHOOK_URL")
        self.token = token or os.getenv("SLACK_BOT_TOKEN")
        self.channel = channel or os.getenv("SLACK_CHANNEL")
        
        if self.webhook_url:
            # Using webhook - no additional validation needed
            self.client = None
        else:
            # Using bot token - need both token and channel
            if not self.token:
                raise ValueError("Either SLACK_WEBHOOK_URL or SLACK_BOT_TOKEN must be provided")
            
            if not self.channel:
                raise ValueError("SLACK_CHANNEL must be provided when using bot token")
            
            self.client = self._import_slack_sdk()
    
    def _import_slack_sdk(self):
        """Import slack SDK and create client"""
        try:
            from slack_sdk import WebClient
            return WebClient(token=self.token)
        except ImportError:
            raise ImportError("slack-sdk package is required for bot token authentication. Install with: pip install slack-sdk")
    
    def _send_webhook_message(self, slack_message: str) -> None:
        """Send message via incoming webhook"""
        if not self.webhook_url:
            raise ValueError("Webhook URL is not configured")
            
        payload = {
            "text": slack_message,
            "mrkdwn": True
        }
        
        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(
            self.webhook_url,
            data=data,
            headers={'Content-Type': 'application/json'}
        )
        
        with urllib.request.urlopen(req) as response:
            if response.status != 200:
                raise Exception(f"Webhook request failed with status {response.status}")
    
    def _send_bot_message(self, slack_message: str) -> None:
        """Send message via bot token"""
        if not self.client:
            raise ValueError("Slack client is not configured")
            
        response = self.client.chat_postMessage(
            channel=self.channel,
            text=slack_message,
            mrkdwn=True
        )
        if not response["ok"]:
            raise Exception(f"Bot message failed: {response.get('error', 'Unknown error')}")
    
    def alert(self, message: str, location_key: str, old_schema: Dict[str, Any], new_schema: Dict[str, Any]) -> None:
        print(f"Sending Slack alert for location: {location_key}")
        try:
            # Format message for Slack
            slack_message = "🚨 *DataFrame Schema Drift Detected*\n\n"
            slack_message += f"*Location:* `{location_key}`\n"
            slack_message += f"*Details:* {message}\n\n"
            
            # Add schema comparison details
            old_columns = set(old_schema.get("columns", {}).keys())
            new_columns = set(new_schema.get("columns", {}).keys())
            
            if old_columns != new_columns:
                added = new_columns - old_columns
                removed = old_columns - new_columns
                if added:
                    slack_message += f"*Added columns:* {', '.join(f'`{col}`' for col in added)}\n"
                if removed:
                    slack_message += f"*Removed columns:* {', '.join(f'`{col}`' for col in removed)}\n"
            
            # Send via webhook or bot token
            print(f"Using {'webhook' if self.webhook_url else 'bot token'} for Slack notification")
            if self.webhook_url:
                self._send_webhook_message(slack_message)
            else:
                self._send_bot_message(slack_message)
                
        except Exception as e:
            print(f"Error sending Slack notification: {e}", file=sys.stderr)
            # Fallback to stderr
            print(f"WARNING: {message}", file=sys.stderr)
            print(f"Location: {location_key}", file=sys.stderr)