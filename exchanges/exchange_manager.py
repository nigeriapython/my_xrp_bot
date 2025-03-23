# exchanges/exchange_manager.py
import ccxt
from typing import Dict

class ExchangeManager:
    def __init__(self, config: dict):
        self.config = config
        self.exchanges = self._initialize_exchanges()

    def _initialize_exchanges(self) -> Dict[str, ccxt.Exchange]:
        """Initialize exchange instances with API credentials."""
        exchanges = {}
        for ex_id, credentials in self.config['exchanges'].items():
            exchange_class = getattr(ccxt, ex_id)
            exchanges[ex_id] = exchange_class({
                'apiKey': credentials['api_key'],
                'secret': credentials['api_secret'],
                'enableRateLimit': True
            })
        return exchanges

    def get_exchange(self, exchange_id: str) -> ccxt.Exchange:
        """Get an exchange instance by ID."""
        return self.exchanges.get(exchange_id)