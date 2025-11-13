"""
MCP (Model Context Protocol) Server for Odoo
"""
from .server import create_mcp_server
from .odoo_tools import OdooMCPTools

__all__ = ['create_mcp_server', 'OdooMCPTools']
