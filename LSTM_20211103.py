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
import numpy as np

import matplotlib.pyplot as plt
import tensorflow as tf

#buy, sell 제대로 됐는지 체크할 것 **

# 참조: https://github.com/mementum/backtrader/blob/master/samples/sigsmacross/sigsmacross.py

async def main():
    c = await db.db_connect() 
    # LOAD HISTORICAL_CANDLE 30m
    df_tt = await db.historical_candle_db_load()
    df_tt['DT']= timeconvert.timestamp_to_datetime_2(df_tt['MTS'])
    df_tt.set_index('DT')
    filename_csv = datetime.datetime.today().strftime(format = "%Y%m%d%H%M")
    # export data to csv and reimport with GenericCSVData
    df_tt.to_csv(os.path.join('./csv/',filename_csv+'.csv'))

    start=datetime.datetime(2020, 1, 1)
    end=datetime.datetime(2020, 12, 31)
    
    c.commit()
    c.close()
    print(df_tt.columns)
    btc=df_tt[['DATETIME','CLOSE']]

    print(btc)

    dates = btc.DATETIME
    X = np.arange(len(dates)).reshape(-1, 1)
    y = btc.CLOSE.values
    y = y.reshape(-1, 1)

    y_std = y.std()
    y_mean = y.mean()
    y = (y - y_mean) / y_std
    
    test_period = 200

    X_train = X[:-test_period]
    y_train = y[:-test_period]
    X_test = X[-test_period:]
    y_test = y[-test_period:]
    from sklearn.model_selection import train_test_split
    X_train, X_val, y_train, y_val = train_test_split(X_train, y_train, test_size=0.3, random_state=0)
    X = X.reshape(-1, 1, 1)
    X_train = X_train.reshape(-1, 1, 1)
    X_val = X_val.reshape(-1, 1, 1)
    X_test = X_test.reshape(-1, 1, 1)
    
    model = tf.keras.models.Sequential([
    tf.keras.layers.LSTM(8, input_shape=(None, 1)),
    tf.keras.layers.Dense(4),
    tf.keras.layers.Dense(1)])

    # df_00 = btfeed.GenericCSVData(
    #     dataname=os.path.join('./csv/',filename_csv+'.csv'),
    #     fromdate=start,
    #     todate=end,
    #     nullvalue=0.0,
    #     dtformat=('%Y-%m-%d %H:%M:%S'),
    #     tmformat=('%H:%M:%S'),
    #     datetime=8,
    #     # time=-1,
    #     high=5,
    #     low=6,
    #     open=3,
    #     close=4,
    #     volume=7,
    #     # openinterest=-1,
    #     timeframe = bt.TimeFrame.Minutes,
    #     compression=30
    # )
    # cerebro.adddata(df_00)  # Add the data feed
    # cerebro.addstrategy(strategy.LSTM)
    # # cerebro.addstrategy(strategy.St)
    # cerebro.addstrategy(strategy.VICrossUp)  # Add the trading strategy
    # cerebro.add_signal(bt.SIGNAL_LONG, strategy.VILongSignal,period=14)
    # cerebro.addstrategy(strategy.StochrsiCross)  # Add the trading strategy
    # cerebro.addstrategy(strategy.sell_AO)
    # cerebro.run()
    # print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
    # cerebro.plot()  # and plot it with a single command
    return
    
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())