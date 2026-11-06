import time
import pytest
from tracescope.conditions import predicate
from tracescope.service import Runner

def test_conditions_never_call_user_hooks():
    class Trap:
        def __eq__(self,other):raise AssertionError('user comparison executed')
        def __bool__(self):raise AssertionError('user truth conversion executed')
    assert predicate('n >= 3 and n % 2 == 1')({'n':3})
    assert not predicate('n == 3')({'n':Trap()})
    for source in ('f()','obj.value','obj[0]','2**100000'):
        with pytest.raises(ValueError):predicate(source)

def test_live_conditional_breakpoint_and_observed_watch():
    runner=Runner(True)
    run_id=runner.start({'language':'python','source':'total=0\nfor i in range(4):\n total+=i\nprint(total)\n','breakpoints':[3],'breakpointCondition':'i == 2'})
    run=runner.runs[run_id];deadline=time.monotonic()+15
    while run['data']['status']!='paused' and time.monotonic()<deadline:time.sleep(.02)
    try:
        assert run['data']['status']=='paused'
        assert run['data']['events'][-1]['values']['i']['value']=='2'
        runner.control(run_id,{'action':'continue'})
        run['process'].wait(timeout=10)
    finally:
        if run['process'].poll() is None:runner.control(run_id,{'action':'stop'})
    watch_id=runner.start({'language':'python','source':'total=0\ntotal=21\nprint(total)\n','watch':['total']})
    watch=runner.runs[watch_id];deadline=time.monotonic()+15;found=False
    try:
        while watch['process'].poll() is None and time.monotonic()<deadline:
            if watch['data']['status']=='paused':
                event=watch['data']['events'][-1]
                if event['values'].get('total',{}).get('value')=='21':found='total' in event.get('watchChanges',[])
                runner.control(watch_id,{'action':'continue'})
            time.sleep(.03)
        assert found
    finally:
        if watch['process'].poll() is None:runner.control(watch_id,{'action':'stop'})
