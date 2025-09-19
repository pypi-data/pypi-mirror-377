#!/usr/bin/env python3
"""
Constitute MCP Server - Constitutional Document Analysis and Scraping Tools
"""

import asyncio
import json
import logging
from typing import Optional, List, Dict, Any

from mcp.server import Server
from mcp.server.stdio import stdio_server

# ---- Version-compat shims ---------------------------------------------------
# Some mcp versions expose dataclass models in mcp.server.models (snake_case),
# others rely on plain dict / TypedDict in mcp.types (camelCase on the wire).
HAS_MODELS_TOOL = False
HAS_MODELS_RESULTS = False

try:
    from mcp.server.models import (  # type: ignore
        InitializationOptions,
        ServerCapabilities,
        Tool as ModelsTool,                # may not exist in older versions
        ListToolsResult as ModelsListToolsResult,
        ListResourcesResult as ModelsListResourcesResult,
        ListPromptsResult as ModelsListPromptsResult,
    )
    HAS_MODELS_RESULTS = True
    # Probe Tool existence
    HAS_MODELS_TOOL = True if ModelsTool else False  # noqa: F401
except Exception:
    # Older mcp: still try to import the non-Tool classes
    from mcp.server.models import (  # type: ignore
        InitializationOptions,
        ServerCapabilities,
    )
    ModelsTool = None
    ModelsListToolsResult = None
    ModelsListResourcesResult = None
    ModelsListPromptsResult = None

# Wire types (always available)
from mcp.types import (
    CallToolRequest,
    CallToolResult,
    TextContent,
)

# If models Tool is missing, we’ll fall back to TypedDict Tool shape (dicts)
try:
    from mcp.types import Tool as TypesTool  # TypedDict in some versions
except Exception:
    TypesTool = dict  # last resort typing

# -----------------------------------------------------------------------------

from .scraper import ConstituteScraper


def build_tool_desc(name: str, description: str, schema_props: Dict[str, Any],
                    required: Optional[List[str]] = None,
                    additional_properties: bool = False) -> Any:
    """
    Build a Tool description compatible across MCP versions.

    If ModelsTool exists: return ModelsTool(name=..., description=..., input_schema=...)
    Else: return a dict containing BOTH 'inputSchema' (camelCase) and 'input_schema' (snake_case).
    """
    json_schema_obj = {
        "type": "object",
        "properties": schema_props,
    }
    if required:
        json_schema_obj["required"] = required
    if additional_properties is not None:
        json_schema_obj["additionalProperties"] = additional_properties

    if HAS_MODELS_TOOL and ModelsTool is not None:
        # Newer server models expect snake_case
        return ModelsTool(
            name=name,
            description=description,
            input_schema=json_schema_obj,
        )
    else:
        # Dict/TypedDict; put both keys to maximize compatibility
        return {
            "name": name,
            "description": description,
            "inputSchema": json_schema_obj,
            "input_schema": json_schema_obj,
        }


def wrap_list_tools(tools_list: List[Any]) -> Any:
    """
    Wrap tools list in a ListToolsResult if available, else return plain dict.
    """
    if HAS_MODELS_RESULTS and ModelsListToolsResult is not None:
        return ModelsListToolsResult(tools=tools_list)  # type: ignore
    return {"tools": tools_list}


def wrap_list_resources(resources_list: List[Any]) -> Any:
    if HAS_MODELS_RESULTS and ModelsListResourcesResult is not None:
        return ModelsListResourcesResult(resources=resources_list)  # type: ignore
    return {"resources": resources_list}


def wrap_list_prompts(prompts_list: List[Any]) -> Any:
    if HAS_MODELS_RESULTS and ModelsListPromptsResult is not None:
        return ModelsListPromptsResult(prompts=prompts_list)  # type: ignore
    return {"prompts": prompts_list}


class ConstituteServer:
    """MCP Server for Constitute Project tools."""

    def __init__(self):
        self.server = Server("constitute-mcp")
        self.scraper = ConstituteScraper(delay=1)
        self.logger = logging.getLogger(__name__)

        # tools/list
        @self.server.list_tools()
        async def handle_list_tools():
            try:
                result = await self.list_tools()
                # For models result, log .tools; for dict, log len of list
                if isinstance(result, dict):
                    self.logger.info(f"Returning {len(result.get('tools', []))} tools")
                else:
                    self.logger.info(f"Returning {len(result.tools)} tools")  # type: ignore
                return result
            except Exception:
                self.logger.exception("Error in list_tools")
                return wrap_list_tools([])

        # call_tool
        @self.server.call_tool()
        async def handle_call_tool(request: CallToolRequest) -> CallToolResult:
            return await self.call_tool(request)

        # prompts/list
        @self.server.list_prompts()
        async def handle_list_prompts():
            return wrap_list_prompts([])

        # resources/list
        @self.server.list_resources()
        async def handle_list_resources():
            return wrap_list_resources([])

    async def list_tools(self):
        """List available constitutional analysis tools."""
        tools = [
            build_tool_desc(
                name="get_constitutions_list",
                description="Get a list of all available constitutions",
                schema_props={
                    "show_details": {
                        "type": "boolean",
                        "description": "Whether to include detailed information",
                    },
                    "region_filter": {
                        "type": "string",
                        "description": "Filter by region (optional)",
                    },
                },
                additional_properties=False,
            ),
            build_tool_desc(
                name="find_constitution_by_country",
                description="Find constitutions by country name",
                schema_props={
                    "country_name": {
                        "type": "string",
                        "description": "Name of the country to search for",
                    },
                    "exact_match": {
                        "type": "boolean",
                        "description": "Whether to use exact matching",
                    },
                },
                required=["country_name"],
                additional_properties=False,
            ),
            build_tool_desc(
                name="scrape_constitution",
                description="Scrape the full content of a specific constitution",
                schema_props={
                    "constitution_id": {
                        "type": "string",
                        "description": "ID of the constitution to scrape",
                    },
                },
                required=["constitution_id"],
                additional_properties=False,
            ),
            build_tool_desc(
                name="get_article_by_number",
                description="Get a specific article from a constitution by its number",
                schema_props={
                    "constitution_id": {"type": "string", "description": "ID of the constitution"},
                    "article_number": {"type": "string", "description": "Article number to retrieve"},
                },
                required=["constitution_id", "article_number"],
                additional_properties=False,
            ),
            build_tool_desc(
                name="get_articles_range",
                description="Get a range of articles from a constitution",
                schema_props={
                    "constitution_id": {"type": "string", "description": "ID of the constitution"},
                    "start_article": {"type": "string", "description": "Starting article number"},
                    "end_article": {"type": "string", "description": "Ending article number"},
                },
                required=["constitution_id", "start_article", "end_article"],
                additional_properties=False,
            ),
            build_tool_desc(
                name="search_articles_by_keyword",
                description="Search for articles containing specific keywords",
                schema_props={
                    "constitution_id": {"type": "string", "description": "ID of the constitution"},
                    "keyword": {"type": "string", "description": "Keyword to search for"},
                },
                required=["constitution_id", "keyword"],
                additional_properties=False,
            ),
            build_tool_desc(
                name="topic_constitutions",
                description="Find constitutions by topic key",
                schema_props={
                    "topic_key": {
                        "type": "string",
                        "description": "Topic key (e.g., 'econplan', 'env', 'leg')",
                    },
                    "in_force": {"type": "boolean", "description": "Only currently in force", "default": True},
                    "is_draft": {"type": "boolean", "description": "Include drafts", "default": False},
                    "ownership": {
                        "type": "string",
                        "description": "Ownership filter",
                        "enum": ["all", "public", "mine"],
                        "default": "all",
                    },
                },
                required=["topic_key"],
                additional_properties=False,
            ),
            build_tool_desc(
                name="topic_sections",
                description="Get specific sections from a constitution related to a topic",
                schema_props={
                    "topic_key": {"type": "string", "description": "Topic key"},
                    "constitution_id": {"type": "string", "description": "ID of the constitution"},
                    "in_force": {"type": "boolean", "description": "Only currently in force", "default": True},
                    "is_draft": {"type": "boolean", "description": "Include drafts", "default": False},
                    "ownership": {
                        "type": "string",
                        "description": "Ownership filter",
                        "enum": ["all", "public", "mine"],
                        "default": "all",
                    },
                },
                required=["topic_key", "constitution_id"],
                additional_properties=False,
            ),
            build_tool_desc(
                name="export_constitution_json",
                description="Export constitution data as JSON",
                schema_props={
                    "constitution_id": {"type": "string", "description": "ID of the constitution"},
                    "filename": {"type": "string", "description": "Output filename (optional)"},
                },
                required=["constitution_id"],
                additional_properties=False,
            ),
            build_tool_desc(
                name="export_constitution_text",
                description="Export constitution as plain text",
                schema_props={
                    "constitution_id": {"type": "string", "description": "ID of the constitution"},
                    "filename": {"type": "string", "description": "Output filename (optional)"},
                },
                required=["constitution_id"],
                additional_properties=False,
            ),
            build_tool_desc(
                name="scrape_all_constitutions",
                description="Scrape all available constitutions (batch operation)",
                schema_props={
                    "limit": {"type": "integer", "description": "Limit number scraped (optional)"},
                    "save_individual": {"type": "boolean", "description": "Save individual files", "default": True},
                },
                additional_properties=False,
            ),
        ]

        return wrap_list_tools(tools)

    async def call_tool(self, request: CallToolRequest) -> CallToolResult:
        """Dispatch tool calls."""
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
            self.logger.exception(f"Error in tool {getattr(request.params, 'name', 'unknown')}")
            return CallToolResult(
                content=[TextContent(type="text", text=f"Error: {str(e)}")],
                isError=True,
            )

    # ----- Tool implementations -----

    async def _get_constitutions_list(
        self, show_details: bool = False, region_filter: Optional[str] = None
    ) -> CallToolResult:
        try:
            constitutions = self.scraper.get_constitutions_list()
            if region_filter:
                constitutions = [
                    c for c in constitutions
                    if c.get("region", "").lower() == region_filter.lower()
                ]

            result = {
                "total_count": len(constitutions),
            }
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
                "note": "Full content cached in server. Use specific article/section tools to access content.",
            }
            return CallToolResult(content=[TextContent(type="text", text=json.dumps(payload, ensure_ascii=False, indent=2))])
        except Exception as e:
            raise RuntimeError(f"Failed to scrape constitution: {e}")

    async def _get_article_by_number(self, constitution_id: str, article_number: str) -> CallToolResult:
        try:
            content = self.scraper.scrape_constitution_content(constitution_id)
            if content is None:
                raise RuntimeError(f"Failed to get constitution content: {constitution_id}")

            article = self.scraper.get_article_by_number(content, article_number)
            if article is None:
                return CallToolResult(content=[TextContent(type="text", text=f"Article {article_number} not found in constitution {constitution_id}")])

            return CallToolResult(content=[TextContent(type="text", text=json.dumps(article, ensure_ascii=False, indent=2))])
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
            return CallToolResult(content=[TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))])
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
            return CallToolResult(content=[TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))])
        except Exception as e:
            raise RuntimeError(f"Failed to search articles: {e}")

    async def _topic_constitutions(self, topic_key: str, in_force: bool = True, is_draft: bool = False, ownership: str = "all") -> CallToolResult:
        try:
            constitutions = self.scraper.topic_constitutions(topic_key, in_force=in_force, is_draft=is_draft, ownership=ownership)
            result = {
                "topic_key": topic_key,
                "parameters": {"in_force": in_force, "is_draft": is_draft, "ownership": ownership},
                "found_count": len(constitutions),
                "constitutions": constitutions,
            }
            return CallToolResult(content=[TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))])
        except Exception as e:
            raise RuntimeError(f"Failed to search constitutions by topic: {e}")

    async def _topic_sections(self, topic_key: str, constitution_id: str, in_force: bool = True, is_draft: bool = False, ownership: str = "all") -> CallToolResult:
        try:
            sections = self.scraper.topic_sections(topic_key, constitution_id, in_force=in_force, is_draft=is_draft, ownership=ownership)
            result = {
                "topic_key": topic_key,
                "constitution_id": constitution_id,
                "parameters": {"in_force": in_force, "is_draft": is_draft, "ownership": ownership},
                "found_count": len(sections),
                "sections": sections,
            }
            return CallToolResult(content=[TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))])
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

            return CallToolResult(content=[TextContent(type="text", text=f"Constitution {constitution_id} exported to {filename}")])
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

            return CallToolResult(content=[TextContent(type="text", text=f"Constitution {constitution_id} exported as text to {filename}")])
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
            return CallToolResult(content=[TextContent(type="text", text=json.dumps(summary, ensure_ascii=False, indent=2))])
        except Exception as e:
            raise RuntimeError(f"Failed to scrape all constitutions: {e}")


async def main():
    """Main entry point for the MCP server."""
    logging.basicConfig(level=logging.INFO)
    server_instance = ConstituteServer()

    async with stdio_server() as (read_stream, write_stream):
        await server_instance.server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="constitute-mcp",
                server_version="0.1.16",
                capabilities=ServerCapabilities(
                    tools={"listChanged": True},
                    prompts={"listChanged": False},
                    resources={"listChanged": False},
                ),
            ),
        )


def cli():
    """CLI entry point for the package."""
    asyncio.run(main())


if __name__ == "__main__":
    cli()
