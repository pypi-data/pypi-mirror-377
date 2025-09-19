#!/usr/bin/env python3
"""
Constitute MCP Server - Constitutional Document Analysis and Scraping Tools

This MCP server provides tools for:
- Listing and searching constitutional documents
- Scraping constitutional content
- Analyzing articles and sections
- Topic-based constitutional research
- Exporting constitutional data
"""

import asyncio
import json
import logging
import os
import uuid
from typing import Any, Dict, List, Optional, Sequence

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.models import ServerCapabilities
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolRequest,
    CallToolResult,
    ListToolsRequest,
    ListToolsResult,
    Tool,
    TextContent,
)
from pydantic import BaseModel, Field

from .scraper import ConstituteScraper


class ConstituteServer:
    """MCP Server for Constitute Project tools."""

    def __init__(self):
        self.server = Server("constitute-mcp")
        self.scraper = ConstituteScraper(delay=1)
        self.logger = logging.getLogger(__name__)

        # Register handlers using proper MCP decorators
        @self.server.list_tools()
        async def handle_list_tools() -> ListToolsResult:
            try:
                result = await self.list_tools()
                self.logger.info(f"Returning {len(result.tools)} tools")
                return result
            except Exception as e:
                self.logger.exception("Error in list_tools")
                return ListToolsResult(tools=[])

        @self.server.call_tool()
        async def handle_call_tool(request: CallToolRequest) -> CallToolResult:
            return await self.call_tool(request)

        # Register resources/list method
        @self.server.method("resources/list")
        async def resources_list_handler(params: dict) -> List[dict]:
            """Handler for resources/list method."""
            try:
                # Assume resources are the available tools
                resources = [
                    {
                        "name": tool.name,
                        "description": tool.description,
                    }
                    for tool in (await self.list_tools()).tools
                ]
                return resources
            except Exception as e:
                self.logger.exception("Error in resources_list_handler")
                return []

    async def list_tools(self) -> ListToolsResult:
        """List available constitutional analysis tools."""
        # Create tools with clean schemas
        tools = [
            Tool(
                name="get_constitutions_list",
                description="Get a list of all available constitutions",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "show_details": {
                            "type": "boolean",
                            "description": "Whether to include detailed information"
                        },
                        "region_filter": {
                            "type": "string",
                            "description": "Filter by region (optional)"
                        }
                    },
                    "additionalProperties": False
                }
            ),
            Tool(
                name="find_constitution_by_country",
                description="Find constitutions by country name",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "country_name": {
                            "type": "string",
                            "description": "Name of the country to search for"
                        },
                        "exact_match": {
                            "type": "boolean",
                            "description": "Whether to use exact matching"
                        }
                    },
                    "required": ["country_name"],
                    "additionalProperties": False
                }
            ),
            Tool(
                name="scrape_constitution",
                description="Scrape the full content of a specific constitution",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "constitution_id": {
                            "type": "string",
                            "description": "ID of the constitution to scrape",
                        }
                    },
                    "required": ["constitution_id"],
                },
            ),
            Tool(
                name="get_article_by_number",
                description="Get a specific article from a constitution by its number",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "constitution_id": {
                            "type": "string",
                            "description": "ID of the constitution",
                        },
                        "article_number": {
                            "type": "string",
                            "description": "Article number to retrieve",
                        },
                    },
                    "required": ["constitution_id", "article_number"],
                },
            ),
            Tool(
                name="get_articles_range",
                description="Get a range of articles from a constitution",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "constitution_id": {
                            "type": "string",
                            "description": "ID of the constitution",
                        },
                        "start_article": {
                            "type": "string",
                            "description": "Starting article number",
                        },
                        "end_article": {
                            "type": "string",
                            "description": "Ending article number",
                        },
                    },
                    "required": ["constitution_id", "start_article", "end_article"],
                },
            ),
            Tool(
                name="search_articles_by_keyword",
                description="Search for articles containing specific keywords",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "constitution_id": {
                            "type": "string",
                            "description": "ID of the constitution",
                        },
                        "keyword": {
                            "type": "string",
                            "description": "Keyword to search for",
                        },
                    },
                    "required": ["constitution_id", "keyword"],
                },
            ),
            Tool(
                name="topic_constitutions",
                description="Find constitutions by topic key",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "topic_key": {
                            "type": "string",
                            "description": "Topic key to search for (e.g., 'econplan', 'env', 'leg')",
                        },
                        "in_force": {
                            "type": "boolean",
                            "description": "Only include constitutions currently in force",
                            "default": True,
                        },
                        "is_draft": {
                            "type": "boolean",
                            "description": "Include draft constitutions",
                            "default": False,
                        },
                        "ownership": {
                            "type": "string",
                            "description": "Ownership filter",
                            "enum": ["all", "public", "mine"],
                            "default": "all",
                        },
                    },
                    "required": ["topic_key"],
                },
            ),
            Tool(
                name="topic_sections",
                description="Get specific sections from a constitution related to a topic",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "topic_key": {
                            "type": "string",
                            "description": "Topic key to search for",
                        },
                        "constitution_id": {
                            "type": "string",
                            "description": "ID of the constitution",
                        },
                        "in_force": {
                            "type": "boolean",
                            "description": "Only include constitutions currently in force",
                            "default": True,
                        },
                        "is_draft": {
                            "type": "boolean",
                            "description": "Include draft constitutions",
                            "default": False,
                        },
                        "ownership": {
                            "type": "string",
                            "description": "Ownership filter",
                            "enum": ["all", "public", "mine"],
                            "default": "all",
                        },
                    },
                    "required": ["topic_key", "constitution_id"],
                },
            ),
            Tool(
                name="export_constitution_json",
                description="Export constitution data as JSON",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "constitution_id": {
                            "type": "string",
                            "description": "ID of the constitution to export",
                        },
                        "filename": {
                            "type": "string",
                            "description": "Output filename (optional)",
                        },
                    },
                    "required": ["constitution_id"],
                },
            ),
            Tool(
                name="export_constitution_text",
                description="Export constitution as plain text",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "constitution_id": {
                            "type": "string",
                            "description": "ID of the constitution to export",
                        },
                        "filename": {
                            "type": "string",
                            "description": "Output filename (optional)",
                        },
                    },
                    "required": ["constitution_id"],
                },
            ),
            Tool(
                name="scrape_all_constitutions",
                description="Scrape all available constitutions (batch operation)",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "limit": {
                            "type": "integer",
                            "description": "Limit the number of constitutions to scrape (optional)",
                        },
                        "save_individual": {
                            "type": "boolean",
                            "description": "Save individual constitution files",
                            "default": True,
                        },
                    },
                },
            ),
        ]

        # Return all tools - MCP compatibility issue should now be fixed
        return ListToolsResult(tools=tools)

    async def call_tool(self, request: CallToolRequest) -> CallToolResult:
        """Handle tool calls."""
        try:
            name = request.params.name
            args = request.params.arguments or {}

            if name == "get_constitutions_list":
                return await self._get_constitutions_list(**args)
            elif name == "find_constitution_by_country":
                return await self._find_constitution_by_country(**args)
            elif name == "scrape_constitution":
                return await self._scrape_constitution(**args)
            elif name == "get_article_by_number":
                return await self._get_article_by_number(**args)
            elif name == "get_articles_range":
                return await self._get_articles_range(**args)
            elif name == "search_articles_by_keyword":
                return await self._search_articles_by_keyword(**args)
            elif name == "topic_constitutions":
                return await self._topic_constitutions(**args)
            elif name == "topic_sections":
                return await self._topic_sections(**args)
            elif name == "export_constitution_json":
                return await self._export_constitution_json(**args)
            elif name == "export_constitution_text":
                return await self._export_constitution_text(**args)
            elif name == "scrape_all_constitutions":
                return await self._scrape_all_constitutions(**args)
            else:
                raise ValueError(f"Unknown tool: {name}")

        except Exception as e:
            self.logger.exception(f"Error in tool {request.params.name}")
            return CallToolResult(
                content=[TextContent(type="text", text=f"Error: {str(e)}")],
                isError=True,
            )

    async def _get_constitutions_list(
        self, show_details: bool = False, region_filter: Optional[str] = None
    ) -> CallToolResult:
        """Get list of available constitutions."""
        try:
            constitutions = self.scraper.get_constitutions_list()

            if region_filter:
                constitutions = [
                    c
                    for c in constitutions
                    if c.get("region", "").lower() == region_filter.lower()
                ]

            if show_details:
                result = {
                    "total_count": len(constitutions),
                    "constitutions": constitutions,
                }
            else:
                result = {
                    "total_count": len(constitutions),
                    "countries": [c.get("country", "Unknown") for c in constitutions],
                }

            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=json.dumps(result, ensure_ascii=False, indent=2),
                    )
                ]
            )
        except Exception as e:
            raise RuntimeError(f"Failed to get constitutions list: {e}")

    async def _find_constitution_by_country(
        self, country_name: str, exact_match: bool = False
    ) -> CallToolResult:
        """Find constitutions by country name."""
        try:
            matches = self.scraper.find_constitution_by_country(
                country_name, exact_match
            )

            result = {
                "query": country_name,
                "exact_match": exact_match,
                "found_count": len(matches),
                "matches": matches,
            }

            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=json.dumps(result, ensure_ascii=False, indent=2),
                    )
                ]
            )
        except Exception as e:
            raise RuntimeError(f"Failed to find constitution by country: {e}")

    async def _scrape_constitution(self, constitution_id: str) -> CallToolResult:
        """Scrape a specific constitution."""
        try:
            content = self.scraper.scrape_constitution_content(constitution_id)

            if content is None:
                raise RuntimeError(f"Failed to scrape constitution: {constitution_id}")

            # Return a summary instead of full content to avoid overwhelming output
            summary = {
                "id": content.get("id"),
                "title": content.get("title"),
                "preamble_length": len(content.get("preamble", "")),
                "chapters_count": len(content.get("chapters", [])),
                "articles_count": len(content.get("articles", [])),
                "full_text_length": len(content.get("full_text", "")),
            }

            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=json.dumps(
                            {
                                "message": f"Successfully scraped constitution: {constitution_id}",
                                "summary": summary,
                                "note": "Full content cached in server. Use specific article/section tools to access content.",
                            },
                            ensure_ascii=False,
                            indent=2,
                        ),
                    )
                ]
            )
        except Exception as e:
            raise RuntimeError(f"Failed to scrape constitution: {e}")

    async def _get_article_by_number(
        self, constitution_id: str, article_number: str
    ) -> CallToolResult:
        """Get a specific article by number."""
        try:
            # First scrape if needed
            content = self.scraper.scrape_constitution_content(constitution_id)
            if content is None:
                raise RuntimeError(
                    f"Failed to get constitution content: {constitution_id}"
                )

            article = self.scraper.get_article_by_number(content, article_number)

            if article is None:
                return CallToolResult(
                    content=[
                        TextContent(
                            type="text",
                            text=f"Article {article_number} not found in constitution {constitution_id}",
                        )
                    ]
                )

            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=json.dumps(article, ensure_ascii=False, indent=2),
                    )
                ]
            )
        except Exception as e:
            raise RuntimeError(f"Failed to get article: {e}")

    async def _get_articles_range(
        self, constitution_id: str, start_article: str, end_article: str
    ) -> CallToolResult:
        """Get a range of articles."""
        try:
            content = self.scraper.scrape_constitution_content(constitution_id)
            if content is None:
                raise RuntimeError(
                    f"Failed to get constitution content: {constitution_id}"
                )

            articles = self.scraper.get_articles_range(
                content, start_article, end_article
            )

            result = {
                "constitution_id": constitution_id,
                "range": f"{start_article}-{end_article}",
                "found_count": len(articles),
                "articles": articles,
            }

            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=json.dumps(result, ensure_ascii=False, indent=2),
                    )
                ]
            )
        except Exception as e:
            raise RuntimeError(f"Failed to get articles range: {e}")

    async def _search_articles_by_keyword(
        self, constitution_id: str, keyword: str
    ) -> CallToolResult:
        """Search for articles by keyword."""
        try:
            content = self.scraper.scrape_constitution_content(constitution_id)
            if content is None:
                raise RuntimeError(
                    f"Failed to get constitution content: {constitution_id}"
                )

            articles = self.scraper.search_articles_by_keyword(content, keyword)

            result = {
                "constitution_id": constitution_id,
                "keyword": keyword,
                "found_count": len(articles),
                "articles": articles,
            }

            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=json.dumps(result, ensure_ascii=False, indent=2),
                    )
                ]
            )
        except Exception as e:
            raise RuntimeError(f"Failed to search articles: {e}")

    async def _topic_constitutions(
        self,
        topic_key: str,
        in_force: bool = True,
        is_draft: bool = False,
        ownership: str = "all",
    ) -> CallToolResult:
        """Find constitutions by topic."""
        try:
            constitutions = self.scraper.topic_constitutions(
                topic_key, in_force=in_force, is_draft=is_draft, ownership=ownership
            )

            result = {
                "topic_key": topic_key,
                "parameters": {
                    "in_force": in_force,
                    "is_draft": is_draft,
                    "ownership": ownership,
                },
                "found_count": len(constitutions),
                "constitutions": constitutions,
            }

            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=json.dumps(result, ensure_ascii=False, indent=2),
                    )
                ]
            )
        except Exception as e:
            raise RuntimeError(f"Failed to search constitutions by topic: {e}")

    async def _topic_sections(
        self,
        topic_key: str,
        constitution_id: str,
        in_force: bool = True,
        is_draft: bool = False,
        ownership: str = "all",
    ) -> CallToolResult:
        """Get topic-related sections from a constitution."""
        try:
            sections = self.scraper.topic_sections(
                topic_key,
                constitution_id,
                in_force=in_force,
                is_draft=is_draft,
                ownership=ownership,
            )

            result = {
                "topic_key": topic_key,
                "constitution_id": constitution_id,
                "parameters": {
                    "in_force": in_force,
                    "is_draft": is_draft,
                    "ownership": ownership,
                },
                "found_count": len(sections),
                "sections": sections,
            }

            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=json.dumps(result, ensure_ascii=False, indent=2),
                    )
                ]
            )
        except Exception as e:
            raise RuntimeError(f"Failed to get topic sections: {e}")

    async def _export_constitution_json(
        self, constitution_id: str, filename: Optional[str] = None
    ) -> CallToolResult:
        """Export constitution as JSON."""
        try:
            content = self.scraper.scrape_constitution_content(constitution_id)
            if content is None:
                raise RuntimeError(
                    f"Failed to get constitution content: {constitution_id}"
                )

            if filename is None:
                filename = f"{constitution_id}.json"

            filename = self.scraper.sanitize_filename(filename)
            self.scraper.save_to_json(content, filename)

            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=f"Constitution {constitution_id} exported to {filename}",
                    )
                ]
            )
        except Exception as e:
            raise RuntimeError(f"Failed to export constitution: {e}")

    async def _export_constitution_text(
        self, constitution_id: str, filename: Optional[str] = None
    ) -> CallToolResult:
        """Export constitution as plain text."""
        try:
            content = self.scraper.scrape_constitution_content(constitution_id)
            if content is None:
                raise RuntimeError(
                    f"Failed to get constitution content: {constitution_id}"
                )

            if filename is None:
                filename = f"{constitution_id}.txt"

            filename = self.scraper.sanitize_filename(filename)

            with open(filename, "w", encoding="utf-8") as f:
                f.write(content.get("full_text", ""))

            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=f"Constitution {constitution_id} exported as text to {filename}",
                    )
                ]
            )
        except Exception as e:
            raise RuntimeError(f"Failed to export constitution as text: {e}")

    async def _scrape_all_constitutions(
        self, limit: Optional[int] = None, save_individual: bool = True
    ) -> CallToolResult:
        """Scrape all constitutions (batch operation)."""
        try:
            result = self.scraper.scrape_all_constitutions(
                limit=limit, save_individual=save_individual
            )

            summary = {
                "total_scraped": len(result),
                "limit_applied": limit,
                "individual_files_saved": save_individual,
                "message": f"Successfully scraped {len(result)} constitutions",
            }

            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=json.dumps(summary, ensure_ascii=False, indent=2),
                    )
                ]
            )
        except Exception as e:
            raise RuntimeError(f"Failed to scrape all constitutions: {e}")


async def main():
    """Main entry point for the MCP server."""
    server_instance = ConstituteServer()

    async with stdio_server() as (read_stream, write_stream):
        await server_instance.server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="constitute-mcp",
                server_version="0.1.12",
                capabilities=ServerCapabilities(
                    tools={"listChanged": True}
                ),
            ),
        )


def cli():
    """CLI entry point for the package."""
    asyncio.run(main())


if __name__ == "__main__":
    cli()
