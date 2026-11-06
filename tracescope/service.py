from __future__ import annotations
import json, os, secrets, shutil, signal, ssl, subprocess, sys, threading, time
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse,parse_qs
from .discovery import ROOT, doctor, find
from .protocol import manifest, validate_trace
from .complexity import analyze
from .limits import ProcessLimits

class Runner:
    def __init__(self,trusted=False):
        self.trusted=trusted;self.runs={};self.lock=threading.RLock()
    def start(self,config):
        if config.get('language') not in ('python','java','kotlin','c','cpp','rust','assembly'):raise ValueError('Unknown execution adapter')
        if config['language']!='assembly' and not self.trusted:raise PermissionError('Native runner is locked. Start with --trusted-local only for code you trust; this is not isolation.')
        if len(config.get('source',''))>100000:raise ValueError('Source exceeds 100 KiB')
        if len(self.runs)>=20:raise ValueError('Session limit reached; restart runner or export sessions')
        if sum(r['data']['status'] in ('running','paused') for r in self.runs.values())>=2:raise ValueError('At most two active runs')
        extensions={'python':'py','java':'java','kotlin':'kt','c':'c','cpp':'cpp','rust':'rs','assembly':'s'}
        filename=('Main' if config['language'] in ('java','kotlin') else 'main')+'.'+extensions[config['language']]
        data=manifest(config['language'],config['source'],filename,'tracescope-'+config['language']+'/0.1.0')
        run_id=data['runId'];folder=(Path(sys.executable).parent if getattr(sys,'frozen',False) else ROOT)/'.runs'/run_id;folder.mkdir(parents=True)
        config.update(filename=filename,workdir=str(folder),maxEvents=min(5000,max(1,int(config.get('maxEvents',3000)))))
        if not isinstance(config.get('args',[]),list) or not all(isinstance(s,str) for s in config.get('args',[])):raise ValueError('Arguments must be strings')
        if not isinstance(config.get('stdin',''),str) or len(config.get('stdin',''))>65536:raise ValueError('Invalid stdin')
        (folder/'config.json').write_text(json.dumps(config),encoding='utf-8')
        env=os.environ.copy();env['PYTHONIOENCODING']='utf-8'
        # Resolve in the launcher's working directory before the worker changes cwd.
        for tool in ('gcc','g++','gdb','objdump','rustc','java','javac','kotlinc'):
            path=find(tool)
            if path:env['TRACESCOPE_'+tool.upper().replace('+','P')]=str(Path(path).resolve())
        command=([sys.executable,'--worker'] if getattr(sys,'frozen',False) else [sys.executable,'-m','tracescope.worker'])+[str(folder/'config.json')]
        proc=subprocess.Popen(command,cwd=ROOT,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,encoding='utf-8',env=env,start_new_session=os.name!='nt',creationflags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0)
        limits=ProcessLimits(proc)
        run={'data':data,'process':proc,'folder':folder,'started':time.monotonic(),'lastSeen':time.monotonic(),'limits':limits};self.runs[run_id]=run
        data['resourceLimits']=limits.status
        data['isolation']='emulator memory only; host Python process' if config['language']=='assembly' else 'trusted local, NOT sandboxed'
        data['complexity']=analyze(config['source'],config['language'])
        threading.Thread(target=self.collect,args=(run,),daemon=True).start()
        threading.Thread(target=self.watchdog,args=(run,),daemon=True).start()
        return run_id
    def collect(self,run):
        data=run['data'];proc=run['process'];size=0
        try:
            for row in proc.stdout:
                size+=len(row)
                if size>24_000_000:self.stop(run,'trace byte quota');break
                packet=json.loads(row)
                with self.lock:
                    if 'event' in packet:
                        data['events'].append(packet['event'])
                    for key,value in packet.items():
                        if key=='event':continue
                        if key=='metrics':data['metrics'].update(value)
                        else:data[key]=value
            proc.wait(timeout=3)
            if data['status'] in ('running','paused'):
                data.update(status='failed',exitCode=proc.returncode,termination=f'worker exited without a terminal packet (exit {proc.returncode})')
                error=proc.stderr.read(8192)
                if error:data['diagnostics'].append({'message':error})
        except Exception as e:
            self.stop(run,'collector error: '+str(e))
        finally:
            data['metrics']['peakJobCommittedBytes']=run['limits'].peak()
            run['limits'].close()
            data['metrics']['runnerWallMs']=(time.monotonic()-run['started'])*1000
            (run['folder']/'trace.json').write_text(json.dumps(data,ensure_ascii=False),encoding='utf-8')
    def watchdog(self,run):
        while run['process'].poll() is None:
            if time.monotonic()-run['started']>120:self.stop(run,'120 second wall quota');return
            time.sleep(.2)
    def stop(self,run,reason='cancelled'):
        proc=run['process']
        run['data'].update(status='cancelled' if reason=='cancelled' else 'truncated',termination=reason)
        if proc.poll() is None:
            run['limits'].terminate()
            if os.name=='nt':
                subprocess.run(['taskkill','/PID',str(proc.pid),'/T','/F'],capture_output=True,creationflags=subprocess.CREATE_NO_WINDOW)
                if proc.poll() is None:proc.kill()
            else:
                try:os.killpg(proc.pid,signal.SIGKILL)
                except ProcessLookupError:pass
            try:proc.wait(timeout=3)
            except subprocess.TimeoutExpired:pass
        run['data'].update(status='cancelled' if reason=='cancelled' else 'truncated',termination=reason)
    def control(self,run_id,command):
        run=self.runs[run_id]
        if command.get('action')=='stop':self.stop(run);return
        if run['data']['language']!='python':raise ValueError('Live debugger control is currently Python-only; use historical replay for this adapter.')
        if run['process'].poll() is not None:raise ValueError('Run already ended')
        run['process'].stdin.write(json.dumps(command)+'\n');run['process'].stdin.flush()

def make_server(host='127.0.0.1',port=7432,trusted=False,token=None,cert=None,key=None):
    if host not in ('127.0.0.1','localhost','::1') and (not cert or not key or not token):raise ValueError('Remote runner requires TLS certificate, key, and an explicit token')
    runner=Runner(trusted);secret=token or secrets.token_urlsafe(32)
    class Handler(SimpleHTTPRequestHandler):
        def __init__(self,*args,**kwargs):super().__init__(*args,directory=str(ROOT/'dist'),**kwargs)
        def log_message(self,*args):pass
        def end_headers(self):
            self.send_header('X-Content-Type-Options','nosniff');self.send_header('Referrer-Policy','no-referrer')
            origin=self.headers.get('Origin','')
            if origin in ('https://appassets.androidplatform.net','http://127.0.0.1:5173','http://localhost:5173'):
                self.send_header('Access-Control-Allow-Origin',origin);self.send_header('Vary','Origin')
            super().end_headers()
        def do_OPTIONS(self):
            if self.headers.get('Origin','') not in ('https://appassets.androidplatform.net','http://127.0.0.1:5173','http://localhost:5173'):
                return self.respond({'error':'Origin not allowed'},403)
            self.send_response(204);self.send_header('Access-Control-Allow-Methods','GET, POST, OPTIONS');self.send_header('Access-Control-Allow-Headers','Authorization, Content-Type');self.end_headers()
        def respond(self,data,status=200):
            body=json.dumps(data,ensure_ascii=False).encode();self.send_response(status);self.send_header('Content-Type','application/json; charset=utf-8');self.send_header('Cache-Control','no-store');self.send_header('Content-Length',str(len(body)));self.end_headers();self.wfile.write(body)
        def authorized(self):return secrets.compare_digest(self.headers.get('Authorization',''),'Bearer '+secret)
        def do_GET(self):
            url=urlparse(self.path)
            if url.path=='/api/health':return self.respond({'ok':True,'trusted':trusted,'version':'0.1.0'})
            if url.path.startswith('/api/'):
                if not self.authorized():return self.respond({'error':'Authentication required'},401)
                if url.path=='/api/doctor':return self.respond(doctor())
                if url.path=='/api/capabilities':return self.respond(json.loads((ROOT/'capabilities.json').read_text(encoding='utf-8')))
                if url.path.startswith('/api/runs/'):
                    run=runner.runs.get(url.path.split('/')[-1])
                    if not run:return self.respond({'error':'Unknown run'},404)
                    with runner.lock:
                        after=int(parse_qs(url.query).get('after',['-1'])[0]);data=dict(run['data']);data['events']=data['events'][after+1:after+257]
                        data['eventCount']=len(run['data']['events'])
                    return self.respond(data)
                return self.respond({'error':'Not found'},404)
            if url.path=='/':self.path='/index.html'
            super().do_GET()
        def do_POST(self):
            if not self.authorized():return self.respond({'error':'Authentication required'},401)
            try:
                length=int(self.headers.get('Content-Length','0'))
                if length<0 or length>2_000_000:raise ValueError('Request quota')
                data=json.loads(self.rfile.read(length))
                if self.path=='/api/runs':return self.respond({'runId':runner.start(data)},201)
                if self.path.startswith('/api/control/'):
                    runner.control(self.path.split('/')[-1],data);return self.respond({'ok':True})
                if self.path=='/api/analyze':return self.respond(analyze(data['source'],data.get('language','python')))
                return self.respond({'error':'Unknown endpoint'},404)
            except PermissionError as e:return self.respond({'error':str(e)},403)
            except Exception as e:return self.respond({'error':str(e)},400)
    server=ThreadingHTTPServer((host,port),Handler)
    if cert:
        context=ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER);context.load_cert_chain(cert,key);server.socket=context.wrap_socket(server.socket,server_side=True)
    server.runner=runner;server.token=secret
    return server
