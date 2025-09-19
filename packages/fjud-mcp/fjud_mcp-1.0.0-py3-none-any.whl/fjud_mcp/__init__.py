# -*- coding: utf-8 -*-
"""
FJUD MCP - 台灣司法院判決查詢 MCP 伺服器

A Model Context Protocol (MCP) server for querying and analyzing
Taiwan Judicial Yuan judgments.
"""

__version__ = "1.0.0"
__author__ = "Claude Code Assistant"
__email__ = "noreply@anthropic.com"
__description__ = "Taiwan Judicial Yuan judgment search MCP server"

from .server import main

__all__ = ["main"]