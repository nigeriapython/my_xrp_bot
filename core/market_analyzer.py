# core/market_analyzer.py
import asyncio
import logging
import pandas as pd
from typing import Dict, List, Optional
from exchanges.api_utils import APIUtils
from utils.data_utils import calculate_indicators
from utils.risk_management import check_liquidity, calculate_slippage
from utils.logger import setup_logger

# Set up logger
logger = setup_logger('MarketAnalyzer')

class MarketAnalyzer:
    def __init__(self, exchanges: Dict[str, object], config: dict):
        """
        Initialize the market analyzer with exchanges and configuration.
        """
        self.exchanges = exchanges
        self.config = config
        self.api_utils = APIUtils()
        self.historical_data = pd.DataFrame()  # Store historical market data
        self.indicators = {}  # Store calculated indicators

    async def fetch_market_data(self) -> Dict[str, dict]:
        """
        Fetch market data (order books and OHLCV) from all exchanges.
        """
        market_data = {}
        tasks = []

        # Fetch order books
        for ex_id, exchange in self.exchanges.items():
            for pair in self.config['symbol_pairs']:
                tasks.append(self.api_utils.fetch_order_book_safely(exchange, pair))

        # Fetch OHLCV data
        for ex_id, exchange in self.exchanges.items():
            for pair in self.config['symbol_pairs']:
                tasks.append(self.api_utils.fetch_ohlcv_safely(exchange, pair, timeframe='5m'))

        results = await asyncio.gather(*tasks)

        # Process order books
        idx = 0
        for ex_id in self.exchanges:
            for pair in self.config['symbol_pairs']:
                if pair not in market_data:
                    market_data[pair] = {}
                market_data[pair][ex_id] = {
                    'order_book': results[idx]
                }
                idx += 1

        # Process OHLCV data
        for ex_id in self.exchanges:
            for pair in self.config['symbol_pairs']:
                market_data[pair][ex_id]['ohlcv'] = results[idx]
                idx += 1

        return market_data

    async def update_historical_data(self):
        """
        Update historical market data for analysis.
        """
        try:
            ohlcv = await self.api_utils.fetch_ohlcv_safely(
                self.exchanges['cex'],
                'BTC/USD',
                timeframe='5m'
            )
            if ohlcv:
                new_data = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                self.historical_data = pd.concat([self.historical_data, new_data]).tail(1000)  # Keep last 1000 data points
                self.indicators = calculate_indicators(self.historical_data)
        except Exception as e:
            logger.error(f"Failed to update historical data: {e}")

    async def monitor_market_conditions(self):
        """
        Monitor market conditions (volatility, liquidity, etc.).
        """
        try:
            market_data = await self.fetch_market_data()
            volatility = self._calculate_volatility(market_data)
            liquidity = self._calculate_liquidity(market_data)

            logger.info(f"Market conditions - Volatility: {volatility}, Liquidity: {liquidity}")
        except Exception as e:
            logger.error(f"Failed to monitor market conditions: {e}")

    def _calculate_volatility(self, market_data: dict) -> float:
        """
        Calculate market volatility based on historical price changes.
        """
        if len(self.historical_data) < 2:
            return 0.0

        price_changes = self.historical_data['close'].pct_change().dropna()
        return price_changes.std() * 100  # Return volatility as a percentage

    def _calculate_liquidity(self, market_data: dict) -> float:
        """
        Calculate market liquidity based on order book depth.
        """
        liquidity = 0.0
        for pair, exchanges_data in market_data.items():
            for ex_id, data in exchanges_data.items():
                order_book = data['order_book']
                if order_book:
                    cumulative = sum(ask[1] for ask in order_book['asks'][:5])  # Top 5 ask levels
                    liquidity += cumulative
        return liquidity