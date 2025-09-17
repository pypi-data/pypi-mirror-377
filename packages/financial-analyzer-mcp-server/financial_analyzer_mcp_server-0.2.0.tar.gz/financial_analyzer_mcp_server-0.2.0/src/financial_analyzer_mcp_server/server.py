# financial_analyzer_server/src/financial_analyzer_mcp_server/server.py
from mcp.server.fastmcp import FastMCP
# C'est l'instance partagée du serveur MCP.
# Le nom "financial_analyzer" sera visible dans Claude for Desktop.
mcp = FastMCP("financial_analyzer")