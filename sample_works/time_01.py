import pandas as pd
from ta.utils import dropna
from ta.trend import VortexIndicator
from time import strftime
from datetime import datetime
# Load datas
df = pd.read_csv('btcusd_2021-10-01.csv', sep=',')

# Clean NaN values
df = dropna(df)

# Initialize Bollinger Bands Indicator
# vortex_indicator = VortexIndicator(high=df["HIGH"], low=df["LOW"], close=df["CLOSE"],
#     window=14, fillna=False)

# dates = pd.to_datetime(pd.Series(['20010101', '20010331']), format = '%Y%m%d')
df['DT']=df['MTS'].apply(lambda x: datetime.fromtimestamp(x/1000))
print(df['MTS'])

print(df['DT'])
# print(df['MTS'].divide(1000).dt.dtfrtime())
# print(type(df['MTS']))

# Add Bollinger Bands features
# df['DT'] = [ts.to_datetime() for ts in df['MTS'].divide(1000)]
