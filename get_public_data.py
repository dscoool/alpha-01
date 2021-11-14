import os
import sys
import asyncio
import datetime
import time
import csv
from bfxapi import Client
import vars
from pandas import DataFrame

bfx = Client(
  logLevel='DEBUG',
)

candle_columns = ['MTS', 'OPEN', 'CLOSE', 'HIGH', 'LOW', 'VOLUME']

# start=round(datetime.datetime(2021, 9, 28, 0, 0, 0, 0).timestamp()*1000)
# end=round(datetime.datetime(2021, 9, 28, 23, 59, 59, 0).timestamp()*1000)

# now = int(round(time.time() * 1000))
# then = now - (1000 * 60 * 60 * 24 * 10) # 10 days ago
columns = ['NO','MTS', 'OPEN', 'CLOSE', 'HIGH', 'LOW', 'VOLUME']

async def log_historical_candles(start,end,limit,filename,symbol='tBTCUSD',tf='30m'):
  candles = await bfx.rest.get_public_candles(symbol,start,end, 'hist',tf,limit, '1')
  # print ("Candles:")
  # [ print (c) for c in candles ]
  df_candles=DataFrame(candles,columns=candle_columns)
  df_candles['DT']=df_candles['MTS'].apply(lambda x: datetime.datetime.fromtimestamp(x/1000))
  # df_candles.to_csv(filename)
  # print("exporting data to : ",filename)
  #write file here
  # print('exported csv file:',vars.OUTPUT_FILE_NAME)
  return df_candles
# BfxRest.get_public_candles(symbol,
#                            start, #millisecond start time
#                            end,
#                            section='hist',
#                            tf='1m',
#                            limit='100',
#                            sort=-1)
# Get all of the public candles between the start and end period.

# Attributes

# @param symbol symbol string: pair symbol i.e tBTCUSD
# @param secton string: available values: "last", "hist"
# @param start int: millisecond start time
# @param end int: millisecond end time
# @param limit int: max number of items in response
# @param tf int: timeframe inbetween candles i.e 1m (min), ..., 1D (day), ... 1M (month)
# @param sort int: if = 1 it sorts results returned with old > new @return Array [ MTS, OPEN, CLOSE, HIGH, LOW, VOLUME ]



async def log_historical_trades():
  trades = await bfx.rest.get_public_trades('tBTCUSD', 0, then)
  print ("Trades:")
  [ print (t) for t in trades ]

async def log_books():
  orders = await bfx.rest.get_public_books('tBTCUSD')
  print ("Order book:")
  [ print (o) for o in orders ]

async def log_ticker():
  ticker = await bfx.rest.get_public_ticker('tBTCUSD')
  print ("Ticker:")
  print (ticker)

async def log_mul_tickers():
  tickers = await bfx.rest.get_public_tickers(['tBTCUSD', 'tETHBTC'])
  print ("Tickers:")
  print (tickers)

async def log_derivative_status():
  status = await bfx.rest.get_derivative_status('tBTCF0:USTF0')
  print ("Deriv status:")
  print (status)

# async def run():
  # await log_historical_candles()
#   await log_historical_trades()
#   await log_books()
#   await log_ticker()
#   await log_mul_tickers()
#   await log_derivative_status()
  
# t = asyncio.ensure_future(run())
# asyncio.get_event_loop().run_until_complete(t)
