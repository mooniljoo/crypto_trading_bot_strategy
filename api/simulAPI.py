
from api.bitmexWS import generate_nonce
import pandas as pd


class SimulAPI:
    def __init__(self, db_engine, period=20) -> None:
        self.__name__ = 'SimulAPI'
        print(f"{self.__class__.__name__} has just started!")
        # init instance
        self.db_engine = db_engine
        print(f"{self.__class__.__name__} got {self.db_engine}")
        # init varibles
        self.marketPrice = 0
        self.count = 0
        self.data = {}
        # partial
        if not 'instruement' in self.data:
            self.data['instrument'] = []
        if not 'trade' in self.data:
            self.data['trade'] = []
        if not 'position' in self.data:
            self.data['position'] = []
        if not 'margin' in self.data:
            self.data['margin'] = []

        # init constants
        self.data['position'].append({'avgEntryPrice': 0, 'currentQty': 0, })
        self.data['margin'].append(
            {'availableMargin': 999999})

        self.df_ohlcv = pd.read_sql(
            f"select top ({period}) * from TBL_BITMEX_OHLCV order by timestamp desc", self.db_engine)
        print(self.df_ohlcv)

        # dataframe to self.data
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

        # print
        for item in self.data['instrument']:
            print(f"{item}")

    def get_marketPrice(self) -> float:
        '''return Current Market Price'''
        print(self.count)
        if self.count < len(self.df_ohlcv.index):
            self.count += 1
            marketPrice = self.data['instrument'][-self.count]['marketPrice']
            self.marketPrice = marketPrice
            return marketPrice
        else:
            return 0

    def buy(self, price: float = None, orderQty: int = 10) -> dict:
        '''return Buy Order'''
        marketPrice = self.get_marketPrice()
        price = marketPrice if price == None else price

        self.availableMargin = self.data['margin'][0]['availableMargin']
        order = {
            "side": "Buy",
            "orderID": generate_nonce(),
            "price": price,
            "orderQty": orderQty,
        }

        if self.availableMargin - price >= 0:
            self.data['trade'].append(order)

            self.data['margin'][0]['availableMargin'] = self.availableMargin - price
            self.data['position'][0]['avgEntryPrice'] = self.get_avgEntryPrice()
            self.data['position'][0]['currentQty'] += orderQty

            print(f"{self.__class__.__name__}가 {price}USD를 {orderQty}만큼 매수했습니다.")
            print(f"successful : {order}")
            return order
        else:
            print(f"{self.__class__.__name__}가 잔고가 부족해 매수하지 못했습니다.")
            print(f"failed : {order}")

    def sell(self, price: float = None, orderQty: int = 10) -> dict:
        '''return Buy Order'''
        marketPrice = self.get_marketPrice()
        price = marketPrice if price == None else price

        self.avgEntryPrice = self.data['position'][0]['avgEntryPrice']
        self.currentQty = self.data['position'][0]['currentQty']

        order = {
            "side": "Sell",
            "orderID": generate_nonce(),
            "price": price,
            "orderQty": orderQty,
            "timestamp": self.data['instrument'][-self.count]['timestamp']
        }

        if (self.avgEntryPrice * self.currentQty) - (price * orderQty) >= 0:
            self.data['trade'].append(order)

            self.data['margin'][0]['availableMargin'] += price
            self.data['position'][0]['avgEntryPrice'] = self.get_avgEntryPrice()
            self.data['position'][0]['currentQty'] -= orderQty

            print(f"{self.__class__.__name__}가 {price}USD를 {orderQty}만큼 매도했습니다.")
            print(f"successful : {order}")
            return order
        else:
            print(f"{self.__class__.__name__}가 코인잔고가 부족해 매도하지 못했습니다.")
            print(f"failed : {order}")

    def get_avgEntryPrice(self) -> float:
        '''return avgEntryPrice'''
        avgEntryPrice = 0
        total = 0
        totalQty = 0
        for trade in self.data['trade']:
            if 'Buy' in trade['side']:
                total += trade['price'] * trade['orderQty']
                totalQty += trade['orderQty']

            if 'Sell' in trade['side']:
                total -= trade['price'] * trade['orderQty']
                totalQty -= trade['orderQty']

        if total and totalQty:
            avgEntryPrice = total / totalQty
        else:
            avgEntryPrice = 0
        return avgEntryPrice

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
