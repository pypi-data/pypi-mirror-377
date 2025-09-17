# financial_analyzer_server/src/financial_analyzer_mcp_server/tools/inflation_tools.py
# Les imports doivent être absolus depuis le package
from financial_analyzer_mcp_server.server import mcp
from financial_analyzer_mcp_server.utils.financial_calculator import calculate_ratio_and_ma_signal

@mcp.tool()
def get_inflation_signal(gold_ticker: str, bond_ticker: str) -> str:
    """
    Analyse le ratio Or / Obligations d'État et sa moyenne mobile sur 7 ans pour détecter une période inflationniste ou non.
    Args:
        gold_ticker: Symbole de l'actif Or (ex: 'XAUUSD' pour l'or en USD).
        bond_ticker: Symbole de l'ETF d'obligations d'État (ex: 'IFGB.PA' pour un ETF français, 'EGB.PA' pour un ETF Euro).
    Returns:
        Un signal indiquant si la période est inflationniste ou non, et la stratégie associée.
    """
    return calculate_ratio_and_ma_signal(gold_ticker, bond_ticker, "inflation")