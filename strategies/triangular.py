# strategies/triangular.py
from typing import Dict, List, Optional

class TriangularArbitrageStrategy:
    def __init__(self, exchanges: Dict[str, object], config: dict):
        self.exchanges = exchanges
        self.config = config

    def find_triangular_arbitrage(self, prices: dict) -> List[dict]:
        """Find triangular arbitrage opportunities."""
        opportunities = []
        triangles = [
            ('BTC/USD', 'ETH/BTC', 'ETH/USD'),
            ('ETH/USD', 'BTC/ETH', 'BTC/USD')
        ]

        for triangle in triangles:
            try:
                # Get prices from both exchanges
                a_ask = prices[triangle[0]]['cex']['asks'][0][0]
                b_ask = prices[triangle[1]]['kraken']['asks'][0][0]
                c_bid = prices[triangle[2]]['cex']['bids'][0][0]

                # Calculate theoretical output
                theoretical = (1 / a_ask) / b_ask * c_bid
                if theoretical > 1.005:  # 0.5% threshold
                    opportunities.append({
                        'path': triangle,
                        'profit': (theoretical - 1) * 100
                    })
            except KeyError:
                continue
        return opportunities