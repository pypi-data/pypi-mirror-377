# --- imports：換掉 Tool 來源，新增 prompts/resources 結果型別 ---
from mcp.server import Server
from mcp.server.models import (
    InitializationOptions,
    ServerCapabilities,
    Tool,                    # ← 用這個 Tool
    ListToolsResult,
    ListResourcesResult,     # 新增
    ListPromptsResult,       # 新增
)
from mcp.server.stdio import stdio_server

# 保留這些（用於 call_tool 的 I/O 結構）
from mcp.types import (
    CallToolRequest,
    CallToolResult,
    TextContent,
)

# ...略...

class ConstituteServer:
    def __init__(self):
        self.server = Server("constitute-mcp")
        self.scraper = ConstituteScraper(delay=1)
        self.logger = logging.getLogger(__name__)

        # tools/list
        @self.server.list_tools()
        async def handle_list_tools() -> ListToolsResult:
            try:
                return await self.list_tools()
            except Exception:
                self.logger.exception("Error in list_tools")
                return ListToolsResult(tools=[])

        # call_tool
        @self.server.call_tool()
        async def handle_call_tool(request: CallToolRequest) -> CallToolResult:
            return await self.call_tool(request)

        # prompts/list（回空即可，避免 Method not found）
        @self.server.list_prompts()
        async def handle_list_prompts() -> ListPromptsResult:
            return ListPromptsResult(prompts=[])

        # resources/list（用官方 decorator）
        @self.server.list_resources()
        async def handle_list_resources() -> ListResourcesResult:
            # 若你目前沒有要提供靜態資源，回空即可
            return ListResourcesResult(resources=[])

    async def list_tools(self) -> ListToolsResult:
        # 用 mcp.server.models.Tool（或回傳純 dict），欄位名是 input_schema（蛇形命名）
        tools = [
            Tool(
                name="get_constitutions_list",
                description="Get a list of all available constitutions",
                input_schema={
                    "type": "object",
                    "properties": {
                        "show_details": {"type": "boolean"},
                        "region_filter": {"type": "string"}
                    },
                    "additionalProperties": False
                },
            ),
            Tool(
                name="find_constitution_by_country",
                description="Find constitutions by country name",
                input_schema={
                    "type": "object",
                    "properties": {
                        "country_name": {"type": "string"},
                        "exact_match": {"type": "boolean"}
                    },
                    "required": ["country_name"],
                    "additionalProperties": False
                },
            ),
            Tool(
                name="scrape_constitution",
                description="Scrape the full content of a specific constitution",
                input_schema={
                    "type": "object",
                    "properties": {
                        "constitution_id": {"type": "string"}
                    },
                    "required": ["constitution_id"]
                },
            ),
            Tool(
                name="get_article_by_number",
                description="Get a specific article from a constitution by its number",
                input_schema={
                    "type": "object",
                    "properties": {
                        "constitution_id": {"type": "string"},
                        "article_number": {"type": "string"}
                    },
                    "required": ["constitution_id", "article_number"]
                },
            ),
            Tool(
                name="get_articles_range",
                description="Get a range of articles from a constitution",
                input_schema={
                    "type": "object",
                    "properties": {
                        "constitution_id": {"type": "string"},
                        "start_article": {"type": "string"},
                        "end_article": {"type": "string"}
                    },
                    "required": ["constitution_id", "start_article", "end_article"]
                },
            ),
            Tool(
                name="search_articles_by_keyword",
                description="Search for articles containing specific keywords",
                input_schema={
                    "type": "object",
                    "properties": {
                        "constitution_id": {"type": "string"},
                        "keyword": {"type": "string"}
                    },
                    "required": ["constitution_id", "keyword"]
                },
            ),
            Tool(
                name="topic_constitutions",
                description="Find constitutions by topic key",
                input_schema={
                    "type": "object",
                    "properties": {
                        "topic_key": {"type": "string"},
                        "in_force": {"type": "boolean", "default": True},
                        "is_draft": {"type": "boolean", "default": False},
                        "ownership": {
                            "type": "string",
                            "enum": ["all", "public", "mine"],
                            "default": "all"
                        }
                    },
                    "required": ["topic_key"]
                },
            ),
            Tool(
                name="topic_sections",
                description="Get specific sections from a constitution related to a topic",
                input_schema={
                    "type": "object",
                    "properties": {
                        "topic_key": {"type": "string"},
                        "constitution_id": {"type": "string"},
                        "in_force": {"type": "boolean", "default": True},
                        "is_draft": {"type": "boolean", "default": False},
                        "ownership": {
                            "type": "string",
                            "enum": ["all", "public", "mine"],
                            "default": "all"
                        }
                    },
                    "required": ["topic_key", "constitution_id"]
                },
            ),
            Tool(
                name="export_constitution_json",
                description="Export constitution data as JSON",
                input_schema={
                    "type": "object",
                    "properties": {
                        "constitution_id": {"type": "string"},
                        "filename": {"type": "string"}
                    },
                    "required": ["constitution_id"]
                },
            ),
            Tool(
                name="export_constitution_text",
                description="Export constitution as plain text",
                input_schema={
                    "type": "object",
                    "properties": {
                        "constitution_id": {"type": "string"},
                        "filename": {"type": "string"}
                    },
                    "required": ["constitution_id"]
                },
            ),
            Tool(
                name="scrape_all_constitutions",
                description="Scrape all available constitutions (batch operation)",
                input_schema={
                    "type": "object",
                    "properties": {
                        "limit": {"type": "integer"},
                        "save_individual": {"type": "boolean", "default": True}
                    }
                },
            ),
        ]
        return ListToolsResult(tools=tools)

# ...略（call_tool 等維持不動）...

async def main():
    server_instance = ConstituteServer()
    async with stdio_server() as (read_stream, write_stream):
        await server_instance.server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="constitute-mcp",
                server_version="0.1.12",
                capabilities=ServerCapabilities(
                    tools={"listChanged": True},
                    prompts={"listChanged": False},    # ← 宣告 prompts 能力
                    resources={"listChanged": False},  # ← 宣告 resources 能力
                ),
            ),
        )
