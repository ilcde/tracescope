import json,time
from pathlib import Path
from tracescope.service import Runner
from tracescope.protocol import validate_trace
ROOT=Path(__file__).resolve().parent.parent

def capture(config):
    runner=Runner(True);rid=runner.start(config);run=runner.runs[rid]
    while run['process'].poll() is None:time.sleep(.03)
    time.sleep(.1)
    return run['data']

def test_compile_failure_and_output_quota():
    bad=capture({'language':'c','source':'int main( { broken code'})
    assert bad['status']=='failed' and bad['metrics']['compileMs']>0 and bad['diagnostics']
    (ROOT/'evidence/compile-failure.json').write_text(json.dumps(bad),encoding='utf-8')
    output=capture({'language':'python','source':'print("x"*70000)'})
    assert output['status']=='truncated';validate_trace(output)
    (ROOT/'evidence/output-quota.json').write_text(json.dumps(output),encoding='utf-8')

def test_compiled_stdin_changes_actual_values():
    sources={
      'c':'#include <stdio.h>\nint main(void){\n int n;\n scanf("%d", &n);\n int result=n*3;\n printf("%d\\n", result);\n return 0;\n}',
      'cpp':'#include <iostream>\nint main(){\n int n;\n std::cin >> n;\n int result=n*3;\n std::cout << result << "\\n";\n return 0;\n}',
      'java':'import java.util.Scanner;\npublic class Main {\n public static void main(String[] args) {\n int n=new Scanner(System.in).nextInt();\n int result=n*3;\n System.out.println(result);\n }\n}',
      'kotlin':'fun main(){\n val n=readln().toInt()\n val result=n*3\n println(result)\n}',
      'rust':'use std::io;\nfn main(){\n let mut text=String::new();\n io::stdin().read_line(&mut text).unwrap();\n let n:i32=text.trim().parse().unwrap();\n let result=n*3;\n println!("{}",result);\n}',
    }
    evidence=[]
    for language,source in sources.items():
        outputs=[]
        for n in (3,7):
            trace=capture({'language':language,'source':source,'stdin':str(n)+'\n'})
            assert trace['status']=='completed',(language,trace['diagnostics'],trace.get('termination'))
            text=''.join(e.get('output','') for e in trace['events']).strip();assert text==str(n*3),(language,text)
            assert any(e['values'].get('result',{}).get('value')==str(n*3) for e in trace['events']),(language,'missing result')
            outputs.append(text);(ROOT/'evidence'/(language+'-stdin-'+str(n)+'.json')).write_text(json.dumps(trace),encoding='utf-8')
        assert outputs[0]!=outputs[1];evidence.append({'language':language,'inputs':[3,7],'outputs':outputs,'status':'passed'})
    (ROOT/'evidence/stdin-journeys.json').write_text(json.dumps(evidence,indent=2),encoding='utf-8')
