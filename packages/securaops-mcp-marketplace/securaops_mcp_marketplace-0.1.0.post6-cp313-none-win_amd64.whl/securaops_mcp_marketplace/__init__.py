# Copyright 2025 SecuraOps Inc. All rights reserved.
#
# Licensed under the BSD License (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://github.com/securacoder/mcp-marketplace/blob/main/LICENSE
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
A marketplace for MCP (Model Context Protocol) connectors
"""
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

__all__ = [
    "SlackConnector", "DiscordConnector", "NotionConnector", 
    "GoogleDriveConnector", "TrelloConnector", "GitHubConnector",
    "JiraConnector", "LinearConnector", "PostgresSqlConnector",
    "MongoDBAtlasConnector"
    ]