from .slack_connector import SlackConnector
from .discord_connector import DiscordConnector
from .notion_connector import NotionConnector
from .google_drive_connector import GoogleDriveConnector
from .trello_connector import TrelloConnector
from .github_connector import GitHubConnector
from .jira_connector import JiraConnector
from .linear_connector import LinearConnector
from .postgresql_connector import PostgresSqlConnector
from .mongodb_connector import MongoDBAtlasConnector

activate = False

if activate:
    from .license_manager import LicenseManager
    __all__ = ["SlackConnector", "DiscordConnector", "LicenseManager"]

    # Global license manager instance
    _license_manager = LicenseManager()

    def activate_license(api_key: str, license_key: str) -> bool:
        """Activate the SDK with API key and license key"""
        return _license_manager.activate(api_key, license_key)

    def check_license() -> bool:
        """Check if license is valid"""
        return _license_manager.is_valid()

__all__ = [
    "SlackConnector", "DiscordConnector", "NotionConnector", 
    "GoogleDriveConnector", "TrelloConnector", "GitHubConnector",
    "JiraConnector", "LinearConnector", "PostgresSqlConnector",
    "MongoDBAtlasConnector"
    ]