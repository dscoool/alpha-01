#!/usr/bin/env python
# -*- coding: utf-8; py-indent-offset:4 -*-
###############################################################################
#
# Copyright (C) 2015-2020 Daniel Rodriguez
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################
from datetime import datetime
import backtrader as bt
import backtrader.feeds as btfeed
import os
import asyncio
import db
import timeconvert
import datetime

class SmaCross(bt.SignalStrategy):
    def __init__(self):
        sma1 = bt.ind.AO(self.data)
        # sma2 = bt.ind.SMA(period=30)
        # crossover = bt.ind.CrossOver(sma1, sma2)
        self.signal_add(bt.SIGNAL_SHORT, sma1)

async def main():

    c = await db.db_connect() 
    # LOAD HISTORICAL_CANDLE 30m
    df_tt = await db.historical_candle_db_load()
    df_tt['DT']= timeconvert.timestamp_to_datetime_2(df_tt['MTS'])
    df_tt.set_index('DT')
    filename_csv = datetime.datetime.today().strftime(format = "%Y%m%d%H%M")
    # export data to csv and reimport with GenericCSVData
    df_tt.to_csv(os.path.join('./csv/',filename_csv+'.csv'))

    start=datetime.datetime(2020, 7, 1)
    end=datetime.datetime(2020, 12, 31)


    cerebro = bt.Cerebro()
    cerebro.addstrategy(SmaCross)

    filename_csv = datetime.datetime.today().strftime(format = "%Y%m%d%H%M")


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

    # data0 = bt.feeds.YahooFinanceData(dataname='YHOO',
    #                                   fromdate=datetime(2011, 1, 1),
    #                                   todate=datetime(2012, 12, 31))

    # cerebro.adddata(data0)
    cerebro.adddata(df_00)

    cerebro.run()
    cerebro.plot()

    
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())