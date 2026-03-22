'''
Created on 2012-7-9

@author: yunify
'''
import time
import datetime

ISO8601_NO_Z = "%Y-%m-%dT%H:%M:%S"
ISO8601 = '%Y-%m-%dT%H:%M:%SZ'
ISO8601_MS = '%Y-%m-%dT%H:%M:%S.%fZ'

def get_ts(ts=None):
    ''' get formatted UTC time '''
    if not ts:
        ts = time.gmtime()
    return time.strftime(ISO8601, ts)


def is_valid_ts(ts):
    ts = ts.strip()
    try:
        time.strptime(ts, ISO8601)
        return True
    except ValueError:
        try:
            time.strptime(ts, ISO8601_MS)
            return True
        except ValueError:
            try:
                time.strptime(ts, ISO8601_NO_Z)
                return True
            except ValueError:
                pass

    return False


def parse_ts(ts):
    ''' parse formatted UTC time to timestamp '''
    ts = ts.strip()
    try:
        ts_s = time.strptime(ts, ISO8601)
        return time.mktime(ts_s)
    except ValueError:
        try:
            ts_s = time.strptime(ts, ISO8601_MS)
            return time.mktime(ts_s)
        except ValueError: 
            return 0

def cmp_ts(ts_a, ts_b):
    ''' comapre two formatted UTC time'''
    ts_a = parse_ts(ts_a)
    ts_b = parse_ts(ts_b)
    return cmp(ts_a, ts_b)

def get_expired_ts(ts, expires_interval):
    ''' get expired timestamp '''
    ts_expired_s = parse_ts(ts) + expires_interval
    ts_expired = time.localtime(ts_expired_s)
    return get_ts(ts_expired)

def time2str(val):
    ''' transform datetime to string '''
    if isinstance(val, datetime.datetime):
        return val.strftime("%Y-%m-%d %H:%M:%S")
    return val

def format_birthday(val):
    ''' transform birthday from datetime to string '''
    if isinstance(val, datetime.datetime):
        return val.strftime("%Y-%m-%d")
    return val

def format_utctime(dt):
    ''' transform local datetime to utc time string '''
    if isinstance(dt, datetime.datetime):
        return time.strftime(ISO8601, time.gmtime(time.mktime(dt.timetuple())))
    return dt

def parse_utctime(ts):
    ''' transform utc time string to local timestamp '''
    timestamp = parse_ts(ts)
    if timestamp == 0:
        return None
    return timestamp - time.altzone

def get_datetime(ts):
    ''' get date time from timestamp '''
    return datetime.datetime.fromtimestamp(ts)
        
def round_timestamp(ts, step, mode="left"):    
    ''' get closest timestamp by step 
        @param mode - left/right/both
    '''     
    index = int(ts / step)
    left = index * step
    if mode == "left":
        return left
    right = (index + 1) * step
    if mode == "right":
        return right
    if ts - left < right - ts:
        return left
    return right   

def local_hour_to_utc_hour(hour):
    if not (0 <= hour <= 23):
        return hour

    local_timetuple = datetime.datetime(2014, 1, 1, hour).timetuple()
    local_ts = time.mktime(local_timetuple)
    utc_struct_time = time.gmtime(local_ts)
    return utc_struct_time.tm_hour

def utc_hour_to_local_hour(hour):
    if not (0 <= hour <= 23):
        return hour

    ts = time.time()
    local_ts = datetime.datetime.fromtimestamp(ts)
    utc_ts = datetime.datetime.utcfromtimestamp(ts)
    timedelta = local_ts - utc_ts

    utc_dt = datetime.datetime(2014, 1, 1, hour)
    local_dt = utc_dt + timedelta
    return local_dt.hour


def ts_seconds_to_utctime(ts_seconds):
    try:
        if isinstance(ts_seconds, str):
            ts_seconds = float(ts_seconds)
        return time.strftime(ISO8601, time.gmtime(ts_seconds))
    except:
        return ts_seconds
