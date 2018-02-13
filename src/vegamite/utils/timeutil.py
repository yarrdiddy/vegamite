import datetime, re


TIME_RANGE_MULTIPLIERS = {
    'month': 30,
    'months': 30,
    'year': 365,
    'years': 365
}

def parse_time_range(time_range):
    time_range_content = re.findall(r'(^[0-9]+\b|year[s]?|month[s]?|day[s]?|hour[s]?|minute[s]?)', time_range)
                
    _count = int(time_range_content[0])
    _unit = time_range_content[1]

    offset = None

    if _unit in TIME_RANGE_MULTIPLIERS.keys():
        _multiplier = TIME_RANGE_MULTIPLIERS[_unit]
        offset = datetime.timedelta(days=_count * _multiplier)
    elif 'day' in _unit:
        offset = datetime.timedelta(days=_count)
    elif 'hour' in _unit:
        offset = datetime.timedelta(hours=_count)
    elif 'minute' in _unit:
        offset = datetime.timedelta(minutes=_count)

    return offset

