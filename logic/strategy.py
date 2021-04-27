from indicator import Indicator


class Strategy:
    '''
    트레이딩에 사용될 전략
    -매수신호에서는 1을 반환
    -매도신호에서는 -1을 반환    
    '''

    def __init__(self, api) -> None:
        self.indicator = Indicator
        # self.api = api
        # self.data = self.api.data
        # self.marketPrice = self.data['trade'][-1]['price']
        self.strategyList = ['volatility_breakout', 'scailing']

    def volatility_breakout(self) -> float:
        return -1
        # volatilityBreakoutPrice = self.indicator.get_volatilityBreakoutPrice(
        #     self.data['trade'][-2]['price'], self.data['trade'][-2]['price'], self.data['trade'][-1]['price'])
        # if volatilityBreakoutPrice > self.marketPrice:
        #     return 1
        # if volatilityBreakoutPrice < self.marketPrice:
        #     return -1

    def scailing(self) -> float:
        return 1
