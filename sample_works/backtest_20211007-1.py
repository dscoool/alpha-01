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
#데이터 제대로 feed 되었는가?
#signal 제대로 만들어 졌는가?
#모델링 제대로 되었는가?

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
        # print(type(sma1))
        crossover = bt.ind.CrossOver(sma1, sma2)
        self.signal_add(bt.SIGNAL_LONG, crossover)

#strategy
class vi_strategy(bt.SignalStrategy):
    def __init__(self):
        vi_plus = bt.ind.Vortex(self.data).vi_plus
        vi_minus = bt.ind.Vortex(self.data).vi_minus
        crossover = bt.ind.CrossOver(vi_plus, vi_minus)

        crossup = bt.ind.CrossUp(vi_plus, vi_minus)
        crossdown = bt.ind.CrossDown(vi_plus,vi_minus)
        # exit = 0
        # self.signal_add(bt.SIGNAL_LONG, crossover)
        
        self.signal_add(bt.SIGNAL_LONG, crossup)
        self.signal_add(bt.SIGNAL_SHORT, crossdown)
        # # self.signal_add(bt.SIGNAL_LONGEXIT, exit)

# class Vortex(bt.Indicator):
#     lines = ('vi_plus', 'vi_minus',)
#     params = (('period', 14),)

#     plotlines = dict(vi_plus=dict(_name='+VI'), vi_minus=dict(_name='-VI'))

#     def __init__(self):
#         h0l1 = abs(self.data.high(0) - self.data.low(-1))
#         vm_plus = bt.ind.SumN(h0l1, period=self.p.period)

#         l0h1 = abs(self.data.low(0) - self.data.high(-1))
#         vm_minus = bt.ind.SumN(l0h1, period=self.p.period)

#         h0c1 = abs(self.data.high(0) - self.data.close(-1))
#         l0c1 = abs(self.data.low(0) - self.data.close(-1))
#         h0l0 = abs(self.data.high(0) - self.data.low(0))

#         tr = bt.ind.SumN(bt.Max(h0l0, h0c1, l0c1), period=self.p.period)

#         self.l.vi_plus = vm_plus / tr
#         self.l.vi_minus = vm_minus / tr

# class VortexExitSignal(bt.Indicator): #buy했으나 긴급상황시 포지션 정리 (sell)
#     def __init__(self):
#         #손실률 넣기 1%이상 손실시 포지션 정리
#         vi_plus = bt.ind.Vortex(self.data).vi_plus
#         vi_minus = bt.ind.Vortex(self.data).vi_minus
#         crossdown = bt.ind.CrossDown(vi_plus, vi_minus)
#         # self.signal_add(bt.SIGNAL_SHORT crossdown)
#         # sma1 = bt.indicators.SMA(period=self.p.p1)
#         # sma2 = bt.indicators.SMA(period=self.p.p2)
#         # self.lines.signal = sma1 - sma2

#buy, sell 제대로 됐는지 체크할 것 **

# 참조: https://github.com/mementum/backtrader/blob/master/samples/sigsmacross/sigsmacross.py

async def main():
    c = await db.db_connect() 
    global df_vi 
    global df_daily
    # LOAD DAILY
    df_daily = await db.historical_candle_db_load()
    df_daily['DT']= timestamp_to_datetime_2(df_daily['MTS'])
    df_daily.set_index('MTS')
    #LOAD VI
    df_vi = await db.vi_db_load(c)
    
    c.commit()
    c.close()
    # BACKTESTING
    cerebro = bt.Cerebro()
    cerebro.broker.setcash(20000.0) #1.2M
    cerebro.broker.setcommission(commission=0.002)
    cerebro.addsizer(bt.sizers.PercentSizer, percents=10)

    df_daily_test=df_daily[-2000:] #1,000 recent records backtesting!!
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
    cerebro = bt.Cerebro() 
    # date and time well feeded?
    df_0 = bt.feeds.PandasData(dataname=df_daily_test, datetime='DT',high='HIGH',low='LOW',close='CLOSE',open='OPEN')
    # Add the data feed
    #timeframe = 30 Minutes
    cerebro.resampledata(df_0,timeframe=bt.TimeFrame.Minutes,compression=30)
    # cerebro.adddata(df_0)
    #strategy
    # cerebro.addstrategy(vi_strategy)  
    cerebro.addstrategy(SmaCross)  

    # if args.exitsignal is not None:
    #     cerebro.add_signal(EXITSIGNALS[args.exitsignal],
    #                        SMAExitSignal,
    #                        p1=args.exitperiod,
    #                        p2=args.smaperiod)
    cerebro.run()

    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

    cerebro.plot()  # and plot it with a single command

    
  
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())