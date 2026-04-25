import asyncio
import ccxt.pro as ccxt
from collections import deque
import time

class LevelsTracker:
    def __init__(self, symbol='BTCUSDT', lookback_hours=24):
        self.symbol = symbol
        self.lookback_seconds = lookback_hours * 3600
        self.exchange = ccxt.bybit({'options': {'defaultType': 'linear'}})
        self.prices = deque()  # (timestamp, price) pairs
        self.high_24h = 0
        self.low_24h = float('inf')
        self.last_swing_high = 0
        self.last_swing_low = float('inf')
        
    async def start(self):
        """Start tracking price levels"""
        # Initialize with current market data
        await self._initialize_levels()
        
    async def _initialize_levels(self):
        """Fetch initial 24h high/low from exchange"""
        try:
            ticker = await self.exchange.fetch_ticker(self.symbol)
            self.high_24h = ticker.get('high', 0)
            self.low_24h = ticker.get('low', float('inf'))
        except Exception as e:
            print(f"Levels Init Error: {e}")
    
    def update_price(self, price):
        """Update current price and track 24h levels"""
        timestamp = time.time()
        self.prices.append((timestamp, price))
        
        # Remove prices older than 24h
        cutoff = timestamp - self.lookback_seconds
        while self.prices and self.prices[0][0] < cutoff:
            self.prices.popleft()
            
        # Update rolling 24h high/low
        if self.prices:
            all_prices = [p for _, p in self.prices]
            self.high_24h = max(all_prices)
            self.low_24h = min(all_prices)
            
        # Track recent swing points (for SFP detection)
        if price > self.last_swing_high:
            self.last_swing_high = price
        if price < self.last_swing_low:
            self.last_swing_low = price
    
    def check_liquidity_zone(self, price, tolerance=0.001):
        """
        Check if price is near a liquidity zone (24h high/low)
        Returns: 'high', 'low', or None
        """
        if abs(price - self.high_24h) / self.high_24h <= tolerance:
            return 'high'
        elif abs(price - self.low_24h) / self.low_24h <= tolerance:
            return 'low'
        return None
    
    def detect_sfp(self, price, side):
        """
        Detect Swing Failure Pattern
        - Price breaks above/below 24h high/low
        - Then quickly reverses (indicating stop hunt)
        """
        if side == 'high':
            # Price broke above 24h high but is now rejecting
            return price > self.high_24h and price < self.last_swing_high
        elif side == 'low':
            # Price broke below 24h low but is now rejecting  
            return price < self.low_24h and price > self.last_swing_low
        return False
    
    def get_levels_summary(self):
        """Return current levels info"""
        return {
            'high_24h': self.high_24h,
            'low_24h': self.low_24h,
            'current_swing_high': self.last_swing_high,
            'current_swing_low': self.last_swing_low
        }
    
    async def close(self):
        await self.exchange.close()
