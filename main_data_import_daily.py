import asyncio
import get_public_data
import coinone_01
import vars
import datetime
import time
import db
import calendar


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
  # #2013까지 완료
#   btc_month= [2,3,4,5,6,7,8,9,10,11,12]
    year=[2021]
    for y in year:
        df_candles=await get_public_data.log_historical_candles(
            await datetime_to_timestamp(y,1,1,0,0,0),
            await datetime_to_timestamp(y,10,5,0,0,0),
            '10000',
            vars.OUTPUT_FILE_NAME,
            'tBTCUSD',
            '1D'
        )
        await db.historical_candle_daily_db_save(c,df_candles)
        time.sleep(5)
        del(df_candles)
    c.commit()
    c.close() 
    
  
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())