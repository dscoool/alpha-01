from __future__ import (absolute_import, division, print_function, unicode_literals)
import datetime
import asyncio
import get_public_data
import coinone_01
import vars
import pandas as pd
import time
import db
import backtrader as bt
import strategy
import argparse

async def datetime_to_timestamp(y,m,d,hh=0,mm=0,ss=0,mmmmmm=0): #UTC기준
  timestamp=round(datetime.datetime(y, m, d, hh, mm, ss, mmmmmm).timestamp()*1000)
  return timestamp

async def timestamp_to_datetime(timestamp):
  ts_series=timestamp.apply(lambda x: datetime.fromtimestamp(x/1000))
  return ts_series
    # Create a subclass of Strategy to define the indicators and logic
def timestamp_to_datetime_2(timestamp):
  ts_series = timestamp.apply(lambda x: datetime.datetime.fromtimestamp(x/1000))
#   print(ts_series)
#   ts_series = datetime.date(ts_series)
  return ts_series
#buy, sell 제대로 됐는지 체크할 것 **

# 참조: https://github.com/mementum/backtrader/blob/master/samples/sigsmacross/sigsmacross.py

async def main():
    c = await db.db_connect() 
    global df_vi 
    global df_daily
    # LOAD DAILY
    df_daily = await db.historical_candle_db_load()
    df_daily['DT']= timestamp_to_datetime_2(df_daily['MTS'])
    df_daily.set_index('DT')
    #LOAD VI
    df_vi = await db.vi_db_load(c)
    
    c.commit()
    c.close()
    # BACKTESTING
    cerebro = bt.Cerebro()
    cerebro.broker.setcash(10000.0) #1.2M
    cerebro.broker.setcommission(commission=0.002)
    # cerebro.addsizer(bt.sizers.PercentSizer, percents=20)

    df_daily_test=df_daily[-400:]
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
    cerebro = bt.Cerebro()  # create a "Cerebro" engine instance
    print(df_daily)
    df_0 = bt.feeds.PandasData(dataname=df_daily_test, datetime='DT',high='HIGH',low='LOW',close='CLOSE',open='OPEN',timeframe=bt.TimeFrame.Minutes,compression=30)

    # cerebro.adddata(df_0)  # Add the data feed
    cerebro.resampledata(df_0,timeframe=bt.TimeFrame.Minutes,compression=30)

    cerebro.addstrategy(strategy.vi_strategy)  # Add the trading strategy
    # cerebro.addstrategy(strategy.StochrsiCross)  # Add the trading strategy

    cerebro.run()
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

    cerebro.plot()  # and plot it with a single command

    
  
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())