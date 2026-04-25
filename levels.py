import ccxt
import time

class LevelsTracker:
    def __init__(self, symbol='BTCUSDT'):
        self.symbol = symbol
        self.exchange = ccxt.bybit()
        self.levels = {'high': None, 'low': None}

    def fetch_levels(self):
        """Получаем High/Low за последние 24 свечи (таймфрейм 1ч)"""
        try:
            ohlcv = self.exchange.fetch_ohlcv(self.symbol, timeframe='1h', limit=24)
            highs = [x[2] for x in ohlcv]
            lows = [x[3] for x in ohlcv]
            self.levels['high'] = max(highs)
            self.levels['low'] = min(lows)
            return self.levels
        except Exception as e:
            print(f"Error fetching levels: {e}")
            return None
