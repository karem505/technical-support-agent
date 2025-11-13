"""
Odoo Technical Support Agent
"""
from .agent import OdooSupportAgent
from .tools import OdooTools
from .prompts import SYSTEM_PROMPT, GREETING_PROMPT

__all__ = ['OdooSupportAgent', 'OdooTools', 'SYSTEM_PROMPT', 'GREETING_PROMPT']
