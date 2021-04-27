
from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL
from sqlalchemy.orm import sessionmaker

from config import config


class DBengine:
    db_url = URL(
        drivername="mssql+pymssql",
        host=config.db_ip,
        # port=db_port,
        username=config.db_id,
        password=config.db_passwd,
        database=config.db_name
    )
    try:
        engine = create_engine(db_url, echo=True)
    except Exception as e:
        print(e)


if __name__ == "__main__":

    print(DBengine.engine)
    import pandas as pd
    sql = '''
    select * from TBL_BITMEX_OHLCV ORDER BY timestamp DESC
    '''
    print(pd.read_sql(sql, DBengine.engine))
