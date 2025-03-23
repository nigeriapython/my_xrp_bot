# strategies/arbitrage.py
from typing import Dict, List, Optional

class ArbitrageStrategy:
    def __init__(self, exchanges: Dict[str, object], config: dict):
        self.exchanges = exchanges
        self.config = config

    def find_arbitrage(self, order_books: dict) -> List[dict]:
        """Find cross-exchange arbitrage opportunities."""
        opportunities = []
        for pair, exchanges_data in order_books.items():
            if len(exchanges_data) < 2:
                continue

            # Find the best bid and ask across exchanges
            best_bid = max(
                exchanges_data.items(),
                key=lambda x: x[1]['bids'][0][0] * (1 - self.exchanges[x[0]].fees['taker'])
            )
            best_ask = min(
                exchanges_data.items(),
                key=lambda x: x[1]['asks'][0][0] * (1 + self.exchanges[x[0]].fees['taker'])
            )

            # Calculate spread and profit
            spread = best_bid[1]['bids'][0][0] - best_ask[1]['asks'][0][0]
            if spread > 0:
                profit = spread / best_ask[1]['asks'][0][0] * 100
                if profit >= self.config['min_profit']:
                    opportunities.append({
                        'pair': pair,
                        'buy_exchange': best_ask[0],
                        'sell_exchange': best_bid[0],
                        'buy_price': best_ask[1]['asks'][0][0],
                        'sell_price': best_bid[1]['bids'][0][0],
                        'profit': profit
                    })
        return opportunities