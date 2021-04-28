from logic.strategy import Strategy
from api.bitmexAPI import BitmexAPI
from api.simulAPI import SimulAPI
from simulator import Simulator
from util.db_engine import DBengine

from time import sleep
import pandas as pd
import sys

from config import config


class Main:
    '''
    Main App
    '''

    def __init__(self) -> None:
        self.runningState = True
        # self.bitmexapi = BitmexAPI(config.BASE_URL, config.SYMBOL, config.API_KEY,
        #                            config.SECRET_KEY, ["tradeBin1m", "quoteBin1m"])
        # self.ws = self.bitmexapi.ws
        self.db_engine = DBengine.engine
        self.simulator = Simulator(self.db_engine)

    def run(self) -> None:
        '''Run the Trader'''
        while self.runningState:
            # 콜렉터는 쓰레드로 항시 실행
            사전데이터가없나 = False
            if 사전데이터가없나:
                # 콜렉터부터 실행
                pass
            else:
                strategy = self.simulator.run()
                print(f"STRATEGY NUMBER : {strategy}")
                break
            # self.runCollector(self.runningState)
            # if self.simulapi.data:
            #     strategy = self.simulator.run()
            #     print(strategy)
            # else:
            #     print("collector 후에 다시 실행")

            sleep(.5)

    def stopRunning(self) -> None:
        '''Stop the Trader.'''
        self.runningState = False

    def runCollector(self, runningState) -> None:
        from collector import Collector
        collector = Collector(self.ws, self.db_engine.engine)
        collector.run(runningState)

    def _exit(self) -> None:
        sys.exit(0)


if __name__ == "__main__":
    main = Main()
    main.run()
