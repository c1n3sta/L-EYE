class AnalyticsProcessor:
    def __init__(self, absorption_threshold=1000000):
        self.absorption_threshold = absorption_threshold
        self.prev_oi = None
        self.cvd = 0

    def analyze(self, price, delta, oi, levels):
        self.cvd += delta
        oi_change = oi - self.prev_oi if self.prev_oi is not None else 0
        self.prev_oi = oi

        # Проверка близости к уровню (зона 0.2% от High/Low)
        in_zone = False
        if levels['high'] and levels['low']:
            near_high = abs(price - levels['high']) / price < 0.002
            near_low = abs(price - levels['low']) / price < 0.002
            in_zone = near_high or near_low

        # Детектор "Захлеба" (Effort vs Result)
        price_efficiency = abs(delta) / price if price != 0 else 1
        is_absorption = abs(delta) > self.absorption_threshold and price_efficiency < 0.05
        
        # Сигнал: Абсорбция + Вход свежих денег (OI растет) + Зона Ликвидности
        signal = "NORMAL"
        if is_absorption and oi_change > 0 and in_zone:
            signal = "⚠️ HUNTING (WHALE IN ZONE) ⚠️"

        return {
            "cvd": self.cvd,
            "oi_change": oi_change,
            "signal": signal,
            "in_zone": in_zone
        }
