import asyncio
import get_public_data
import coinone_01
import vars
import datetime
import time
import db
import calendar

start=round(datetime.datetime(2021, 9, 28, 0, 0, 0, 0).timestamp()*1000)
end=round(datetime.datetime(2021, 9, 28, 23, 59, 59, 0).timestamp()*1000)
now = int(round(time.time() * 1000))





async def datetime_to_timestamp(y,m,d,hh=0,mm=0,ss=0,mmmmmm=0): #UTC기준
  timestamp=round(datetime.datetime(y, m, d, hh, mm, ss, mmmmmm).timestamp()*1000)
  return timestamp

async def timestamp_to_datetime(timestamp):
  ts_series=timestamp.apply(lambda x: datetime.fromtimestamp(x/1000))
  return ts_series

async def main():
  #db connection
  cal = calendar.Calendar()
  c = await db.db_connect() #db connect
  # btc_year = [2014,2015,2016,2017,2018,2019,2020]
  btc_month= [10]
  # for year in btc_year:
  year=2018
  for month in btc_month:
      for dt in cal.itermonthdays4(year, month):
        df_candles=await get_public_data.log_historical_candles(
            await datetime_to_timestamp(dt[0],dt[1],dt[2],0,0,0),
            await datetime_to_timestamp(dt[0],dt[1],dt[2],23,50,0),
            '1000',
            vars.OUTPUT_FILE_NAME,
            'tBTCUSD',
            '30m'
            )
        await db.historical_candle_db_save(c,df_candles)
    # df_historical=await db.historical_candle_db_load(c)
  #close database
  c.commit()
  c.close() 
    
  
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())