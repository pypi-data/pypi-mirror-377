"""
Agent Team Chat Enhanced MCP Server

A production-ready Multi-Agent Coordination System using the Model Context Protocol (MCP).
Enables natural team chat between multiple AI agents with advanced features for coordination,
webhooks, rate limiting, and documentation management.
"""

__version__ = "0.1.0"
__author__ = "Agent Team"
__email__ = "noreply@example.com"

from .server import main

__all__ = ["main"]
