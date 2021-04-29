from logic.strategy import Strategy
from api.simulAPI import SimulAPI
from util.db_engine import DBengine
from config import settings

from time import sleep
import pandas as pd


class Simulator:
    '''
    제일 높은 수익률의 Strategy 반환
    DB데이터와 indicator(보조지표)로 시뮬레이팅
    '''

    def __init__(self, db_engine) -> None:
        self.__name__ = 'Simulator'
        print(f"{self.__class__.__name__} has just started!")
        self.db_engine = db_engine
        self.runningState = True
        self.strategyNumList = [0, 1]

    def run(self, period: int = 10) -> str:
        '''Return strategy after simulation with period'''
        print(f"...{self.__class__.__name__} is running...")
        while self.runningState:
            simulResultList = []
            simulNum = 0
            for strategyNum in self.strategyNumList:
                # intialize api, strategy
                simulapi = SimulAPI(self.db_engine, period)
                strategy = Strategy(simulapi)
                print(f"A Strategy Simulation has just started!!")
                # simulation
                for i in range(len(simulapi.data['instrument'])):
                    print(i)
                    if "buy" == strategy.run(strategyNum):
                        simulapi.buy()
                    elif "sell" == strategy.run(strategyNum):
                        simulapi.sell()
                    print(
                        f"margin : {simulapi.data['margin'][0]['availableMargin']}")
                    print(
                        f"avgEntryPrice : {simulapi.data['position'][0]['avgEntryPrice']} x {simulapi.data['position'][0]['currentQty']}")
                    sleep(settings.SIMULATION_SPEED)
                print(f"A Strategy Simulation has just finished!!\n\n")

                # result simulation
                simulResultList.append(
                    simulapi.data['margin'][0]['availableMargin'])
                simulNum += 1
            print(simulResultList)
            resultStrategy = simulResultList.index(max(simulResultList))
            return resultStrategy

        # for strategy in self.strategy.strategyList:
        #     print(eval(f"self.strategy.{strategy}()"))

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


    def stopRunning(self) -> None:
        '''Stop the Simulator.'''
        self.runningState = False


if __name__ == "__main__":
    simulator = Simulator()
    simulator.run()
