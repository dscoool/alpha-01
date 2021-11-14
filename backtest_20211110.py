from __future__ import (absolute_import, division, print_function, unicode_literals)
import datetime
import asyncio
import get_public_data
import coinone_01
import vars
import pandas as pd
import time
import timeconvert
import db
import backtrader as bt
import backtrader.feeds as btfeed
import strategy
import argparse
import os 
from numpy import log

#buy, sell 제대로 됐는지 체크할 것 **

# 참조: https://github.com/mementum/backtrader/blob/master/samples/sigsmacross/sigsmacross.py

async def main():
    c = await db.db_connect() 
    # LOAD HISTORICAL_CANDLE 30m
    df_tt = await db.historical_candle_db_load()
    df_tt['DT']= timeconvert.timestamp_to_datetime_2(df_tt['MTS'])
    df_tt.set_index('DT')
    #set log_e
    df_tt['CLOSE']=log(df_tt['CLOSE'])
    df_tt['HIGH']=log(df_tt['HIGH'])
    df_tt['LOW']=log(df_tt['LOW'])
    df_tt['OPEN']=log(df_tt['OPEN'])

    filename_csv = datetime.datetime.today().strftime(format = "%Y%m%d%H%M")
    # export data to csv and reimport with GenericCSVData
    df_tt.to_csv(os.path.join('./csv/',filename_csv+'.csv'))

    start=datetime.datetime(2019, 1, 1)
    end=datetime.datetime(2021, 10,1)
    #LOAD VI
    # df_vi = await db.vi_db_load(c)
    
    c.commit()
    c.close()

    # BACKTESTING
    cerebro = bt.Cerebro()
    cerebro.broker.setcash(1200000.0) #1.2M
    cerebro.broker.setcommission(commission=0.002)
    # cerebro.addsizer(bt.sizers.SizerFix, stake=0.1) 
    cerebro.addsizer(bt.sizers.PercentSizer, percents=20)
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

    df_00 = btfeed.GenericCSVData(
        dataname=os.path.join('./csv/',filename_csv+'.csv'),
        fromdate=start,
        todate=end,
        nullvalue=0.0,
        dtformat=('%Y-%m-%d %H:%M:%S'),
        tmformat=('%H:%M:%S'),
        datetime=8,
        # time=-1,
        high=5,
        low=6,
        open=3,
        close=4,
        volume=7,
        # openinterest=-1,
        timeframe = bt.TimeFrame.Minutes,
        compression=30
    )
    cerebro.adddata(df_00)  # Add the data feed
    # cerebro.addstrategy(strategy.St)
    # cerebro.addstrategy(strategy.VICross)  # Add the trading strategy
    cerebro.addstrategy(strategy.EMACross)
    # cerebro.add_signal(bt.SIGNAL_LONG, strategy.VILongSignal,period=14)

    #로그 칠 것!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    cerebro.run()
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
    cerebro.plot()  # and plot it with a single command
    return
    
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())