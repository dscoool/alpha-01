import asyncio
import get_public_data
import coinone_01
import vars
import datetime
import time
import vortex
import db
import calendar
import signal
from pandas import Series, DataFrame

async def datetime_to_timestamp(y,m,d,hh=0,mm=0,ss=0,mmmmmm=0): #UTC기준
  timestamp=round(datetime.datetime(y, m, d, hh, mm, ss, mmmmmm).timestamp()*1000)
  return timestamp

async def timestamp_to_datetime(timestamp):
  ts_series=timestamp.apply(lambda x: datetime.fromtimestamp(x/1000))
  return ts_series

async def main():
  #db connection
    cal = calendar.Calendar()
    c = await db.db_connect() 
#   df_historical=await db.historical_candle_db_load()
#   print(df_historical)
#   df_vortex=await vortex.calc_VI(df_historical)
#   await db.vi_db_save(c,df_vortex)
    df_v = await db.vi_db_load(c)
    
    df_s = await signal.calc_signal(df_v)
  
#   print(df_vortex)
  #calculate VI index

  #db connect
  # btc_year = [2014,2015,2016,2017,2018,2019,2020]
#   btc_month= [6,5,4,3,2,1]
#   # for year in btc_year:
#   year=2015
#   for month in btc_month:
#     for dt in cal.itermonthdays4(year, month):
#         df_candles=await get_public_data.log_historical_candles(
#             await datetime_to_timestamp(dt[0],dt[1],dt[2],0,0,0),
#             await datetime_to_timestamp(dt[0],dt[1],dt[2],23,50,0),
#             '10000',
#             vars.OUTPUT_FILE_NAME,
#             'tBTCUSD',
#             '30m'
#             )
#         await db.historical_candle_db_save(c,df_candles)
#         del(df_candles)
#     time.sleep(10)
  #close database
  c.commit()
  c.close() 
    
  
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())