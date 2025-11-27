"""
Agent tools for Odoo operations
"""
import os
import asyncio
from collections import deque
import odoorpc
from livekit.agents.llm import function_tool


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
            # odoorpc doesn't have a logout method, just clear the reference
            self.odoo = None


# Global connection instance
odoo_conn = OdooConnection()


@function_tool
async def check_odoo_status() -> str:
    """Check if the Odoo instance is running and accessible."""
    def _check_status():
        odoo = odoo_conn.connect()
        version = odoo.version
        return f"Odoo instance is running. Version: {version}"

    try:
        return await asyncio.to_thread(_check_status)
    except Exception as e:
        return f"Unable to connect to Odoo instance: {str(e)}"


@function_tool
async def get_installed_modules() -> str:
    """Get a list of all installed Odoo modules."""
    def _get_modules():
        odoo = odoo_conn.connect()
        Module = odoo.env['ir.module.module']
        module_ids = Module.search([('state', '=', 'installed')])
        modules = Module.read(module_ids, ['name', 'shortdesc', 'installed_version'])

        result = "Installed Modules:\n"
        for module in modules:
            result += f"- {module['name']} ({module['shortdesc']}): v{module['installed_version']}\n"

        return result

    try:
        return await asyncio.to_thread(_get_modules)
    except Exception as e:
        return f"Error retrieving modules: {str(e)}"


@function_tool
async def install_module(module_name: str) -> str:
    """Install a specific Odoo module by name.

    Args:
        module_name: The technical name of the module to install
    """
    def _install():
        odoo = odoo_conn.connect()
        Module = odoo.env['ir.module.module']
        module_ids = Module.search([('name', '=', module_name)])

        if not module_ids:
            return f"Module '{module_name}' not found in the system"

        Module.button_immediate_install(module_ids)
        return f"Successfully installed module: {module_name}"

    try:
        return await asyncio.to_thread(_install)
    except Exception as e:
        return f"Error installing module: {str(e)}"


@function_tool
async def update_module(module_name: str) -> str:
    """Update a specific Odoo module by name.

    Args:
        module_name: The technical name of the module to update
    """
    def _update():
        odoo = odoo_conn.connect()
        Module = odoo.env['ir.module.module']
        module_ids = Module.search([('name', '=', module_name)])

        if not module_ids:
            return f"Module '{module_name}' not found in the system"

        Module.button_immediate_upgrade(module_ids)
        return f"Successfully updated module: {module_name}"

    try:
        return await asyncio.to_thread(_update)
    except Exception as e:
        return f"Error updating module: {str(e)}"


@function_tool
async def get_user_info(user_identifier: str) -> str:
    """Get information about a user by email or login.

    Args:
        user_identifier: Email or login of the user
    """
    def _get_user_info():
        odoo = odoo_conn.connect()
        User = odoo.env['res.users']
        user_ids = User.search([
            '|',
            ('login', '=', user_identifier),
            ('email', '=', user_identifier)
        ])

        if not user_ids:
            return f"User '{user_identifier}' not found"

        users = User.read(user_ids[0], ['name', 'login', 'email', 'active', 'groups_id'])
        # read() returns a list even for single ID
        user = users[0] if isinstance(users, list) else users

        result = f"User Information:\n"
        result += f"Name: {user['name']}\n"
        result += f"Login: {user['login']}\n"
        result += f"Email: {user['email']}\n"
        result += f"Active: {user['active']}\n"
        result += f"Groups: {len(user['groups_id'])} groups assigned\n"

        return result

    try:
        return await asyncio.to_thread(_get_user_info)
    except Exception as e:
        return f"Error retrieving user info: {str(e)}"


@function_tool
async def create_user(name: str, login: str, email: str, password: str) -> str:
    """Create a new Odoo user.

    Args:
        name: Full name of the user
        login: Login username
        email: Email address
        password: Initial password
    """
    def _create_user():
        odoo = odoo_conn.connect()
        User = odoo.env['res.users']

        user_id = User.create({
            'name': name,
            'login': login,
            'email': email,
            'password': password
        })

        return f"Successfully created user: {name} (ID: {user_id})"

    try:
        return await asyncio.to_thread(_create_user)
    except Exception as e:
        return f"Error creating user: {str(e)}"


@function_tool
async def reset_user_password(user_identifier: str, new_password: str) -> str:
    """Reset a user's password.

    Args:
        user_identifier: Email or login of the user
        new_password: New password for the user
    """
    def _reset_password():
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

    try:
        return await asyncio.to_thread(_reset_password)
    except Exception as e:
        return f"Error resetting password: {str(e)}"


@function_tool
async def get_server_logs(lines: int = 50) -> str:
    """Get recent server logs to help diagnose issues.

    Args:
        lines: Number of recent log lines to retrieve (default: 50)
    """
    def _get_logs():
        log_file = os.getenv("ODOO_LOG_FILE", "/var/log/odoo/odoo-server.log")

        if not os.path.exists(log_file):
            return f"Log file not found at: {log_file}"

        # Use deque with maxlen to efficiently read only the last N lines
        # This avoids loading the entire file into memory
        with open(log_file, 'r') as f:
            recent_lines = deque(f, maxlen=lines)

        return "Recent Server Logs:\n" + "".join(recent_lines)

    try:
        return await asyncio.to_thread(_get_logs)
    except Exception as e:
        return f"Error reading logs: {str(e)}"


@function_tool
async def analyze_error(error_message: str) -> str:
    """Analyze an error message and suggest solutions.

    Args:
        error_message: The error message to analyze
    """
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
