"""
Odoo-specific MCP tools
"""
import os
import logging
import asyncio
from typing import Any, Dict, List
import odoorpc

logger = logging.getLogger(__name__)

# Allowlist of permitted Odoo models for search operations
ALLOWED_MODELS = {
    'res.users', 'res.partner', 'res.company',
    'ir.module.module', 'ir.module.module.dependency',
    'sale.order', 'purchase.order', 'account.move',
    'stock.picking', 'product.product', 'product.template',
}


class OdooMCPTools:
    """MCP tools for Odoo operations"""

    def __init__(self):
        self.host = os.getenv("ODOO_HOST", "localhost")
        self.port = int(os.getenv("ODOO_PORT", "8069"))
        self.db = os.getenv("ODOO_DB", "odoo")
        self.username = os.getenv("ODOO_USERNAME", "admin")
        self.password = os.getenv("ODOO_PASSWORD", "admin")
        self.odoo = None

    def connect(self):
        """Establish connection to Odoo"""
        if not self.odoo:
            try:
                self.odoo = odoorpc.ODOO(self.host, port=self.port)
                self.odoo.login(self.db, self.username, self.password)
                logger.info(f"Connected to Odoo at {self.host}:{self.port}")
            except Exception as e:
                logger.error(f"Failed to connect to Odoo: {e}")
                raise
        return self.odoo

    def disconnect(self):
        """Close Odoo connection"""
        if self.odoo:
            try:
                self.odoo.logout()
                self.odoo = None
                logger.info("Disconnected from Odoo")
            except Exception as e:
                logger.error(f"Error disconnecting from Odoo: {e}")

    async def list_modules(self) -> List[Dict[str, Any]]:
        """List all Odoo modules"""
        def _list_modules():
            odoo = self.connect()
            Module = odoo.env['ir.module.module']
            module_ids = Module.search([])
            modules = Module.read(module_ids, ['name', 'shortdesc', 'state', 'installed_version'])
            return modules

        try:
            return await asyncio.to_thread(_list_modules)
        except Exception as e:
            logger.error(f"Error listing modules: {e}")
            return []

    async def get_module_info(self, module_name: str) -> Dict[str, Any]:
        """Get detailed information about a module"""
        def _get_module_info():
            odoo = self.connect()
            Module = odoo.env['ir.module.module']
            module_ids = Module.search([('name', '=', module_name)])

            if not module_ids:
                return {"error": f"Module {module_name} not found"}

            modules = Module.read(module_ids[0], [
                'name', 'shortdesc', 'description', 'state',
                'installed_version', 'author', 'website', 'license'
            ])
            # read() returns a list even for single ID
            return modules[0] if isinstance(modules, list) else modules

        try:
            return await asyncio.to_thread(_get_module_info)
        except Exception as e:
            logger.error(f"Error getting module info: {e}")
            return {"error": str(e)}

    async def list_users(self) -> List[Dict[str, Any]]:
        """List all users"""
        def _list_users():
            odoo = self.connect()
            User = odoo.env['res.users']
            user_ids = User.search([])
            users = User.read(user_ids, ['name', 'login', 'email', 'active'])
            return users

        try:
            return await asyncio.to_thread(_list_users)
        except Exception as e:
            logger.error(f"Error listing users: {e}")
            return []

    async def get_user_details(self, user_id: int) -> Dict[str, Any]:
        """Get detailed user information"""
        def _get_user_details():
            odoo = self.connect()
            User = odoo.env['res.users']
            users = User.read(user_id, [
                'name', 'login', 'email', 'active', 'groups_id',
                'company_id', 'partner_id', 'lang', 'tz'
            ])
            # read() returns a list even for single ID
            return users[0] if isinstance(users, list) else users

        try:
            return await asyncio.to_thread(_get_user_details)
        except Exception as e:
            logger.error(f"Error getting user details: {e}")
            return {"error": str(e)}

    async def search_records(self, model: str, domain: List, fields: List[str] = None) -> List[Dict[str, Any]]:
        """Search records in a model"""
        # Validate model against allowlist
        if model not in ALLOWED_MODELS:
            logger.warning(f"Attempted access to non-allowed model: {model}")
            return {"error": f"Model '{model}' is not in the allowed list"}

        def _search_records():
            odoo = self.connect()
            Model = odoo.env[model]
            record_ids = Model.search(domain)

            if fields:
                records = Model.read(record_ids, fields)
            else:
                records = Model.read(record_ids)

            return records

        try:
            return await asyncio.to_thread(_search_records)
        except Exception as e:
            logger.error(f"Error searching records: {e}")
            return []

    async def get_database_info(self) -> Dict[str, Any]:
        """Get database information"""
        def _get_database_info():
            odoo = self.connect()
            return {
                "version": odoo.version,
                "database": self.db,
                "host": self.host,
                "port": self.port,
            }

        try:
            return await asyncio.to_thread(_get_database_info)
        except Exception as e:
            logger.error(f"Error getting database info: {e}")
            return {"error": str(e)}

    async def get_company_info(self) -> Dict[str, Any]:
        """Get company information"""
        def _get_company_info():
            odoo = self.connect()
            Company = odoo.env['res.company']
            company_ids = Company.search([])

            if not company_ids:
                return {"error": "No company found"}

            companies = Company.read(company_ids, ['name', 'email', 'phone', 'website', 'currency_id'])
            return companies

        try:
            return await asyncio.to_thread(_get_company_info)
        except Exception as e:
            logger.error(f"Error getting company info: {e}")
            return {"error": str(e)}

    async def check_module_dependencies(self, module_name: str) -> Dict[str, Any]:
        """Check module dependencies"""
        def _check_dependencies():
            odoo = self.connect()
            Module = odoo.env['ir.module.module']
            Dependency = odoo.env['ir.module.module.dependency']

            module_ids = Module.search([('name', '=', module_name)])
            if not module_ids:
                return {"error": f"Module {module_name} not found"}

            dependency_ids = Dependency.search([('module_id', '=', module_ids[0])])
            dependencies = Dependency.read(dependency_ids, ['name', 'state'])

            return {
                "module": module_name,
                "dependencies": dependencies
            }

        try:
            return await asyncio.to_thread(_check_dependencies)
        except Exception as e:
            logger.error(f"Error checking dependencies: {e}")
            return {"error": str(e)}
