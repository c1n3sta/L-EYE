import asyncio
import ccxt.pro as ccxt

class DataStream:
    def __init__(self, symbol='BTCUSDT'):
        self.symbol = symbol
        # Настройка Bybit для работы с бессрочными фьючерсами
        self.exchange = ccxt.bybit({'options': {'defaultType': 'linear'}})

    async def fetch_trades(self):
        """Стрим рыночных сделок (для расчета Дельты)"""
        while True:
            try:
                trades = await self.exchange.watch_trades(self.symbol)
                # Группируем сделки по направлению
                delta = 0
                for t in trades:
                    cost = t['amount'] * t['price']
                    delta += cost if t['side'] == 'buy' else -cost
                return delta, trades[-1]['price']
            except Exception as e:
                print(f"Stream Error (Trades): {e}")
                await asyncio.sleep(1)

    async def fetch_oi(self):
        """Стрим открытого интереса через тикер"""
        while True:
            try:
                ticker = await self.exchange.watch_ticker(self.symbol)
                # Извлекаем OI из сырых данных биржи
                oi = float(ticker['info']['openInterest'])
                return oi
            except Exception as e:
                print(f"Stream Error (OI): {e}")
                await asyncio.sleep(1)

    async def close(self):
        await self.exchange.close()
