
import pandas as pd


class SimulAPI:
    def __init__(self, db_engine, period) -> None:
        self.__name__ = 'SimulAPI'
        self.db_engine = db_engine
        print(self.db_engine)
        self.df_ohlcv = pd.read_sql(
            f"select top ({period}) * from TBL_BITMEX_OHLCV order by timestamp desc", self.db_engine)

        self.marketPrice = self.df_ohlcv.iloc[-1]['close']


if __name__ == "__main__":
    if __package__ is None:
        import sys
        from os import path
        print(path.dirname(path.dirname(path.abspath(__file__))))
        sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
        from util.db_engine import DBengine

    db_engine = DBengine
    simulapi = SimulAPI(db_engine, 10)
    print(simulapi.marketPrice)
