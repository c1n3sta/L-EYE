class AnalyticsProcessor:
    def __init__(self, absorption_threshold=1000000):
        self.absorption_threshold = absorption_threshold
        self.prev_oi = None
        self.cvd = 0

    def analyze(self, price, delta, oi, liq_zone=None, sfp_detected=False):
        """
        Входящие данные: текущая цена, дельта пачки сделок, открытый интерес.
        Логика: выявление неэффективности (Effort vs Result) + анализ зон ликвидности.
        """
        self.cvd += delta
        oi_change = oi - self.prev_oi if self.prev_oi is not None else 0
        self.prev_oi = oi

        # 1. Детектор "Захлеба" (Absorption)
        # Если дельта > порога, а цена сдвинулась менее чем на 0.01%
        price_efficiency = abs(delta) / (price if price != 0 else 1)
        
        is_absorption = abs(delta) > self.absorption_threshold and price_efficiency < 0.1

        # 2. Определение "Качества" движения
        # OI растет + Delta растет = Кит строит позицию
        # OI падает + Delta растет = Толпа закрывает шорты (Short Cover)
        is_smart_money = oi_change > 0
        
        # 3. Усиление сигнала в зоне ликвидности
        # SFP + Absorption + Smart Money = HIGHEST PROBABILITY SETUP
        signal_strength = 0
        if is_absorption:
            signal_strength += 1
        if is_smart_money:
            signal_strength += 1
        if liq_zone:
            signal_strength += 1
        if sfp_detected:
            signal_strength += 1
        
        # Определяем финальный сигнал
        if signal_strength >= 3:
            signal = "🔥 HUNTING (HIGH CONF)"
        elif signal_strength == 2:
            signal = "⚡ POTENTIAL SETUP"
        elif is_absorption and liq_zone:
            signal = "👁️  LIQ ABSORPTION"
        elif sfp_detected:
            signal = "🎯 SFP DETECTED"
        else:
            signal = "NORMAL"

        return {
            "cvd": self.cvd,
            "oi_change": oi_change,
            "is_absorption": is_absorption,
            "is_smart_money": is_smart_money,
            "liq_zone": liq_zone,
            "sfp_detected": sfp_detected,
            "signal": signal,
            "signal_strength": signal_strength
        }
