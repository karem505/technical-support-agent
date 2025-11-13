"""
MCP Server implementation for Odoo
"""
import asyncio
import logging
from typing import Any
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from .odoo_tools import OdooMCPTools

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_mcp_server() -> Server:
    """Create and configure the MCP server"""
    server = Server("odoo-support-mcp")
    odoo_tools = OdooMCPTools()

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        """List available tools"""
        return [
            Tool(
                name="list_modules",
                description="List all Odoo modules with their state and version",
                inputSchema={
                    "type": "object",
                    "properties": {},
                },
            ),
            Tool(
                name="get_module_info",
                description="Get detailed information about a specific module",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "module_name": {
                            "type": "string",
                            "description": "Technical name of the module",
                        }
                    },
                    "required": ["module_name"],
                },
            ),
            Tool(
                name="list_users",
                description="List all Odoo users",
                inputSchema={
                    "type": "object",
                    "properties": {},
                },
            ),
            Tool(
                name="get_user_details",
                description="Get detailed information about a specific user",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "user_id": {
                            "type": "integer",
                            "description": "ID of the user",
                        }
                    },
                    "required": ["user_id"],
                },
            ),
            Tool(
                name="search_records",
                description="Search records in any Odoo model",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "model": {
                            "type": "string",
                            "description": "Model name (e.g., 'res.partner', 'sale.order')",
                        },
                        "domain": {
                            "type": "array",
                            "description": "Search domain (Odoo format)",
                        },
                        "fields": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Fields to retrieve",
                        },
                    },
                    "required": ["model", "domain"],
                },
            ),
            Tool(
                name="get_database_info",
                description="Get Odoo database and connection information",
                inputSchema={
                    "type": "object",
                    "properties": {},
                },
            ),
            Tool(
                name="get_company_info",
                description="Get company information from Odoo",
                inputSchema={
                    "type": "object",
                    "properties": {},
                },
            ),
            Tool(
                name="check_module_dependencies",
                description="Check dependencies for a specific module",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "module_name": {
                            "type": "string",
                            "description": "Technical name of the module",
                        }
                    },
                    "required": ["module_name"],
                },
            ),
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: Any) -> list[TextContent]:
        """Handle tool calls"""
        try:
            if name == "list_modules":
                result = await odoo_tools.list_modules()
            elif name == "get_module_info":
                result = await odoo_tools.get_module_info(arguments["module_name"])
            elif name == "list_users":
                result = await odoo_tools.list_users()
            elif name == "get_user_details":
                result = await odoo_tools.get_user_details(arguments["user_id"])
            elif name == "search_records":
                result = await odoo_tools.search_records(
                    arguments["model"],
                    arguments["domain"],
                    arguments.get("fields"),
                )
            elif name == "get_database_info":
                result = await odoo_tools.get_database_info()
            elif name == "get_company_info":
                result = await odoo_tools.get_company_info()
            elif name == "check_module_dependencies":
                result = await odoo_tools.check_module_dependencies(arguments["module_name"])
            else:
                result = {"error": f"Unknown tool: {name}"}

            return [TextContent(type="text", text=str(result))]
        except Exception as e:
            logger.error(f"Error calling tool {name}: {e}")
            return [TextContent(type="text", text=f"Error: {str(e)}")]

    return server


async def main():
    """Run the MCP server"""
    server = create_mcp_server()
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )


if __name__ == "__main__":
    asyncio.run(main())
