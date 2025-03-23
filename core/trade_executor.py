# core/trade_executor.py
import asyncio
import logging
from typing import List, Dict
from exchanges.api_utils import APIUtils
from utils.risk_management import check_liquidity, calculate_slippage
from utils.logger import setup_logger

# Set up logger
logger = setup_logger('TradeExecutor')

class TradeExecutor:
    def __init__(self, exchanges: Dict[str, object], config: dict):
        self.exchanges = exchanges
        self.config = config
        self.api_utils = APIUtils()

    async def execute_trades(self, opportunities: List[dict]):
        """Execute profitable trades with risk management."""
        for opp in sorted(opportunities, key=lambda x: x['profit'], reverse=True):
            if opp['profit'] >= self.config['min_profit']:
                logger.info(f"Executing opportunity: {opp}")
                if await self._execute_trade(opp):
                    logger.info("Trade executed successfully")
                    await asyncio.sleep(self.config['cooldown'])
                    break

    async def _execute_trade(self, opportunity: dict) -> bool:
        """Execute a single trade with slippage and liquidity checks."""
        try:
            buy_ex = self.exchanges[opportunity['buy_exchange']]
            sell_ex = self.exchanges[opportunity['sell_exchange']]
            pair = opportunity['pair']

            # Verify liquidity
            if not await self._check_liquidity(buy_ex, pair, self.config['trade_amount']):
                logger.warning(f"Insufficient liquidity for {pair} on {opportunity['buy_exchange']}")
                return False

            # Execute buy order with slippage protection
            buy_price = opportunity['buy_price'] * (1 - self.config['slippage_tolerance'])
            buy_order = await self.api_utils.create_order_safely(
                buy_ex,
                symbol=pair,
                side='buy',
                amount=self.config['trade_amount'],
                order_type='limit',
                price=buy_price
            )
            if buy_order is None:
                return False

            # Execute sell order with slippage protection
            sell_price = opportunity['sell_price'] * (1 + self.config['slippage_tolerance'])
            sell_order = await self.api_utils.create_order_safely(
                sell_ex,
                symbol=pair,
                side='sell',
                amount=self.config['trade_amount'],
                order_type='limit',
                price=sell_price
            )
            if sell_order is None:
                return False

            logger.info(f"Executed orders: Buy {buy_order} | Sell {sell_order}")
            return True
        except Exception as e:
            logger.error(f"Trade execution failed: {e}")
            return False

    async def _check_liquidity(self, exchange, symbol: str, amount: float) -> bool:
        """Check if there is sufficient liquidity for the trade."""
        order_book = await self.api_utils.fetch_order_book_safely(exchange, symbol)
        if order_book is None:
            return False

        cumulative = 0
        for ask in order_book['asks']:
            cumulative += ask[1]
            if cumulative >= amount:
                return True
        return False