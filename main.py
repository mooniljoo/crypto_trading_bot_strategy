from logic.strategy import Strategy
from api.bitmexAPI import BitmexAPI
from api.simulAPI import SimulAPI
from simulator import Simulator
from util.db_engine import DBengine
from config import settings

from time import sleep
import pandas as pd
import sys

from config import config


class Main:
    '''
    Main App
    '''

    def __init__(self) -> None:
        # init variables
        self.runningState = True
        # init instance
        self.bitmexapi = BitmexAPI(config.BASE_URL, config.SYMBOL, config.API_KEY,
                                   config.SECRET_KEY, ["trade", "tradeBin1m", "quoteBin1m"])
        self.ws = self.bitmexapi.ws
        self.db_engine = DBengine.engine
        self.simulator = Simulator(self.db_engine)
        # first func
        self.runCollector(self.ws, self.db_engine)

    def run(self) -> None:
        '''Run the Trader'''
        while self.runningState:
            # 콜렉터는 쓰레드로 항시 실행

            while self.get_ohlcv_from_db(self.db_engine).empty:
                print("백테스팅에 활용할 데이터가 데이터베이스에 입력되기를 기다립니다")
                sleep(settings.WATING_FOR_DB_DURATION)

            # period의 행으로 백테스팅 후 사용할 전략 반환
            strategy = self.simulator.run(10)
            print(f"STRATEGY NUMBER : {strategy}")
            break
            sleep(0.5)

    def get_ohlcv_from_db(self, db_engine) -> None:
        df = pd.read_sql(
            f"select * from TBL_BITMEX_OHLCV order by timestamp desc", db_engine)
        return df

    def stopRunning(self) -> None:
        '''Stop the Trader.'''
        self.runningState = False

    def runCollector(self, ws, db_engine) -> None:
        from collector import Collector
        collectorThread = Collector(ws, db_engine)
        collectorThread.daemon = True
        collectorThread.start()

    def _exit(self) -> None:
        sys.exit(0)


if __name__ == "__main__":
    main = Main()
    main.run()
