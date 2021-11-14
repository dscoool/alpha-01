from __future__ import (absolute_import, division, print_function, unicode_literals)
import datetime
import asyncio
import get_public_data
import coinone_01
import vars
import pandas as pd
import time
import db
import vortex
import backtrader as bt
from ta import add_all_ta_features
from ta.utils import dropna
from ta import trend
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

class SmaCross(bt.SignalStrategy):
    def __init__(self):
        sma1, sma2 = bt.ind.SMA(period=10), bt.ind.SMA(period=30)
        crossover = bt.ind.CrossOver(sma1, sma2)
        self.signal_add(bt.SIGNAL_LONG, crossover)

class vi_strategy(bt.SignalStrategy):
    def notify_order(self, order):
        if not order.alive():
            print('{} {} {}@{}'.format(
                bt.num2date(order.executed.dt),
                'buy' if order.isbuy() else 'sell',
                order.executed.size,
                order.executed.price)
            )

    def notify_trade(self, trade):
        if trade.isclosed:
            print('profit {}'.format(trade.pnlcomm))

    def __init__(self):
        vi_diff=df_vi.loc[:,'VI_DIFF']
        vi_pos=df_vi.loc[:,'VI_POS']
        vi_neg=df_vi.loc[:,'VI_NEG']
        self.crossover = bt.ind.CrossOver(vi_pos, vi_neg)
        self.signal_add(bt.SIGNAL_LONG, self.crossover)

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
    cerebro.broker.setcash(1200000.0) #1.2M
    cerebro.broker.setcommission(commission=0.0)
    # cerebro.addsizer(bt.sizers.PercentSizer, percents=20)

    df_daily_test=df_daily[-400:]
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
    cerebro = bt.Cerebro()  # create a "Cerebro" engine instance
    
    df_0 = bt.feeds.PandasData(dataname=df_daily_test, datetime='DT',high='HIGH',low='LOW',close='CLOSE',open='OPEN')

    cerebro.adddata(df_0)  # Add the data feed
    cerebro.resampledata(df_0,timeframe=bt.TimeFrame.Minutes,compression=30)

    cerebro.addstrategy(SmaCross)  # Add the trading strategy
    cerebro.run()

    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

    cerebro.plot()  # and plot it with a single command

    
  
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())