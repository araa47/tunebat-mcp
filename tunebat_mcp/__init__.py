"""Tunebat MCP Server

A Model Context Protocol server that provides access to music analysis data from Tunebat.com.
"""

__version__ = "0.1.0"
__author__ = "Tunebat MCP"
__description__ = "MCP server for Tunebat music analysis data"

from .server import main

__all__ = ["main"]
