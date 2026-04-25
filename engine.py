import asyncio
from data_stream import DataStream
from processor import AnalyticsProcessor
from levels import LevelsTracker
from colorama import Fore, init

init(autoreset=True)

async def run_l_eye():
    symbol = 'BTCUSDT'
    stream = DataStream(symbol)
    levels = LevelsTracker(symbol)
    # Порог абсорбции: $1,000,000 в одной пачке сделок
    processor = AnalyticsProcessor(absorption_threshold=1000000)

    print(f"{Fore.CYAN}L-EYE ENGINE STARTED | MONITORING {symbol}")
    print(f"{Fore.CYAN}Strategy: Shark Remora - Hunting Liquidation Zones")
    print("-" * 60)

    # Initialize levels tracker
    await levels.start()

    try:
        while True:
            # Получаем данные из стрима параллельно
            # Мы используем gather, чтобы задержка одного потока не тормозила другой
            delta_task = stream.fetch_trades()
            oi_task = stream.fetch_oi()
            
            delta, price = await delta_task
            oi = await oi_task

            # Обновляем уровни ликвидности
            levels.update_price(price)
            
            # Проверяем зону ликвидности и SFP
            liq_zone = levels.check_liquidity_zone(price)
            sfp_detected = False
            if liq_zone:
                sfp_detected = levels.detect_sfp(price, liq_zone)

            # Передаем данные в процессор с учетом уровней
            results = processor.analyze(price, delta, oi, liq_zone, sfp_detected)

            # Формируем вывод с учетом всех сигналов
            color = Fore.WHITE
            signal_parts = []
            
            if results['is_absorption']:
                color = Fore.GREEN if delta > 0 else Fore.RED
                signal_parts.append("ABSORPTION")
            
            if liq_zone:
                signal_parts.append(f"LIQ_{liq_zone.upper()}")
                color = Fore.YELLOW
            
            if sfp_detected:
                signal_parts.append("SFP")
                color = Fore.MAGENTA
            
            if results['is_smart_money']:
                signal_parts.append("SMART_MONEY")
            
            final_signal = " | ".join(signal_parts) if signal_parts else "NORMAL"

            levels_info = levels.get_levels_summary()
            msg = (
                f"{color}Price: {price:<10} | "
                f"Delta: {delta:>12,.0f}$ | "
                f"OI Change: {results['oi_change']:>10,.0f} | "
                f"24H H/L: {levels_info['high_24h']:,.0f}/{levels_info['low_24h']:,.0f} | "
                f"SIGNAL: {final_signal}"
            )
            print(msg)

    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Stopping L-EYE...")
    finally:
        await stream.close()
        await levels.close()

if __name__ == "__main__":
    asyncio.run(run_l_eye())
