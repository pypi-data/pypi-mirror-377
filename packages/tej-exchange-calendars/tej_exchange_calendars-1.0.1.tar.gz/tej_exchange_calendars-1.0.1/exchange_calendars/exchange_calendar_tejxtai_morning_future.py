from datetime import time, datetime
from dateutil.relativedelta import relativedelta
from pytz import timezone
import pandas as pd

from .exchange_calendar_tejxtai import TEJ_XTAIExchangeCalendar




class TEJ_morning_future_XTAIExchangeCalendar(TEJ_XTAIExchangeCalendar):

    name = "TEJ_morning_future"

    tz = timezone("Asia/Taipei")
    
    open_times = ((None, time(8,45)),)
    
    close_times = ((None, time(13, 45)),)
    
    weekmask = "1111111"
    
    start_date = pd.to_datetime('20050101').tz_localize('UTC')
    
    end_date = pd.to_datetime((datetime.now()+relativedelta(years = 1)).strftime('%Y%m%d')).tz_localize('UTC')
    
