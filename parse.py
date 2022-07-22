from pprint import pprint
import json

raw_lines = open('sample.sa').readlines()

comments = []
tags = {}
trackplan = {
    'count': None,
    'data': [],
}
timer = {
    'unit': None,
    'data': [],
}

trace = {
    'pt': None,
    'data': [],
}

def comment(raw):
    comments.append(raw.lstrip(';').strip())

def info(raw):
    line = raw.lstrip('#')
    tag, data = line.split('=', 1)

    tags.update({tag: data.strip().rstrip('=').strip()})

def timer_units(raw):
    units = raw.split('#unit=')[1].strip().rstrip('>')
    return units

def trackplan_sectors(raw):
    count = raw.split('#sectors=')[1].strip().rstrip('>')
    return count

def trace_pt(raw):
    count = raw.split('#pt=')[1].strip().rstrip('>')
    return count


def parse_timer(raw):
    data = []
    raw_iter = iter(raw['data'])
    prev_sector = 0
    lap = 1

    for head, foot in zip(raw_iter, raw_iter):
        sector, time = head.lstrip('#').split(',')

        if int(sector) < int(prev_sector):
            lap = lap + 1

        prev_sector = sector
        data.append({ 'lap':  int(lap), 'sector': int(sector), 'time': time, 'raw': foot })

    return {
        'unit': raw['unit'],
        'sectors': data
    }

def parse_trackplan(raw):
    data = []

    for line in raw['data']:
        sector, start_lat, start_lon, end_lat, end_lon = line.split(',')
        data.append({
            'sector': int(sector),
            'start': [float(start_lat), float(start_lon)],
            'end': [float(end_lat), float(end_lon)]
        })

    return {
        'count': int(raw['count']),
        'data': data
    }

def parse_trace(raw):
    return {
        'points': raw['pt'],
        'data': raw['data']
    }

def parse(raw):
    header = []
    data = []

    for line in raw_lines:
        if len(data) > 0 or line[0] == '<':
            data.append(line)
        else:
            header.append(line)

    return header, data


header, data = parse(raw_lines)

for line in header:
    if line[0] == ';':
        comment(line)

    if line[0] == '#':
        info(line)

section = None
for line in data:
    if line[0] == '<':
        if 'timer' in line:
            if section is not None:
                timer = parse_timer(timer)
                section = None
                continue

            # get units
            timer['unit'] = timer_units(line)
            section = 'timer'
            continue

        if 'trackplan' in line:
            if section is not None:
                trackplan = parse_trackplan(trackplan)
                section = None
                continue

            # get units
            trackplan['count'] = trackplan_sectors(line)
            section = 'trackplan'
            continue

        if 'trace' in line:
            if section is not None:
                trace = parse_trace(trace)
                section = None
                continue

            # get units
            trace['pt'] = trace_pt(line)
            section = 'trace'
            continue

    if section == 'timer':
        timer['data'].append(line.strip())

    if section == 'trackplan':
        trackplan['data'].append(line.strip())

    if section == 'trace':
        trace['data'].append(line.strip())


out = {
        'comments': comments,
        'tags': tags,
        'trace': trace,
        'trackplan': trackplan,
        'timer': timer
}

print(json.dumps(out))
