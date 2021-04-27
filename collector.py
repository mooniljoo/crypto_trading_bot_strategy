
from util.db_engine import DBengine


from time import sleep
import pandas as pd

import dateutil.parser
import pytz
import datetime

db_engine = DBengine.engine


def rfc_to_int(rfc, timeformat: str = "%Y%m%d%H%M%S", timezone: str = 'Asia/Seoul') -> int:

    date = dateutil.parser.parse(rfc)
    local_timezone = pytz.timezone(timezone)
    local_date = date.replace(tzinfo=pytz.utc).astimezone(local_timezone)
    return int(datetime.datetime.strftime(local_date, timeformat))


def change_dictItems_in_list(_list: list, itemName: str) -> list:
    for item in _list:
        if type(item[itemName]).__name__ == 'str':
            item[itemName] = rfc_to_int(item[itemName])
    return _list


if __name__ == "__main__":
    from config import config
    from api.bitmexWS import BitmexWebsocket
    ws = BitmexWebsocket(config.BASE_URL, config.SYMBOL, config.API_KEY,
                         config.SECRET_KEY, ["tradeBin1m", "quoteBin1m"])
    # tradeBin1m
    # tradeBin5m
    # tradeBin1h
    # tradeBin1d
    while 1:
        print('...running...')
        # if 'trade' in ws.data:
        #     _list = change_dictItems_in_list(ws.data['trade'], 'timestamp')
        #     df = pd.DataFrame(_list)
        #     df.to_sql('TBL_BITMEX_OHLCV', db_engine, if_exists="replace")
        #     print("추가\n", df)

        if 'tradeBin1m' in ws.data:
            _list = change_dictItems_in_list(
                ws.data['tradeBin1m'], 'timestamp')
            df = pd.DataFrame(_list)
            df.to_sql('TBL_BITMEX_OHLCV', db_engine, if_exists="replace")
            print("추가\n", df)

        if 'quoteBin1m' in ws.data:
            _list = change_dictItems_in_list(
                ws.data['quoteBin1m'], 'timestamp')
            df = pd.DataFrame(_list)
            df.to_sql('TBL_BITMEX_QUOTE', db_engine, if_exists="replace")
            print("추가\n", df)

        sleep(1)
