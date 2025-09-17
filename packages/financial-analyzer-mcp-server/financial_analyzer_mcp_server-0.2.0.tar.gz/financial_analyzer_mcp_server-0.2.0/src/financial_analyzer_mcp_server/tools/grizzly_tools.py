# financial_analyzer_server/src/financial_analyzer_mcp_server/tools/grizzly_tools.py
# Les imports doivent être absolus depuis le package
from financial_analyzer_mcp_server.server import mcp
from financial_analyzer_mcp_server.utils.financial_calculator import calculate_ratio_and_ma_signal

@mcp.tool()
def get_grizzly_signal(action_ticker: str, gold_ticker: str) -> str:
    """
    Analyse le ratio Actions / Or et sa moyenne mobile sur 7 ans pour détecter un signal 'Grizzly' (destruction de valeur pour les actions).
    Args:
        action_ticker: Symbole de l'indice ou de l'ETF d'actions (ex: 'SPY' pour S&P 500, '^FCHI' pour CAC40).
        gold_ticker: Symbole de l'actif Or (ex: 'XAUUSD' pour l'or en USD).
    Returns:
        Un signal indiquant si l'investissement en actions est favorable ou si un 'Grizzly' est détecté.
    """
    return calculate_ratio_and_ma_signal(action_ticker, gold_ticker, "grizzly")