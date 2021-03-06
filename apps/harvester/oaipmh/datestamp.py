import datetime
from harvester.oaipmh.error import DatestampError

def datetime_to_datestamp(dt, day_granularity=False):
    assert dt.tzinfo is None # only accept timezone naive datetimes
    # ignore microseconds
    dt = dt.replace(microsecond=0)
    result = dt.isoformat() + 'Z'
    if day_granularity:
        result = result[:-10]
    return result

# handy utility function not used by pyoai itself yet
def date_to_datestamp(d, day_granularity=False): 	 
    return datetime_to_datestamp( 	 
        datetime.datetime.combine(d, datetime.time(0)), day_granularity)

def datestamp_to_datetime(datestamp):
    try:
        return _datestamp_to_datetime(datestamp)
    except ValueError:
        raise DatestampError(datestamp)
    
def _datestamp_to_datetime(datestamp):
    splitted = datestamp.split('T')
    if len(splitted) == 2:
        d, t = splitted
        if not t or t[-1] != 'Z':
            raise DatestampError(datestamp)
        # strip off 'Z'
        t = t[:-1]
    else:
        d = splitted[0]
        t = '00:00:00'
    YYYY, MM, DD = d.split('-')
    hh, mm, ss = t.split(':') # this assumes there's no timezone info
    return datetime.datetime(
        int(YYYY), int(MM), int(DD), int(hh), int(mm), int(ss))

def tolerant_datestamp_to_datetime(datestamp):
    """A datestamp to datetime that's more tolerant of diverse inputs.

    Not used inside pyoai itself right now, but can be used when defining
    your own metadata schema if that has a broader variety of datetimes
    in there.
    """
    splitted = datestamp.split('T')
    if len(splitted) == 2:
        d, t = splitted
        # if no Z is present, raise error
        if t[-1] != 'Z':
            raise DatestampError(datestamp)
        # split off Z at the end
        t = t[:-1]
    else:
        d = splitted[0]
        t = '00:00:00'
    d_splitted = d.split('-')
    if len(d_splitted) == 3:
        YYYY, MM, DD = d_splitted
    elif len(d_splitted) == 2:
        YYYY, MM = d_splitted
        DD = '01'
    elif len(d_splitted) == 1:
        YYYY = d_splitted[0]
        MM = '01'
        DD = '01'   
    else:
        raise DatestampError(datestamp)
    
    t_splitted = t.split(':')
    if len(t_splitted) == 3:
        hh, mm, ss = t_splitted
    else:
        raise DatestampError(datestamp)
    return datetime.datetime(
        int(YYYY), int(MM), int(DD), int(hh), int(mm), int(ss))
