
from api.bitmexWS import generate_nonce
import pandas as pd


class SimulAPI:
    def __init__(self, db_engine, period=20) -> None:
        self.__name__ = 'SimulAPI'
        self.db_engine = db_engine
        print(self.db_engine)
        self.marketPrice = 0
        self.count = 0
        self.data = {}

        self.df_ohlcv = pd.read_sql(
            f"select top ({period}) * from TBL_BITMEX_OHLCV order by timestamp desc", self.db_engine)

        if not 'instruement' in self.data:
            self.data['instrument'] = []
        if not 'trade' in self.data:
            self.data['trade'] = []

        if not self.df_ohlcv.empty:
            for i in range(len(self.df_ohlcv.index)):
                self.data['instrument'].append({
                    "timestamp": self.df_ohlcv.iloc[i]['timestamp'],
                    "open": self.df_ohlcv.iloc[i]['open'],
                    "high": self.df_ohlcv.iloc[i]['high'],
                    "low": self.df_ohlcv.iloc[i]['low'],
                    "trades": self.df_ohlcv.iloc[i]['trades'],
                    "marketPrice": self.df_ohlcv.iloc[i]['close'],
                    "volume": self.df_ohlcv.iloc[i]['volume'],
                    "lastSize": self.df_ohlcv.iloc[i]['lastSize'],
                })

    def get_marketPrice(self) -> float:
        print(self.count)
        if self.count < len(self.df_ohlcv.index):
            self.count += 1
            marketPrice = self.df_ohlcv.iloc[-self.count]['close']
            self.marketPrice = marketPrice
            return marketPrice
        else:
            return 0

    def buy(self, price: float = None, orderQty: int = 10):
        price = self.marketPrice if price == None else price

        order = {
            "side": "Buy",
            "orderID": generate_nonce(),
            "price": price,
            "orderQty": orderQty,
        }
        self.data['trade'].append(order)
        print(f"{self.__class__.__name__}가 {price}USD를 {orderQty}만큼 매수했습니다.")
        print(self.data['trade'])

    def sell(self, price: float = None, orderQty: int = 10):
        price = self.marketPrice if price == None else price
        order = {
            "side": "Sell",
            "orderID": generate_nonce(),
            "price": price,
            "orderQty": orderQty,
        }
        self.data['trade'].append(order)
        print(f"{self.__class__.__name__}가 {price}USD를 {orderQty}만큼 매도했습니다.")
        print(self.data['trade'])

    def get_earningRate(self):
        pass


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
