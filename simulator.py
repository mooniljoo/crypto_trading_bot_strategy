from logic.strategy import Strategy
from api.simulAPI import SimulAPI
from util.db_engine import DBengine

from time import sleep
import pandas as pd


class Simulator:
    '''
    제일 높은 수익률의 Strategy 반환
    DB데이터와 indicator(보조지표)로 시뮬레이팅
    '''

    def __init__(self, db_engine, period: int = 20) -> None:
        self.__name__ = 'Simulator'
        self.period = period
        self.db_engine = db_engine
        self.runningState = True
        self.simulapi = SimulAPI(self.db_engine, period)

    def run(self) -> str:
        '''Return strategy after simulation with period'''
        strategy = Strategy(self.simulapi)
        while self.runningState:
            print(len(self.simulapi.data['instrument']))
            # for i in range(len(self.simulapi.data['instrument'])):
            #     print(i)
            #     if "buy" == strategy.run(1):
            #         self.simulapi.buy()
            #     elif "sell" == strategy.run(1):
            #         self.simulapi.sell()
            #     sleep(.5)
            self.simulapi.get_earningRate()
            break
            sleep(.5)

        resultStrategy = ""
        # for strategy in self.strategy.strategyList:
        #     print(eval(f"self.strategy.{strategy}()"))

        resultStrategy = "volatility_breakout"

        # df_ohlcv = pd.read_sql(
        #     f"select top ({period}) * from TBL_BITMEX_OHLCV order by timestamp desc", self.db_engine)

        # # simulating
        # self.api = SimulAPI(self.db_engine, period)
        # for i in range(len(df_ohlcv.index)):
        #     print(self.api.marketPrice)

        #     # print(df_ohlcv.iloc[i]['close'])

        #     if df_ohlcv.loc[i:].empty:
        #         break
        #     sleep(.5)

        # while self.runningState:
        #     if df_ohlcv.loc[index:].empty:
        #         self.stopRunning()

        #     index += 1
        #     sleep(0.5)

        return resultStrategy

    def stopRunning(self) -> None:
        '''Stop the Simulator.'''
        self.runningState = False


if __name__ == "__main__":
    simulator = Simulator()
    simulator.run()
