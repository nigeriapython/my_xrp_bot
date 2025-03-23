# exchanges/api_utils.py
import asyncio
import logging
from typing import Any, Callable, Optional
from ccxt import NetworkError, ExchangeError, RequestTimeout

logger = logging.getLogger('APIUtils')

class APIUtils:
    @staticmethod
    async def fetch_with_retry(
        func: Callable,
        max_retries: int = 3,
        delay: float = 1.0,
        *args,
        **kwargs
    ) -> Optional[Any]:
        """Fetch data from an API with retries and exponential backoff."""
        for attempt in range(max_retries):
            try:
                result = await func(*args, **kwargs)
                return result
            except (NetworkError, ExchangeError, RequestTimeout) as e:
                logger.warning(f"Attempt {attempt + 1} failed for {func.__name__}: {str(e)}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(delay * (2 ** attempt))  # Exponential backoff
                else:
                    logger.error(f"All retries failed for {func.__name__}: {str(e)}")
                    return None
            except Exception as e:
                logger.error(f"Unexpected error in {func.__name__}: {str(e)}")
                return None

    @staticmethod
    async def fetch_order_book_safely(
        exchange,
        symbol: str,
        max_retries: int = 3,
        delay: float = 1.0
    ) -> Optional[dict]:
        """Safely fetch an order book with retries and error handling."""
        return await APIUtils.fetch_with_retry(
            exchange.fetch_order_book,
            max_retries,
            delay,
            symbol
        )

    @staticmethod
    async def fetch_ohlcv_safely(
        exchange,
        symbol: str,
        timeframe: str = '5m',
        max_retries: int = 3,
        delay: float = 1.0
    ) -> Optional[List[list]]:
        """Safely fetch OHLCV data with retries and error handling."""
        return await APIUtils.fetch_with_retry(
            exchange.fetch_ohlcv,
            max_retries,
            delay,
            symbol,
            timeframe
        )