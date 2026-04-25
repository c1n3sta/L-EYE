import asyncio
from data_stream import DataStream
from processor import AnalyticsProcessor
from levels import LevelsTracker
from colorama import Fore, init

init(autoreset=True)

async def run_l_eye():
    symbol = 'BTCUSDT'
    stream = DataStream(symbol)
    processor = AnalyticsProcessor(absorption_threshold=1000000)
    tracker = LevelsTracker(symbol)
    
    # Сразу подгружаем уровни
    levels = tracker.fetch_levels()
    print(f"{Fore.YELLOW}Target Levels: High {levels['high']} | Low {levels['low']}")

    try:
        while True:
            delta, price = await stream.fetch_trades()
            oi = await stream.fetch_oi()
            
            # Раз в 10 минут можно обновлять уровни (упрощенно)
            # Для MVP пока оставим текущие
            
            res = processor.analyze(price, delta, oi, levels)

            color = Fore.WHITE
            if res['in_zone']: color = Fore.CYAN  # Синим, если мы в зоне охоты
            if "HUNTING" in res['signal']: color = Fore.MAGENTA # Жирный сигнал

            print(f"{color}Price: {price} | Delta: {delta:>9,.0f} | OI Chg: {res['oi_change']:>8,.2f} | {res['signal']}")

    except Exception as e:
        print(f"Engine Error: {e}")
    finally:
        await stream.close()

if __name__ == "__main__":
    asyncio.run(run_l_eye())
