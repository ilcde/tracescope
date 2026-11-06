from __future__ import annotations
import hashlib, json, platform, time, uuid

SCHEMA = 'tracescope/1'
STATES = {'available', 'unavailable', 'optimized-out', 'uninitialized', 'freed', 'stale', 'truncated', 'uncaptured'}

def digest(data: str | bytes) -> str:
    return hashlib.sha256(data.encode('utf-8') if isinstance(data, str) else data).hexdigest()

def manifest(language, source, filename, adapter, target=None):
    return dict(schema=SCHEMA, runId=str(uuid.uuid4()), sourceHash=digest(source), buildHash=None,
                source=source, filename=filename, language=language, adapter=adapter,
                host=dict(os=platform.system(), release=platform.release(), machine=platform.machine()),
                target=target or dict(isa=platform.machine(), endian='little', abi='host'),
                createdAt=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
                events=[], artifacts=[], diagnostics=[], metrics={}, status='running', limitations=[])

class Recorder:
    def __init__(self, emit, limit=5000):
        self.emit, self.limit = emit, limit
        self.seq, self.start, self.previous = 0, time.monotonic_ns(), {}

    def event(self, kind, line=0, frame='main', function='<module>', values=None, **extra):
        if self.seq >= self.limit:
            raise TraceLimit('event quota reached')
        values = values or {}
        prior = self.previous.get(frame, {})
        delta = {'set': {k:v for k,v in values.items() if prior.get(k) != v},
                 'remove': [k for k in prior if k not in values]}
        event = dict(seq=self.seq, timeNs=str(time.monotonic_ns()-self.start), kind=kind,
                     line=line, column=0, thread='main', task=None, frame=frame,
                     function=function, phase='before' if kind in ('line','instruction') else 'observed',
                     values=values, delta=delta, checkpoint=self.seq % 100 == 0, **extra)
        self.previous[frame] = values
        self.seq += 1
        self.emit({'event':event})
        return event

class TraceLimit(Exception): pass

def validate_trace(data):
    if not isinstance(data, dict) or data.get('schema') != SCHEMA:
        raise ValueError('Unsupported trace schema')
    if not isinstance(data.get('source'), str) or len(data['source']) > 1_000_000:
        raise ValueError('Invalid source snapshot')
    if digest(data['source']) != data.get('sourceHash'):
        raise ValueError('Source hash mismatch')
    events = data.get('events')
    if not isinstance(events, list) or len(events) > 10000:
        raise ValueError('Invalid event count')
    for i,e in enumerate(events):
        if not isinstance(e,dict) or e.get('seq') != i or not isinstance(e.get('values'),dict):
            raise ValueError('Invalid event sequence or state')
        if not isinstance(e.get('timeNs'),str) or not e['timeNs'].isdigit():
            raise ValueError('Monotonic nanoseconds must be decimal strings')
        if not isinstance(e.get('line'),int) or e['line']<0 or not isinstance(e.get('kind'),str):
            raise ValueError('Invalid source location or event kind')
        if not isinstance(e.get('delta'),dict) or not isinstance(e['delta'].get('set'),dict) or not isinstance(e['delta'].get('remove'),list):
            raise ValueError('Invalid state delta')
        budget=[0]
        def value(v,depth=0):
            budget[0]+=1
            if depth>6 or budget[0]>5000 or not isinstance(v,dict):raise ValueError('Value traversal quota')
            if not isinstance(v.get('type'),str) or not isinstance(v.get('value'),str) or v.get('state') not in STATES:raise ValueError('Invalid typed value')
            if 'children' in v:
                if not isinstance(v['children'],dict):raise ValueError('Invalid children')
                for child in v['children'].values():value(child,depth+1)
        for v in e['values'].values():value(v)
    return data
