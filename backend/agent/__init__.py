"""
Odoo Technical Support Agent
"""
from .agent import OdooSupportAgent
from .tools import (
    check_odoo_status,
    get_installed_modules,
    install_module,
    update_module,
    get_user_info,
    create_user,
    reset_user_password,
    get_server_logs,
    analyze_error,
)
from .prompts import SYSTEM_PROMPT, GREETING_PROMPT

__all__ = [
    'OdooSupportAgent',
    'SYSTEM_PROMPT',
    'GREETING_PROMPT',
    'check_odoo_status',
    'get_installed_modules',
    'install_module',
    'update_module',
    'get_user_info',
    'create_user',
    'reset_user_password',
    'get_server_logs',
    'analyze_error',
]
