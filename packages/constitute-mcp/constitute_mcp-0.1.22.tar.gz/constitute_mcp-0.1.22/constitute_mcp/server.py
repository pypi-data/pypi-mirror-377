#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Constitute MCP Server - Constitutional Document Analysis and Scraping Tools

Exposes tools for:
- Listing/searching constitutions
- Scraping constitution content
- Fetching articles/sections
- Topic-based queries
- Export/export text

Requires: mcp>=1.2,<2.0
"""

import asyncio
import json
import logging
from typing import Optional, List, Dict, Any

from mcp.server import Server
from mcp.server.models import (
    InitializationOptions,
    ServerCapabilities,
)
from mcp.server.stdio import stdio_server
from mcp.types import (
    Tool,
    ListToolsResult,
    ListResourcesResult,
    ListPromptsResult,
)

# 線路層的呼叫/回應型別仍從 mcp.types 取得
from mcp.types import (
    CallToolRequest,
    CallToolResult,
    TextContent,
)

from .scraper import ConstituteScraper


class ConstituteServer:
    """MCP Server for Constitute Project tools."""

    def __init__(self) -> None:
        self.server = Server("constitute-mcp")
        self.scraper = ConstituteScraper(delay=1)
        self.logger = logging.getLogger("constitute_mcp.server")

        # ---- MCP handlers ----

        @self.server.list_tools()
        async def handle_list_tools() -> ListToolsResult:
            try:
                result = await self.list_tools()
                self.logger.info("Returning %d tools", len(result.tools))
                return result
            except Exception:
                self.logger.exception("Error in list_tools")
                return ListToolsResult(tools=[])

        @self.server.call_tool()
        async def handle_call_tool(request: CallToolRequest) -> CallToolResult:
            return await self.call_tool(request)

        @self.server.list_prompts()
        async def handle_list_prompts() -> ListPromptsResult:
            # 目前沒有 prompts；回空陣列即可（需用模型型別）
            return ListPromptsResult(prompts=[])

        @self.server.list_resources()
        async def handle_list_resources() -> ListResourcesResult:
            # 若未提供靜態資源，回空陣列（需用模型型別）
            return ListResourcesResult(resources=[])

    # ---------------- Tools registry ----------------

    async def list_tools(self) -> ListToolsResult:
        """Assemble and return the tool catalog."""
        tools: List[Tool] = [
            Tool(
                name="get_constitutions_list",
                description="Get a list of all available constitutions",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "show_details": {
                            "type": "boolean",
                            "description": "Whether to include detailed information",
                        },
                        "region_filter": {
                            "type": "string",
                            "description": "Filter by region (optional)",
                        },
                    },
                    "additionalProperties": False,
                },
            ),
            Tool(
                name="find_constitution_by_country",
                description="Find constitutions by country name",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "country_name": {
                            "type": "string",
                            "description": "Name of the country to search for",
                        },
                        "exact_match": {
                            "type": "boolean",
                            "description": "Whether to use exact matching",
                        },
                    },
                    "required": ["country_name"],
                    "additionalProperties": False,
                },
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
                    "additionalProperties": False,
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
                    "additionalProperties": False,
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
                    "additionalProperties": False,
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
                    "additionalProperties": False,
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
                    "additionalProperties": False,
                },
            ),
            Tool(
                name="topic_sections",
                description="Get specific sections from a constitution related to a topic",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "topic_key": {"type": "string", "description": "Topic key to search for"},
                        "constitution_id": {"type": "string", "description": "ID of the constitution"},
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
                    "additionalProperties": False,
                },
            ),
            Tool(
                name="export_constitution_json",
                description="Export constitution data as JSON",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "constitution_id": {"type": "string", "description": "ID of the constitution"},
                        "filename": {"type": "string", "description": "Output filename (optional)"},
                    },
                    "required": ["constitution_id"],
                    "additionalProperties": False,
                },
            ),
            Tool(
                name="export_constitution_text",
                description="Export constitution as plain text",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "constitution_id": {"type": "string", "description": "ID of the constitution"},
                        "filename": {"type": "string", "description": "Output filename (optional)"},
                    },
                    "required": ["constitution_id"],
                    "additionalProperties": False,
                },
            ),
            Tool(
                name="scrape_all_constitutions",
                description="Scrape all available constitutions (batch operation)",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "limit": {"type": "integer", "description": "Limit the number of constitutions"},
                        "save_individual": {"type": "boolean", "description": "Save individual files", "default": True},
                    },
                    "additionalProperties": False,
                },
            ),
        ]

        return ListToolsResult(tools=tools)

    # ---------------- Dispatcher ----------------

    async def call_tool(self, request: CallToolRequest) -> CallToolResult:
        """Handle tool calls dispatched by name."""
        try:
            name = request.params.name
            args: Dict[str, Any] = request.params.arguments or {}

            if name == "get_constitutions_list":
                return await self._get_constitutions_list(**args)
            if name == "find_constitution_by_country":
                return await self._find_constitution_by_country(**args)
            if name == "scrape_constitution":
                return await self._scrape_constitution(**args)
            if name == "get_article_by_number":
                return await self._get_article_by_number(**args)
            if name == "get_articles_range":
                return await self._get_articles_range(**args)
            if name == "search_articles_by_keyword":
                return await self._search_articles_by_keyword(**args)
            if name == "topic_constitutions":
                return await self._topic_constitutions(**args)
            if name == "topic_sections":
                return await self._topic_sections(**args)
            if name == "export_constitution_json":
                return await self._export_constitution_json(**args)
            if name == "export_constitution_text":
                return await self._export_constitution_text(**args)
            if name == "scrape_all_constitutions":
                return await self._scrape_all_constitutions(**args)

            raise ValueError(f"Unknown tool: {name}")

        except Exception as e:
            self.logger.exception("Error in tool %s", getattr(request.params, "name", "unknown"))
            return CallToolResult(
                content=[TextContent(type="text", text=f"Error: {str(e)}")],
                isError=True,
            )

    # ---------------- Tool implementations ----------------

    async def _get_constitutions_list(
        self, show_details: bool = False, region_filter: Optional[str] = None
    ) -> CallToolResult:
        try:
            constitutions = self.scraper.get_constitutions_list()
            if region_filter:
                rf = (region_filter or "").lower()
                constitutions = [c for c in constitutions if c.get("region", "").lower() == rf]

            result: Dict[str, Any] = {"total_count": len(constitutions)}
            if show_details:
                result["constitutions"] = constitutions
            else:
                result["countries"] = [c.get("country", "Unknown") for c in constitutions]

            return CallToolResult(
                content=[TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]
            )
        except Exception as e:
            raise RuntimeError(f"Failed to get constitutions list: {e}")

    async def _find_constitution_by_country(
        self, country_name: str, exact_match: bool = False
    ) -> CallToolResult:
        try:
            matches = self.scraper.find_constitution_by_country(country_name, exact_match)
            result = {
                "query": country_name,
                "exact_match": exact_match,
                "found_count": len(matches),
                "matches": matches,
            }
            return CallToolResult(
                content=[TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]
            )
        except Exception as e:
            raise RuntimeError(f"Failed to find constitution by country: {e}")

    async def _scrape_constitution(self, constitution_id: str) -> CallToolResult:
        try:
            content = self.scraper.scrape_constitution_content(constitution_id)
            if content is None:
                raise RuntimeError(f"Failed to scrape constitution: {constitution_id}")

            summary = {
                "id": content.get("id"),
                "title": content.get("title"),
                "preamble_length": len(content.get("preamble", "")),
                "chapters_count": len(content.get("chapters", [])),
                "articles_count": len(content.get("articles", [])),
                "full_text_length": len(content.get("full_text", "")),
            }
            payload = {
                "message": f"Successfully scraped constitution: {constitution_id}",
                "summary": summary,
                "note": "Full content cached on server. Use specific article/section tools to access content.",
            }
            return CallToolResult(
                content=[TextContent(type="text", text=json.dumps(payload, ensure_ascii=False, indent=2))]
            )
        except Exception as e:
            raise RuntimeError(f"Failed to scrape constitution: {e}")

    async def _get_article_by_number(self, constitution_id: str, article_number: str) -> CallToolResult:
        try:
            content = self.scraper.scrape_constitution_content(constitution_id)
            if content is None:
                raise RuntimeError(f"Failed to get constitution content: {constitution_id}")

            article = self.scraper.get_article_by_number(content, article_number)
            if article is None:
                return CallToolResult(
                    content=[TextContent(type="text", text=f"Article {article_number} not found in constitution {constitution_id}")]
                )

            return CallToolResult(
                content=[TextContent(type="text", text=json.dumps(article, ensure_ascii=False, indent=2))]
            )
        except Exception as e:
            raise RuntimeError(f"Failed to get article: {e}")

    async def _get_articles_range(self, constitution_id: str, start_article: str, end_article: str) -> CallToolResult:
        try:
            content = self.scraper.scrape_constitution_content(constitution_id)
            if content is None:
                raise RuntimeError(f"Failed to get constitution content: {constitution_id}")

            articles = self.scraper.get_articles_range(content, start_article, end_article)
            result = {
                "constitution_id": constitution_id,
                "range": f"{start_article}-{end_article}",
                "found_count": len(articles),
                "articles": articles,
            }
            return CallToolResult(
                content=[TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]
            )
        except Exception as e:
            raise RuntimeError(f"Failed to get articles range: {e}")

    async def _search_articles_by_keyword(self, constitution_id: str, keyword: str) -> CallToolResult:
        try:
            content = self.scraper.scrape_constitution_content(constitution_id)
            if content is None:
                raise RuntimeError(f"Failed to get constitution content: {constitution_id}")

            articles = self.scraper.search_articles_by_keyword(content, keyword)
            result = {
                "constitution_id": constitution_id,
                "keyword": keyword,
                "found_count": len(articles),
                "articles": articles,
            }
            return CallToolResult(
                content=[TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]
            )
        except Exception as e:
            raise RuntimeError(f"Failed to search articles: {e}")

    async def _topic_constitutions(
        self, topic_key: str, in_force: bool = True, is_draft: bool = False, ownership: str = "all"
    ) -> CallToolResult:
        try:
            constitutions = self.scraper.topic_constitutions(
                topic_key, in_force=in_force, is_draft=is_draft, ownership=ownership
            )
            result = {
                "topic_key": topic_key,
                "parameters": {"in_force": in_force, "is_draft": is_draft, "ownership": ownership},
                "found_count": len(constitutions),
                "constitutions": constitutions,
            }
            return CallToolResult(
                content=[TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]
            )
        except Exception as e:
            raise RuntimeError(f"Failed to search constitutions by topic: {e}")

    async def _topic_sections(
        self, topic_key: str, constitution_id: str, in_force: bool = True, is_draft: bool = False, ownership: str = "all"
    ) -> CallToolResult:
        try:
            sections = self.scraper.topic_sections(
                topic_key, constitution_id, in_force=in_force, is_draft=is_draft, ownership=ownership
            )
            result = {
                "topic_key": topic_key,
                "constitution_id": constitution_id,
                "parameters": {"in_force": in_force, "is_draft": is_draft, "ownership": ownership},
                "found_count": len(sections),
                "sections": sections,
            }
            return CallToolResult(
                content=[TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]
            )
        except Exception as e:
            raise RuntimeError(f"Failed to get topic sections: {e}")

    async def _export_constitution_json(self, constitution_id: str, filename: Optional[str] = None) -> CallToolResult:
        try:
            content = self.scraper.scrape_constitution_content(constitution_id)
            if content is None:
                raise RuntimeError(f"Failed to get constitution content: {constitution_id}")

            if not filename:
                filename = f"{constitution_id}.json"
            filename = self.scraper.sanitize_filename(filename)
            self.scraper.save_to_json(content, filename)

            return CallToolResult(
                content=[TextContent(type="text", text=f"Constitution {constitution_id} exported to {filename}")]
            )
        except Exception as e:
            raise RuntimeError(f"Failed to export constitution: {e}")

    async def _export_constitution_text(self, constitution_id: str, filename: Optional[str] = None) -> CallToolResult:
        try:
            content = self.scraper.scrape_constitution_content(constitution_id)
            if content is None:
                raise RuntimeError(f"Failed to get constitution content: {constitution_id}")

            if not filename:
                filename = f"{constitution_id}.txt"
            filename = self.scraper.sanitize_filename(filename)

            with open(filename, "w", encoding="utf-8") as f:
                f.write(content.get("full_text", ""))

            return CallToolResult(
                content=[TextContent(type="text", text=f"Constitution {constitution_id} exported as text to {filename}")]
            )
        except Exception as e:
            raise RuntimeError(f"Failed to export constitution as text: {e}")

    async def _scrape_all_constitutions(self, limit: Optional[int] = None, save_individual: bool = True) -> CallToolResult:
        try:
            result = self.scraper.scrape_all_constitutions(limit=limit, save_individual=save_individual)
            summary = {
                "total_scraped": len(result),
                "limit_applied": limit,
                "individual_files_saved": save_individual,
                "message": f"Successfully scraped {len(result)} constitutions",
            }
            return CallToolResult(
                content=[TextContent(type="text", text=json.dumps(summary, ensure_ascii=False, indent=2))]
            )
        except Exception as e:
            raise RuntimeError(f"Failed to scrape all constitutions: {e}")


# ---------------- Entrypoints ----------------

async def main() -> None:
    """Main entry point for the MCP server (stdio transport)."""
    logging.basicConfig(level=logging.INFO)
    server_instance = ConstituteServer()
    async with stdio_server() as (read_stream, write_stream):
        await server_instance.server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="constitute-mcp",
                server_version="0.1.17",
                capabilities=ServerCapabilities(
                    tools={"listChanged": True},
                    prompts={"listChanged": False},
                    resources={"listChanged": False},
                ),
            ),
        )


def cli() -> None:
    """CLI entry point configured in pyproject [project.scripts]."""
    asyncio.run(main())


if __name__ == "__main__":
    cli()
