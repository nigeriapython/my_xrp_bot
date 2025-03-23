# utils/risk_management.py
from typing import Dict, Optional

def check_liquidity(order_book: Dict[str, list], amount: float) -> bool:
    """
    Check if there is sufficient liquidity for a trade.

    Args:
        order_book: The order book data.
        amount: The amount to trade.

    Returns:
        True if there is sufficient liquidity, False otherwise.
    """
    cumulative = 0
    for ask in order_book['asks']:
        cumulative += ask[1]
        if cumulative >= amount:
            return True
    return False

def calculate_slippage(order_book: Dict[str, list], amount: float) -> float:
    """
    Calculate the expected slippage for a trade.

    Args:
        order_book: The order book data.
        amount: The amount to trade.

    Returns:
        The expected slippage as a percentage.
    """
    cumulative = 0
    slippage = 0.0
    for ask in order_book['asks']:
        if cumulative + ask[1] >= amount:
            slippage += (amount - cumulative) * (ask[0] - order_book['asks'][0][0])
            break
        else:
            slippage += ask[1] * (ask[0] - order_book['asks'][0][0])
            cumulative += ask[1]
    return (slippage / amount) * 100