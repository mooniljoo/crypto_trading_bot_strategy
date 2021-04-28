from numpy.core.numeric import indices
from indicator import Indicator


class Strategy:
    '''
    트레이딩에 사용될 전략
    -매수신호에서는 1을 반환
    -매도신호에서는 -1을 반환    
    '''

    def __init__(self, api):
        self.api = api

    def run(self, strategyIndex: int) -> str:
        '''
        미리 설정해둔 전략으로 매수매도 타이밍 반환
        매수시 "buy"반환, 매도시 "sell" 반환
        설정해둔 전략이 없을시 None 반환
        strategyIndex == 1: 변동성돌파
        strategyIndex == 2: 물타기
        '''
        if self.api == None:
            raise("api is None")

        if strategyIndex == 1:
            '''변동성돌파전략'''
            # volatilityBreakoutPrice = Indicator.get_volatilityBreakoutPrice()
            volatilityBreakoutPrice = 54570

            if self.api.marketPrice > volatilityBreakoutPrice:
                return "buy"
            if self.api.marketPrice < volatilityBreakoutPrice:
                return "sell"

        elif strategyIndex == 2:
            '''물타기전략'''
            pass
        else:
            print(f"일치하는 매매기법을 찾지 못했습니다.")
            return None
    # def __init__(self, api, strategyIndex) -> None:
    #     self.indicator = Indicator
    #     # self.api = api
    #     # self.data = self.api.data
    #     # self.marketPrice = self.data['trade'][-1]['price']
    #     self.strategyList = ['volatility_breakout', 'scailing']

    #     self.
    #     # volatilityBreakoutPrice = self.indicator.get_volatilityBreakoutPrice(
    #     #     self.data['trade'][-2]['price'], self.data['trade'][-2]['price'], self.data['trade'][-1]['price'])
    #     # if volatilityBreakoutPrice > self.marketPrice:
    #     #     return 1
    #     # if volatilityBreakoutPrice < self.marketPrice:
    #     #     return -1

    # def scailing(self) -> float:
    #     return 1
