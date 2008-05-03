"""
    pyrtc high level functions
    Authored by Michael 'Mickey' Lauer <mlauer@vanille-media.de>
    (C) 2008 OpenMoko, Inc.
    GPLv2 or later
"""

__version__ = "1.0.0"

cdef extern from "time.h":
    struct tm:
        int tm_sec
        int tm_min
        int tm_hour
        int tm_mday
        int tm_mon
        int tm_year
        int tm_wday
        int tm_yday
        int tm_isdst

cdef extern from "linux/rtc.h":
    struct rtc_wkalrm:
        char enabled
        char pending
        tm time

cdef extern from "rtc.c":
    int rtc_read_time(tm*)
    int rtc_write_time(tm*)
    int rtc_read_alarm(rtc_wkalrm*)
    int rtc_write_alarm(rtc_wkalrm*)
    int rtc_disable_alarm()

def rtcReadTime():
    """Read the RTC time"""
    cdef tm t
    cdef int success
    success = rtc_read_time(&t)
    if ( success ):
        return ( t.tm_year+1900, t.tm_mon+1, t.tm_mday, t.tm_hour, t.tm_min, t.tm_sec, t.tm_wday, t.tm_yday, t.tm_isdst )
    else:
        return None

def rtcSetTime( newTime ):
    """Set the RTC time"""
    cdef tm t
    t.tm_year, t.tm_mon, t.tm_mday, t.tm_hour, t.tm_min, t.tm_sec, t.tm_wday, t.tm_yday, t.tm_isdst = newTime
    t.tm_year -= 1900
    t.tm_mon -= 1
    cdef int success
    success = rtc_write_time(&t)
    return success

def rtcReadAlarm():
    """Read the RTC Wakeup Alarm"""
    cdef rtc_wkalrm a
    cdef int success
    success = rtc_read_alarm(&a)
    if ( success ):
        return ( a.enabled, a.pending ), ( a.time.tm_year+1900, a.time.tm_mon+1, a.time.tm_mday, a.time.tm_hour, a.time.tm_min, a.time.tm_sec, a.time.tm_wday, a.time.tm_yday, a.time.tm_isdst )
    else:
        return None

def rtcSetAlarm( newAlarm ):
    """Set a new RTC Wakeup Alarm"""
    cdef rtc_wkalrm a
    a.enabled = 1
    a.pending = 0
    a.time.tm_year, a.time.tm_mon, a.time.tm_mday, a.time.tm_hour, a.time.tm_min, a.time.tm_sec, a.time.tm_wday, a.time.tm_yday, a.time.tm_isdst = newAlarm
    a.time.tm_year -= 1900
    a.time.tm_mon -= 1
    cdef int success
    success = rtc_write_alarm(&a)
    return success

def rtcDisableAlarm():
    """Disable the RTC Wakeup Alarm"""
    return rtc_disable_alarm()
