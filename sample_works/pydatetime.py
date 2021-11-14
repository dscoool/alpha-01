from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import datetime

from backtrader.utils.py3 import filter, string_types, integer_types

from backtrader import date2num
import backtrader.feed as feed

# 2021-10-02 21:00:00.to_pydatetime()

(datetime.datetime.now()).to_pydatetime()