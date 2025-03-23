# core/bot.py
import asyncio
import logging
from typing import Dict, List
import pandas as pd
from exchanges.exchange_manager import ExchangeManager
from strategies.arbitrage import ArbitrageStrategy
from strategies.triangular import TriangularArbitrageStrategy
from strategies.statistical import StatisticalArbitrageStrategy
from core.trade_executor import TradeExecutor
from core.market_analyzer import MarketAnalyzer
from exchanges.api_utils import APIUtils
from utils.logger import setup_logger
from utils.data_utils import process_order_books
from utils.risk_management import check_liquidity, calculate_slippage

# Set up logger
logger = setup_logger('ArbitrageBot', log_file='arbitrage.log')

class ArbitrageBot:
    def __init__(self, config: dict):
        """
        Initialize the arbitrage bot with all strategies and components.
        """
        self.config = config
        self.exchange_manager = ExchangeManager(config)
        self.market_analyzer = MarketAnalyzer(self.exchange_manager.exchanges, config)
        self.arbitrage_strategy = ArbitrageStrategy(self.exchange_manager.exchanges, config)
        self.triangular_strategy = TriangularArbitrageStrategy(self.exchange_manager.exchanges, config)
        self.statistical_strategy = StatisticalArbitrageStrategy(config)
        self.trade_executor = TradeExecutor(self.exchange_manager.exchanges, config)
        self.api_utils = APIUtils()

    async def run(self):
        """
        Main bot loop with market analysis, arbitrage detection, and trade execution.
        """
        while True:
            try:
                # Fetch and process market data
                market_data = await self.market_analyzer.fetch_market_data()
                if not market_data:
                    logger.warning("Failed to fetch market data")
                    await asyncio.sleep(self.config['poll_interval'])
                    continue

                # Update historical data and calculate indicators
                await self.market_analyzer.update_historical_data()

                # Monitor market conditions
                await self.market_analyzer.monitor_market_conditions()

                # Find arbitrage opportunities
                cross_arbitrage_ops = self.arbitrage_strategy.find_arbitrage(market_data)
                triangular_ops = self.triangular_strategy.find_triangular_arbitrage(market_data)
                statistical_ops = await self.statistical_strategy.analyze(self.market_analyzer.historical_data)

                # Execute trades
                await self.trade_executor.execute_trades(
                    cross_arbitrage_ops + triangular_ops + statistical_ops
                )

                await asyncio.sleep(self.config['poll_interval'])
            except Exception as e:
                logger.error(f"Error in main loop: {e}")
                await asyncio.sleep(60)

    async def _fetch_all_order_books(self) -> Dict[str, dict]:
        """
        Fetch order books from all exchanges with retries.
        """
        tasks = []
        for ex_id, exchange in self.exchange_manager.exchanges.items():
            for pair in self.config['symbol_pairs']:
                tasks.append(self.api_utils.fetch_order_book_safely(exchange, pair))
        results = await asyncio.gather(*tasks)
        return process_order_books(results, list(self.exchange_manager.exchanges.keys()), self.config['symbol_pairs'])

    async def _update_historical_data(self):
        """
        Update historical market data for statistical analysis.
        """
        try:
            ohlcv = await self.api_utils.fetch_ohlcv_safely(
                self.exchange_manager.exchanges['cex'],
                'BTC/USD',
                timeframe='5m'
            )
            if ohlcv:
                new_data = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                self.market_analyzer.historical_data = pd.concat([self.market_analyzer.historical_data, new_data]).tail(1000)  # Keep last 1000 data points
        except Exception as e:
            logger.error(f"Failed to update historical data: {e}")