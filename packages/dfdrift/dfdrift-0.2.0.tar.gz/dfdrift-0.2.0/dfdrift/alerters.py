import os
import sys
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
    def __init__(self, channel: Optional[str] = None, token: Optional[str] = None):
        self.token = token or os.getenv("SLACK_BOT_TOKEN")
        self.channel = channel or os.getenv("SLACK_CHANNEL")
        
        if not self.token:
            raise ValueError("Slack token must be provided either as argument or SLACK_BOT_TOKEN environment variable")
        
        if not self.channel:
            raise ValueError("Slack channel must be provided either as argument or SLACK_CHANNEL environment variable")
        
        self.client = self._import_slack_sdk()
    
    def _import_slack_sdk(self):
        """Import slack SDK and create client"""
        try:
            from slack_sdk import WebClient
            return WebClient(token=self.token)
        except ImportError:
            raise ImportError("slack-sdk package is required for SlackAlerter. Install with: pip install slack-sdk")
    
    def alert(self, message: str, location_key: str, old_schema: Dict[str, Any], new_schema: Dict[str, Any]) -> None:
        try:
            # Format message for Slack
            slack_message = f"🚨 *DataFrame Schema Drift Detected*\n\n"
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
            
            # Send to Slack
            response = self.client.chat_postMessage(
                channel=self.channel,
                text=slack_message,
                mrkdwn=True
            )
            if not response["ok"]:
                print(f"Failed to send Slack message: {response.get('error', 'Unknown error')}", file=sys.stderr)
                # Fallback to stderr
                print(f"WARNING: {message}", file=sys.stderr)
                print(f"Location: {location_key}", file=sys.stderr)
                
        except Exception as e:
            print(f"Error sending Slack notification: {e}", file=sys.stderr)
            # Fallback to stderr
            print(f"WARNING: {message}", file=sys.stderr)
            print(f"Location: {location_key}", file=sys.stderr)