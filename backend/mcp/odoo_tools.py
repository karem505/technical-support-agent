"""
Odoo-specific MCP tools
"""
import os
import logging
from typing import Any, Dict, List
import odoorpc

logger = logging.getLogger(__name__)


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
        try:
            odoo = self.connect()
            Module = odoo.env['ir.module.module']
            module_ids = Module.search([])
            modules = Module.read(module_ids, ['name', 'shortdesc', 'state', 'installed_version'])
            return modules
        except Exception as e:
            logger.error(f"Error listing modules: {e}")
            return []

    async def get_module_info(self, module_name: str) -> Dict[str, Any]:
        """Get detailed information about a module"""
        try:
            odoo = self.connect()
            Module = odoo.env['ir.module.module']
            module_ids = Module.search([('name', '=', module_name)])

            if not module_ids:
                return {"error": f"Module {module_name} not found"}

            module = Module.read(module_ids[0], [
                'name', 'shortdesc', 'description', 'state',
                'installed_version', 'author', 'website', 'license'
            ])
            return module
        except Exception as e:
            logger.error(f"Error getting module info: {e}")
            return {"error": str(e)}

    async def list_users(self) -> List[Dict[str, Any]]:
        """List all users"""
        try:
            odoo = self.connect()
            User = odoo.env['res.users']
            user_ids = User.search([])
            users = User.read(user_ids, ['name', 'login', 'email', 'active'])
            return users
        except Exception as e:
            logger.error(f"Error listing users: {e}")
            return []

    async def get_user_details(self, user_id: int) -> Dict[str, Any]:
        """Get detailed user information"""
        try:
            odoo = self.connect()
            User = odoo.env['res.users']
            user = User.read(user_id, [
                'name', 'login', 'email', 'active', 'groups_id',
                'company_id', 'partner_id', 'lang', 'tz'
            ])
            return user
        except Exception as e:
            logger.error(f"Error getting user details: {e}")
            return {"error": str(e)}

    async def search_records(self, model: str, domain: List, fields: List[str] = None) -> List[Dict[str, Any]]:
        """Search records in a model"""
        try:
            odoo = self.connect()
            Model = odoo.env[model]
            record_ids = Model.search(domain)

            if fields:
                records = Model.read(record_ids, fields)
            else:
                records = Model.read(record_ids)

            return records
        except Exception as e:
            logger.error(f"Error searching records: {e}")
            return []

    async def execute_method(self, model: str, method: str, args: List = None, kwargs: Dict = None) -> Any:
        """Execute a method on a model"""
        try:
            odoo = self.connect()
            Model = odoo.env[model]

            if args is None:
                args = []
            if kwargs is None:
                kwargs = {}

            result = getattr(Model, method)(*args, **kwargs)
            return result
        except Exception as e:
            logger.error(f"Error executing method: {e}")
            return {"error": str(e)}

    async def get_database_info(self) -> Dict[str, Any]:
        """Get database information"""
        try:
            odoo = self.connect()
            return {
                "version": odoo.version,
                "database": self.db,
                "host": self.host,
                "port": self.port,
            }
        except Exception as e:
            logger.error(f"Error getting database info: {e}")
            return {"error": str(e)}

    async def get_company_info(self) -> Dict[str, Any]:
        """Get company information"""
        try:
            odoo = self.connect()
            Company = odoo.env['res.company']
            company_ids = Company.search([])

            if not company_ids:
                return {"error": "No company found"}

            companies = Company.read(company_ids, ['name', 'email', 'phone', 'website', 'currency_id'])
            return companies
        except Exception as e:
            logger.error(f"Error getting company info: {e}")
            return {"error": str(e)}

    async def check_module_dependencies(self, module_name: str) -> Dict[str, Any]:
        """Check module dependencies"""
        try:
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
        except Exception as e:
            logger.error(f"Error checking dependencies: {e}")
            return {"error": str(e)}
