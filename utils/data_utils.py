# utils/data_utils.py
import pandas as pd
from typing import Dict, List, Optional

def process_order_books(results: list, exchanges: List[str], symbol_pairs: List[str]) -> Dict[str, dict]:
    """
    Process raw order book data into a structured format.

    Args:
        results: Raw order book data from exchanges.
        exchanges: List of exchange IDs.
        symbol_pairs: List of trading pairs.

    Returns:
        A dictionary of processed order books.
    """
    order_books = {}
    idx = 0
    for ex_id in exchanges:
        for pair in symbol_pairs:
            if pair not in order_books:
                order_books[pair] = {}
            order_books[pair][ex_id] = results[idx]
            idx += 1
    return order_books

def calculate_indicators(historical_data: pd.DataFrame) -> Dict[str, pd.Series]:
    """
    Calculate technical indicators from historical data.

    Args:
        historical_data: A DataFrame containing OHLCV data.

    Returns:
        A dictionary of calculated indicators.
    """
    indicators = {}
    if len(historical_data) < 20:  # Need at least 20 data points
        return indicators

    # Calculate Bollinger Bands
    window = 20
    sma = historical_data['close'].rolling(window).mean()
    std = historical_data['close'].rolling(window).std()
    indicators['bollinger_upper'] = sma + (std * 2)
    indicators['bollinger_lower'] = sma - (std * 2)

    # Calculate RSI
    delta = historical_data['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window).mean()
    rs = gain / loss
    indicators['rsi'] = 100 - (100 / (1 + rs))

    return indicators