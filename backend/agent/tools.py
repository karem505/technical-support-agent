"""
Agent tools for Odoo operations
"""
import os
from typing import Annotated
import odoorpc
from livekit.agents import llm


class OdooConnection:
    """Manage Odoo connection"""

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
            self.odoo = odoorpc.ODOO(self.host, port=self.port)
            self.odoo.login(self.db, self.username, self.password)
        return self.odoo

    def disconnect(self):
        """Close Odoo connection"""
        if self.odoo:
            self.odoo.logout()
            self.odoo = None


# Global connection instance
odoo_conn = OdooConnection()


class OdooTools:
    """Collection of Odoo support tools"""

    @llm.ai_callable(
        description="Check if the Odoo instance is running and accessible"
    )
    async def check_odoo_status(self) -> str:
        """Check Odoo instance status"""
        try:
            odoo = odoo_conn.connect()
            version = odoo.version
            return f"Odoo instance is running. Version: {version}"
        except Exception as e:
            return f"Unable to connect to Odoo instance: {str(e)}"

    @llm.ai_callable(
        description="Get a list of all installed Odoo modules"
    )
    async def get_installed_modules(self) -> str:
        """List all installed modules"""
        try:
            odoo = odoo_conn.connect()
            Module = odoo.env['ir.module.module']
            module_ids = Module.search([('state', '=', 'installed')])
            modules = Module.read(module_ids, ['name', 'shortdesc', 'installed_version'])

            result = "Installed Modules:\n"
            for module in modules:
                result += f"- {module['name']} ({module['shortdesc']}): v{module['installed_version']}\n"

            return result
        except Exception as e:
            return f"Error retrieving modules: {str(e)}"

    @llm.ai_callable(
        description="Install a specific Odoo module by name"
    )
    async def install_module(
        self,
        module_name: Annotated[str, llm.TypeInfo(description="The technical name of the module to install")]
    ) -> str:
        """Install a module"""
        try:
            odoo = odoo_conn.connect()
            Module = odoo.env['ir.module.module']
            module_ids = Module.search([('name', '=', module_name)])

            if not module_ids:
                return f"Module '{module_name}' not found in the system"

            Module.button_immediate_install(module_ids)
            return f"Successfully installed module: {module_name}"
        except Exception as e:
            return f"Error installing module: {str(e)}"

    @llm.ai_callable(
        description="Update a specific Odoo module by name"
    )
    async def update_module(
        self,
        module_name: Annotated[str, llm.TypeInfo(description="The technical name of the module to update")]
    ) -> str:
        """Update a module"""
        try:
            odoo = odoo_conn.connect()
            Module = odoo.env['ir.module.module']
            module_ids = Module.search([('name', '=', module_name)])

            if not module_ids:
                return f"Module '{module_name}' not found in the system"

            Module.button_immediate_upgrade(module_ids)
            return f"Successfully updated module: {module_name}"
        except Exception as e:
            return f"Error updating module: {str(e)}"

    @llm.ai_callable(
        description="Get information about a user by email or login"
    )
    async def get_user_info(
        self,
        user_identifier: Annotated[str, llm.TypeInfo(description="Email or login of the user")]
    ) -> str:
        """Get user information"""
        try:
            odoo = odoo_conn.connect()
            User = odoo.env['res.users']
            user_ids = User.search([
                '|',
                ('login', '=', user_identifier),
                ('email', '=', user_identifier)
            ])

            if not user_ids:
                return f"User '{user_identifier}' not found"

            user = User.read(user_ids[0], ['name', 'login', 'email', 'active', 'groups_id'])

            result = f"User Information:\n"
            result += f"Name: {user['name']}\n"
            result += f"Login: {user['login']}\n"
            result += f"Email: {user['email']}\n"
            result += f"Active: {user['active']}\n"
            result += f"Groups: {len(user['groups_id'])} groups assigned\n"

            return result
        except Exception as e:
            return f"Error retrieving user info: {str(e)}"

    @llm.ai_callable(
        description="Create a new Odoo user"
    )
    async def create_user(
        self,
        name: Annotated[str, llm.TypeInfo(description="Full name of the user")],
        login: Annotated[str, llm.TypeInfo(description="Login username")],
        email: Annotated[str, llm.TypeInfo(description="Email address")],
        password: Annotated[str, llm.TypeInfo(description="Initial password")]
    ) -> str:
        """Create a new user"""
        try:
            odoo = odoo_conn.connect()
            User = odoo.env['res.users']

            user_id = User.create({
                'name': name,
                'login': login,
                'email': email,
                'password': password
            })

            return f"Successfully created user: {name} (ID: {user_id})"
        except Exception as e:
            return f"Error creating user: {str(e)}"

    @llm.ai_callable(
        description="Reset a user's password"
    )
    async def reset_user_password(
        self,
        user_identifier: Annotated[str, llm.TypeInfo(description="Email or login of the user")],
        new_password: Annotated[str, llm.TypeInfo(description="New password for the user")]
    ) -> str:
        """Reset user password"""
        try:
            odoo = odoo_conn.connect()
            User = odoo.env['res.users']
            user_ids = User.search([
                '|',
                ('login', '=', user_identifier),
                ('email', '=', user_identifier)
            ])

            if not user_ids:
                return f"User '{user_identifier}' not found"

            User.write(user_ids[0], {'password': new_password})
            return f"Successfully reset password for user: {user_identifier}"
        except Exception as e:
            return f"Error resetting password: {str(e)}"

    @llm.ai_callable(
        description="Get recent server logs to help diagnose issues"
    )
    async def get_server_logs(
        self,
        lines: Annotated[int, llm.TypeInfo(description="Number of recent log lines to retrieve")] = 50
    ) -> str:
        """Get server logs"""
        try:
            log_file = os.getenv("ODOO_LOG_FILE", "/var/log/odoo/odoo-server.log")

            if not os.path.exists(log_file):
                return f"Log file not found at: {log_file}"

            with open(log_file, 'r') as f:
                all_lines = f.readlines()
                recent_lines = all_lines[-lines:]

            return "Recent Server Logs:\n" + "".join(recent_lines)
        except Exception as e:
            return f"Error reading logs: {str(e)}"

    @llm.ai_callable(
        description="Analyze an error message and suggest solutions"
    )
    async def analyze_error(
        self,
        error_message: Annotated[str, llm.TypeInfo(description="The error message to analyze")]
    ) -> str:
        """Analyze error and suggest solutions"""
        # Common Odoo error patterns and solutions
        solutions = {
            "Access Denied": "This is typically a permissions issue. Check user access rights and security groups.",
            "Module not found": "The module may not be installed or the technical name is incorrect.",
            "Database locked": "Another process may be using the database. Check for running upgrades or backups.",
            "psycopg2": "This is a PostgreSQL database error. Check database connectivity and permissions.",
            "ImportError": "A Python dependency is missing. Check that all required packages are installed.",
            "ValidationError": "Data validation failed. Check that all required fields are filled correctly.",
            "MissingError": "A record was not found. It may have been deleted or the ID is incorrect.",
        }

        result = f"Error Analysis for: {error_message}\n\n"

        for pattern, solution in solutions.items():
            if pattern.lower() in error_message.lower():
                result += f"Possible cause: {solution}\n"

        if result == f"Error Analysis for: {error_message}\n\n":
            result += "No specific pattern matched. Please provide more context or check the server logs."

        return result
