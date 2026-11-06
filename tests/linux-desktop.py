"""Exercise an installed GTK/WebKit window on an Xvfb display in CI."""
import json, os, threading, time, traceback, tempfile, struct, zlib
from pathlib import Path
import webview
from tracescope.service import make_server

evidence=Path(os.environ['TRACESCOPE_EVIDENCE']);evidence.mkdir(parents=True,exist_ok=True)
server=make_server('127.0.0.1',0,False,None)
threading.Thread(target=server.serve_forever,daemon=True).start()
window=webview.create_window('TraceScope Linux acceptance',f'http://127.0.0.1:{server.server_port}/#token={server.token}',width=1440,height=950)
result={'status':'failed','renderer':'GTK / WebKit2 4.1','display':'Xvfb X11','securityAcceptance':False}
profile=tempfile.TemporaryDirectory(prefix='tracescope-webview-test-')

def check():
    try:
        assert window.events.loaded.wait(30),'WebKit page load timeout'
        deadline=time.monotonic()+60
        while time.monotonic()<deadline:
            ready=window.evaluate_js('!!document.querySelector(".run-button")')
            if ready is True:break
            time.sleep(.2)
        else:raise AssertionError('Application did not render: '+str(window.evaluate_js('document.body.innerText')))
        window.evaluate_js('document.querySelector(".run-button").click()')
        while time.monotonic()<deadline:
            if window.evaluate_js('document.querySelector(".status-label")?.textContent.includes("Completed")') is True:break
            time.sleep(.2)
        else:raise AssertionError('Local JavaScript execution did not complete')
        # Click timeline end using the native range setter so React observes it.
        window.evaluate_js('''(()=>{const s=document.querySelector('input[type="range"][aria-label="Execution timeline"]');Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set.call(s,s.max);s.dispatchEvent(new Event('input',{bubbles:true}));s.dispatchEvent(new Event('change',{bubbles:true}));})()''')
        time.sleep(.5)
        assert window.evaluate_js('document.querySelectorAll(".neuron-node").length')>0
        window.evaluate_js('document.querySelector(`button[title="Fullscreen diagram"]`).click()')
        time.sleep(.5)
        assert window.evaluate_js('getComputedStyle(document.querySelector(".source-panel")).display')=='none'
        from gi.repository import Gdk, GLib
        captured=threading.Event();capture_errors=[]
        def screenshot():
            try:
                root=Gdk.get_default_root_window();pixbuf=Gdk.pixbuf_get_from_window(root,0,0,root.get_width(),root.get_height())
                # Encode the actual X11 pixels directly. Fedora's PNG plugin
                # starts an additional sandbox that is unavailable in CI.
                width,height=pixbuf.get_width(),pixbuf.get_height();channels=pixbuf.get_n_channels();stride=pixbuf.get_rowstride();pixels=pixbuf.get_pixels()
                def chunk(kind,data):return struct.pack('!I',len(data))+kind+data+struct.pack('!I',zlib.crc32(kind+data)&0xffffffff)
                rows=b''.join(b'\0'+pixels[y*stride:y*stride+width*channels] for y in range(height))
                png=b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('!IIBBBBB',width,height,8,6 if channels==4 else 2,0,0,0))+chunk(b'IDAT',zlib.compress(rows))+chunk(b'IEND',b'')
                (evidence/'linux-native-fullscreen.png').write_bytes(png)
            except Exception:capture_errors.append(traceback.format_exc())
            finally:captured.set()
            return False
        GLib.idle_add(screenshot);assert captured.wait(10);assert not capture_errors,capture_errors
        assert (evidence/'linux-native-fullscreen.png').stat().st_size>1000
        result.update(status='passed',javascriptExecution=True,networkDiagram=True,fullscreen=True)
    except Exception:
        result['error']=traceback.format_exc()
        try:result['page']=window.evaluate_js('({url:location.origin+location.pathname,text:document.body.innerText,html:document.body.innerHTML.slice(0,4000)})')
        except Exception:pass
    finally:
        (evidence/'linux-desktop.json').write_text(json.dumps(result,indent=2));window.destroy()

threading.Timer(90,lambda:os._exit(80)).start()
webview.start(check,gui='gtk',private_mode=False,storage_path=profile.name);server.shutdown()
print(json.dumps(result,indent=2),flush=True)
os._exit(0 if result['status']=='passed' else 1)
