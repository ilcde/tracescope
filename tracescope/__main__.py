import argparse,json,sys,threading,time
from pathlib import Path
from .discovery import doctor
from .protocol import validate_trace
from .service import Runner,make_server

def main():
    p=argparse.ArgumentParser(prog='tracescope');sub=p.add_subparsers(dest='command',required=True)
    sub.add_parser('doctor')
    for name in ('serve','desktop'):
        s=sub.add_parser(name);s.add_argument('--port',type=int,default=0 if name=='desktop' else 7432);s.add_argument('--host',default='127.0.0.1');s.add_argument('--trusted-local',action='store_true');s.add_argument('--token');s.add_argument('--cert');s.add_argument('--key');s.add_argument('--allow-origin',action='append',default=[])
    t=sub.add_parser('trace');t.add_argument('file');t.add_argument('--language',required=True);t.add_argument('--profile',default='x86-64');t.add_argument('--out',required=True);t.add_argument('--stdin',default='');t.add_argument('--trusted-local',action='store_true');t.add_argument('--benchmark',action='store_true');t.add_argument('--optimized',action='store_true');t.add_argument('--max-events',type=int,default=3000);t.add_argument('--instruction',action='store_true')
    v=sub.add_parser('validate');v.add_argument('file')
    project=sub.add_parser('project');project.add_argument('file');project.add_argument('--out',required=True);project.add_argument('--trusted-local',action='store_true')
    a=p.parse_args()
    if a.command=='doctor':print(json.dumps(doctor(),indent=2));return
    if a.command=='validate':validate_trace(json.loads(Path(a.file).read_text(encoding='utf-8')));print('Valid tracescope/1 trace');return
    if a.command in ('trace','project'):
        if a.command=='project':
            spec=json.loads(Path(a.file).read_text(encoding='utf-8'))
            if spec.get('schema')!='tracescope-project/1':raise ValueError('Invalid project schema')
            config={**spec.get('config',{}),'language':spec['language'],'entry':spec['entry'],'files':spec['files'],'source':spec['files'][spec['entry']]}
        else:config=dict(language=a.language,source=Path(a.file).read_text(encoding='utf-8'),profile=a.profile,stdin=a.stdin,mode='benchmark' if a.benchmark else 'trace',buildProfile='optimized' if a.optimized else 'learn',maxEvents=a.max_events,instruction=a.instruction)
        runner=Runner(a.trusted_local);rid=runner.start(config)
        run=runner.runs[rid]
        while run['process'].poll() is None:time.sleep(.05)
        time.sleep(.1);Path(a.out).parent.mkdir(parents=True,exist_ok=True);Path(a.out).write_text(json.dumps(run['data'],ensure_ascii=False,indent=2),encoding='utf-8')
        print(json.dumps({'status':run['data']['status'],'events':len(run['data']['events']),'output':a.out,'diagnostics':run['data']['diagnostics']}))
        sys.exit(0 if run['data']['status']=='completed' else 1)
    server=make_server(a.host,a.port,a.trusted_local,a.token,a.cert,a.key,a.allow_origin)
    url=f"{'https' if a.cert else 'http'}://{a.host}:{server.server_port}/#token={server.token}"
    print('TraceScope: '+url,flush=True)
    if a.command=='desktop':
        import webview
        threading.Thread(target=server.serve_forever,daemon=True).start();webview.create_window('TraceScope',url,width=1440,height=950,min_size=(420,640));webview.start();server.shutdown()
    else:
        try:server.serve_forever()
        except KeyboardInterrupt:server.shutdown()

if __name__=='__main__':main()
