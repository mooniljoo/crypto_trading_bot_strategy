class Indicator:
    def get_volatilityBreakoutPrice(lastPriceHigh: float, lastPriceLow: float, nowOpenPrice: float, k: float = 0.5) -> bool:
        now_open = nowOpenPrice
        lasttime_high = lastPriceHigh
        lasttime_low = lastPriceLow
        breakout_price = now_open + (lasttime_high - lasttime_low) * k
        return breakout_price
