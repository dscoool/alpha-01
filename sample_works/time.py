import time
import datetime
# import datetime
now = int(round(time.time() * 1000))

#timestamp 형식 (UTC)
print(round(datetime.datetime(2021, 9, 30, 8, 16, 42, 200000).timestamp()*1000))
# print(round(time.time(11,11,24)*1000))
# datetime.time(hour=0, minute=0, second=0, microsecond=0, tzinfo=None, *, fold=0)¶
print(time.time())
# print(type(time.time()))
