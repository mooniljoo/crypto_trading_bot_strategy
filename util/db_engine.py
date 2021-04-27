
from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL
from sqlalchemy.orm import sessionmaker

from config import config


class DBengine:
    db_ip = config.db_ip
    db_id = config.db_id
    db_passwd = config.db_passwd
    db_name = config.db_name

    db_url = URL(
        drivername="mssql+pymssql",
        host=db_ip,
        # port=db_port,
        username=db_id,
        password=db_passwd,
        database=db_name
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
