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
import backtrader.feeds as btfeed
import strategy
import argparse
import os 

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
    # global df_vi 
    # global df_daily
    # LOAD DAILY
    df_tt = await db.historical_candle_db_load()
    df_tt['DT']= timestamp_to_datetime_2(df_tt['MTS'])
    df_tt.set_index('DT')
    filename_csv = datetime.datetime.today().strftime(format = "%Y%m%d%H%M")
    df_tt.to_csv(os.path.join('./csv/',filename_csv+'.csv'))

    start=datetime.datetime(2020, 1, 1)
    end=datetime.datetime(2020, 12, 31)
    #LOAD VI
    # df_vi = await db.vi_db_load(c)
    
    c.commit()
    c.close()
    # BACKTESTING
    cerebro = bt.Cerebro()
    cerebro.broker.setcash(10000.0) #1.2M
    cerebro.broker.setcommission(commission=0.002)
    # cerebro.addsizer(bt.sizers.PercentSizer, percents=20)

    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
    cerebro = bt.Cerebro()  # create a "Cerebro" engine instance
    # df_0 = bt.feeds.PandasData(dataname=df_daily_test, datetime='DT',high='HIGH',low='LOW',close='CLOSE',open='OPEN',timeframe=bt.TimeFrame.Minutes,compression=30)
    
    df_00 = btfeed.GenericCSVData(
    dataname=os.path.join('./csv/',filename_csv+'.csv'),

    fromdate=start,
    todate=end,

    nullvalue=0.0,

    dtformat=('%Y-%m-%d %H:%M:%S'),
    tmformat=('%H:%M:%S'),

    datetime='DT',
    time=-1,
    high='HIGH',
    low='LOW',
    open='OPEN',
    close='CLOSE',
    volume='VOLUME',
    openinterest=-1
)
    # cerebro.adddata(df_0)  # Add the data feed
    cerebro.resampledata(df_00,timeframe=bt.TimeFrame.Minutes,compression=30)

    cerebro.addstrategy(strategy.vi_strategy)  # Add the trading strategy
    # cerebro.addstrategy(strategy.StochrsiCross)  # Add the trading strategy

    cerebro.run()
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

    cerebro.plot()  # and plot it with a single command

    
  
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())