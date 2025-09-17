# financial_analyzer_server/utils/financial_calculator.py
import yfinance as yf
import pandas as pd
import pandas_ta as ta
from pathlib import Path

# Définition de la longueur de la moyenne mobile (7 ans * 12 mois)
MA_LENGTH_MONTHS = 7 * 12

def get_monthly_close_data(ticker: str, years: int = 20) -> pd.Series:
    """
    Récupère les prix de clôture mensuels pour un ticker donné.
    Utilise 20 ans de données pour s'assurer d'avoir suffisamment pour la MA 7 ans.
    """
    try:
        data = yf.Ticker(ticker).history(period=f"{years}y", interval="1mo")
        if data.empty or 'Close' not in data:
            raise ValueError(f"Aucune donnée de clôture trouvée pour le ticker: {ticker}")
        return data['Close']
    except Exception as e:
        raise RuntimeError(f"Erreur lors de la récupération des données pour {ticker}: {e}")

def calculate_ratio_and_ma_signal(
    numerator_ticker: str,
    denominator_ticker: str,
    signal_type: str # "inflation" ou "grizzly"
) -> str:
    """
    Calcule le ratio entre deux actifs, sa moyenne mobile sur 7 ans et retourne un signal.
    """
    try:
        # Récupération des données
        price_num = get_monthly_close_data(numerator_ticker)
        price_den = get_monthly_close_data(denominator_ticker)

        # Aligner les données sur le même index temporel et gérer les valeurs manquantes
        combined_prices = pd.DataFrame({'num': price_num, 'den': price_den}).dropna()

        if combined_prices.empty or len(combined_prices) < MA_LENGTH_MONTHS:
            return f"Erreur: Données historiques insuffisantes ou non alignées pour {numerator_ticker} et {denominator_ticker} sur {MA_LENGTH_MONTHS} mois. Nécessite au moins {MA_LENGTH_MONTHS} points de données."

        # Calcul du ratio
        ratio = combined_prices['num'] / combined_prices['den']

        # Calcul de la moyenne mobile (SMA)
        ratio_ma = ta.sma(ratio, length=MA_LENGTH_MONTHS)

        # Assurez-vous que la MA est calculée jusqu'à la dernière période
        if ratio_ma.empty or pd.isna(ratio_ma.iloc[-1]):
            return "Erreur: Impossible de calculer la moyenne mobile jusqu'à la dernière période avec les données disponibles."

        current_ratio = ratio.iloc[-1]
        current_ma = ratio_ma.iloc[-1]

        # Génération du signal selon la méthode du livre
        if signal_type == "inflation":
            if current_ratio > current_ma:
                return (f"Analyse Inflation (Ratio {numerator_ticker}/{denominator_ticker}):\n"
                        f"Ratio actuel ({current_ratio:.4f}) est AU-DESSUS de sa MA 7 ans ({current_ma:.4f}).\n"
                        f"Cela suggère une période **INFLATIONNISTE**. Privilégiez l'**OR** dans la partie dynamique de votre portefeuille.")
            else:
                return (f"Analyse Inflation (Ratio {numerator_ratio}/{denominator_ticker}):\n"
                        f"Ratio actuel ({current_ratio:.4f}) est EN-DESSOUS de sa MA 7 ans ({current_ma:.4f}).\n"
                        f"Cela suggère une période **NON-INFLATIONNISTE**. Privilégiez les **OBLIGATIONS D'ÉTAT** dans la partie dynamique de votre portefeuille.")
        elif signal_type == "grizzly":
            if current_ratio > current_ma:
                return (f"Analyse Grizzly (Ratio {numerator_ticker}/{denominator_ticker}):\n"
                        f"Ratio actuel ({current_ratio:.4f}) est AU-DESSUS de sa MA 7 ans ({current_ma:.4f}).\n"
                        f"L'investissement en **ACTIONS** est favorable. Pas de signal 'Grizzly'.")
            else:
                return (f"Analyse Grizzly (Ratio {numerator_ticker}/{denominator_ticker}):\n"
                        f"Ratio actuel ({current_ratio:.4f}) est EN-DESSOUS de sa MA 7 ans ({current_ma:.4f}).\n"
                        f"ATTENTION : Signal '**Grizzly**' détecté ! Envisagez de **sortir des ACTIONS** et de vous positionner en **OR et/ou CASH**.")
        else:
            return "Erreur : Type de signal inconnu. Utilisez 'inflation' ou 'grizzly'."

    except RuntimeError as e:
        return f"Erreur de récupération de données: {e}"
    except Exception as e:
        return f"Une erreur inattendue est survenue lors du calcul: {e}"