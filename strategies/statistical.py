# strategies/statistical.py
import pandas as pd
from typing import Dict, List, Optional

class StatisticalArbitrageStrategy:
    def __init__(self, config: dict):
        self.config = config

    async def analyze(self, historical_data: pd.DataFrame) -> List[dict]:
        """Detect statistical arbitrage opportunities using Bollinger Bands."""
        if len(historical_data) < 20:  # Need at least 20 data points
            return []

        # Calculate Bollinger Bands
        window = 20
        sma = historical_data['close'].rolling(window).mean()
        std = historical_data['close'].rolling(window).std()
        upper_band = sma + (std * 2)
        lower_band = sma - (std * 2)

        # Generate signals
        current_price = historical_data['close'].iloc[-1]
        opportunities = []
        if current_price < lower_band.iloc[-1]:
            opportunities.append({
                'pair': 'BTC/USD',
                'side': 'buy',
                'price': current_price,
                'indicator': 'bollinger_lower'
            })
        elif current_price > upper_band.iloc[-1]:
            opportunities.append({
                'pair': 'BTC/USD',
                'side': 'sell',
                'price': current_price,
                'indicator': 'bollinger_upper'
            })
        return opportunities