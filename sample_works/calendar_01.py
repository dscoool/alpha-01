import calendar 

cal = calendar.Calendar()
year = 2017
month = 2

for i in cal.itermonthdays4(year, month):
    print(i)
