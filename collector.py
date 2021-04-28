from time import sleep
import pandas as pd

import dateutil.parser
import pytz
import datetime


class Collector:
    def __init__(self, ws, db_engine) -> None:
        print(f"{self.__class__.__name__} has just started!")
        self.ws = ws
        self.db_engine = db_engine

    def run(self, runningState) -> None:
        while runningState:
            print(f"...{self.__class__.__name__} is running...")
            # if 'trade' in ws.data:
            #     _list = change_dictItems_in_list(ws.data['trade'], 'timestamp')
            #     df = pd.DataFrame(_list)
            #     df.to_sql('TBL_BITMEX_OHLCV', db_engine, if_exists="replace")
            #     print("추가\n", df)

            if 'tradeBin1m' in self.ws.data:
                _list = self.change_dictItems_in_list(
                    self.ws.data['tradeBin1m'], 'timestamp')
                df = pd.DataFrame(_list)
                df.to_sql('TBL_BITMEX_OHLCV', self.db_engine,
                          if_exists="replace")
                print("추가\n", df)
            else:
                print(f"{self.__class__.__name__}가 담을 'tradeBin1m'이 없습니다.")
                break

            if 'quoteBin1m' in self.ws.data:
                _list = self.change_dictItems_in_list(
                    self.ws.data['quoteBin1m'], 'timestamp')
                df = pd.DataFrame(_list)
                df.to_sql('TBL_BITMEX_QUOTE', self.db_engine,
                          if_exists="replace")
                print("추가\n", df)
            else:
                print(f"{self.__class__.__name__}가 담을 'quoteBin1m'이 없습니다.")
                break

            sleep(1)
        print(f"{self.__class__.__name__} has just finished!")

    def rfc_to_int(self, rfc, timeformat: str = "%Y%m%d%H%M%S", timezone: str = 'Asia/Seoul') -> int:

        date = dateutil.parser.parse(rfc)
        local_timezone = pytz.timezone(timezone)
        local_date = date.replace(tzinfo=pytz.utc).astimezone(local_timezone)
        return int(datetime.datetime.strftime(local_date, timeformat))

    def change_dictItems_in_list(self, _list: list, itemName: str) -> list:
        for item in _list:
            if type(item[itemName]).__name__ == 'str':
                item[itemName] = self.rfc_to_int(item[itemName])
        return _list
