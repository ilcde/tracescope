import json, sys, traceback
from .protocol import TraceLimit

def main():
    config=json.load(open(sys.argv[1],encoding='utf-8'))
    original=sys.stdout
    def emit(data):
        original.write(json.dumps(data,ensure_ascii=True,allow_nan=False)+'\n'); original.flush()
    try:
        language=config['language']
        if language=='python': from .python_adapter import run
        elif language=='assembly': from .assembly_adapter import run
        elif language in ('java','kotlin'): from .jvm_adapter import run
        elif language in ('c','cpp','rust'): from .native_adapter import run
        else: raise ValueError('Unsupported server adapter '+language)
        exitcode=run(config,emit) or 0
        emit({'status':'completed' if exitcode==0 else 'failed','exitCode':exitcode})
    except TraceLimit as e: emit({'status':'truncated','termination':str(e)})
    except SystemExit as e:
        code=e.code if isinstance(e.code,int) else 0 if e.code is None else 1
        emit({'status':'completed' if code==0 else 'failed','exitCode':code})
    except BaseException as e:
        emit({'status':'failed','exitCode':1,'diagnostics':[{'message':str(e),'line':getattr(e,'lineno',0),'kind':type(e).__name__}]})

if __name__=='__main__': main()
