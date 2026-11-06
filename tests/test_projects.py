import json,time
from pathlib import Path
import pytest
from tracescope.service import Runner
from tracescope.project import validate_files

PROJECTS={
 'python':('main.py',{'main.py':'from helper import triple\nresult=triple(7)\nprint(result)\n','helper.py':'def triple(n):\n    value=n*3\n    return value\n'}),
 'c':('main.c',{'main.c':'#include <stdio.h>\nint triple(int);\nint main(){\n int result=triple(7);\n printf("%d\\n",result);\n return 0;\n}\n','helper.c':'int triple(int n){\n int value=n*3;\n return value;\n}'}),
 'cpp':('main.cpp',{'main.cpp':'#include <iostream>\nint triple(int);\nint main(){\n int result=triple(7);\n std::cout << result << "\\n";\n return 0;\n}\n','helper.cpp':'int triple(int n){\n int value=n*3;\n return value;\n}'}),
 'rust':('main.rs',{'main.rs':'mod helper;\nfn main(){\n let result=helper::triple(7);\n println!("{}",result);\n}','helper.rs':'pub fn triple(n:i32)->i32{\n let value=n*3;\n value\n}'}),
 'java':('Main.java',{'Main.java':'public class Main {\n public static void main(String[] args){\n int result=Helper.triple(7);\n System.out.println(result);\n }\n}','Helper.java':'class Helper {\n static int triple(int n){\n int value=n*3;\n return value;\n }\n}'}),
 'kotlin':('Main.kt',{'Main.kt':'fun main(){\n val result=triple(7)\n println(result)\n}','Helper.kt':'fun triple(n:Int):Int{\n val value=n*3\n return value\n}'}),
}

@pytest.mark.parametrize('language',PROJECTS)
def test_multifile_changed_source_has_real_helper_observations(language):
    entry,files=PROJECTS[language];runner=Runner(True)
    rid=runner.start({'language':language,'entry':entry,'files':files,'source':files[entry]})
    run=runner.runs[rid]
    while run['process'].poll() is None:time.sleep(.05)
    time.sleep(.1);trace=run['data']
    Path('evidence').mkdir(exist_ok=True);Path(f'evidence/project-{language}.json').write_text(json.dumps(trace),encoding='utf-8')
    assert trace['status']=='completed',trace.get('diagnostics')
    assert ''.join(e.get('output','') for e in trace['events']).strip()=='21'
    assert any(e.get('file','').lower().startswith('helper.') and e['values'] for e in trace['events']),language
    assert trace['sources']==files

def test_project_paths_cannot_escape_staging_directory():
    for name in ('../outside.py','/outside.py','C:/outside.py','a/../../outside.py','a\\outside.py'):
        with pytest.raises(ValueError):validate_files({name:'x'},'main.py','pass')
