import sqlite3
import pandas as pd
import traceback
import sys

async def db_connect():
    con = sqlite3.connect("./db/alpha_01.db")
    # type(con)
    sqlite3.Connection
    print("DB connected : alpha_01.db")
    return con

async def historical_candle_db_save(c, df):
    # print(df)
    for r in df.iterrows():

        t=(r[1][0],r[1][1],r[1][2],r[1][3],r[1][4],r[1][5],str(r[1][6]))
        print(t)
        try:
            c.executemany("INSERT INTO HISTORICAL_CANDLES VALUES(?,?,?,?,?,?,?)", (t,))
            print("written to db:",t)
        except sqlite3.Error as er:
            print('SQLite error: %s' % (' '.join(er.args)))
            print("Exception class is: ", er.__class__)
            print('SQLite traceback: ')
            exc_type, exc_value, exc_tb = sys.exc_info()
            print(traceback.format_exception(exc_type, exc_value, exc_tb))
       

async def historical_candle_db_load():
    # f = (etfcode,modify_date)
    col_historical_candle = ['MTS','DATETIME','OPEN','CLOSE','HIGH','LOW','VOLUME']

    conn = sqlite3.connect("./db/alpha_01.db") 
    cur = conn.cursor() 
    cur.execute("SELECT MTS, DATETIME, OPEN, CLOSE, HIGH, LOW, VOLUME FROM HISTORICAL_CANDLES ORDER BY MTS ASC") 
    rows = cur.fetchall() 
    df_hc=pd.DataFrame(rows, columns=col_historical_candle)
    conn.close()
        
    return df_hc

async def vi_db_save(c, df):
    # print(df)
    for r in df.iterrows():
        t=(r[1][0],r[1][1],r[1][2],r[1][3],r[1][4],r[1][5],str(r[1][6]),r[1][7],r[1][8],r[1][9])
        print(t)
        try:
            c.executemany("INSERT INTO VI VALUES(?,?,?,?,?,?,?,?,?,?)", (t,))
            print("written to \'VI\' db:",t)
        except sqlite3.Error as er:
            print('SQLite error: %s' % (' '.join(er.args)))
            print("Exception class is: ", er.__class__)
            print('SQLite traceback: ')
            exc_type, exc_value, exc_tb = sys.exc_info()
            print(traceback.format_exception(exc_type, exc_value, exc_tb))
        

async def vi_db_load(c):
    # f = (etfcode,modify_date)
    col_historical_candle = ['MTS','DATETIME','OPEN','CLOSE','HIGH','LOW','VOLUME','VI_DIFF','VI_POS','VI_NEG']

    conn = sqlite3.connect("./db/alpha_01.db") 
    cur = conn.cursor() 
    cur.execute("SELECT MTS, DATETIME, OPEN, CLOSE, HIGH, LOW, VOLUME, VI_DIFF, VI_POS, VI_NEG FROM VI ORDER BY MTS ASC") 
    rows = cur.fetchall() 
    df=pd.DataFrame(rows, columns=col_historical_candle)
    conn.close() 
        
    return df


async def historical_candle_daily_db_save(c, df):
    # print(df)
    for r in df.iterrows():

        t=(r[1][0],r[1][1],r[1][2],r[1][3],r[1][4],r[1][5],str(r[1][6]))
        print(t)
        try:
            c.executemany("INSERT INTO HISTORICAL_CANDLES_DAILY VALUES(?,?,?,?,?,?,?)", (t,))
            print("written to db:",t)

        # except:
        except sqlite3.Error as er:
            print('SQLite error: %s' % (' '.join(er.args)))
            print("Exception class is: ", er.__class__)
            print('SQLite traceback: ')
            exc_type, exc_value, exc_tb = sys.exc_info()
            print(traceback.format_exception(exc_type, exc_value, exc_tb))
            # print('db writing error')



async def historical_candle_daily_db_load():
    # f = (etfcode,modify_date)
    col_historical_candle = ['MTS','DATETIME','OPEN','CLOSE','HIGH','LOW','VOLUME']

    conn = sqlite3.connect("./db/alpha_01.db") 
    cur = conn.cursor() 
    cur.execute("SELECT MTS, DATETIME, OPEN, CLOSE, HIGH, LOW, VOLUME FROM HISTORICAL_CANDLES_DAILY ORDER BY MTS ASC") 
    rows = cur.fetchall() 
    df_hcd=pd.DataFrame(rows, columns=col_historical_candle)
    conn.close()
        
    return df_hcd
