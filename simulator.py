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

    def __init__(self) -> None:
        self.__name__ = 'Simulator'
        self.api = SimulAPI
        self.db_engine = DBengine.engine
        self.strategy = Strategy(self.api)
        self.runningState = True

    def run(self, period: int = 20) -> str:
        '''Return strategy after simulation with period'''
        index = 0
        resultStrategy = ""
        # for strategy in self.strategy.strategyList:
        #     print(eval(f"self.strategy.{strategy}()"))

        resultStrategy = "volatility_breakout"

        # self.api(self.db_engine)
        df_ohlcv = pd.read_sql(
            f"select top ({period}) * from TBL_BITMEX_OHLCV order by timestamp desc", self.db_engine)

        for i in range(len(df_ohlcv.index)):
            print(df_ohlcv.iloc[i]['close'])
            sleep(1)

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
