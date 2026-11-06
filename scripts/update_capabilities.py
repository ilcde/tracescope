import json
from pathlib import Path
root=Path(__file__).resolve().parent.parent;p=root/'capabilities.json';data=json.loads(p.read_text(encoding='utf-8'))
for adapter in data['adapters']:
    evidence={'javascript':['evidence/javascript-input-5.json','evidence/javascript-input-8.json','evidence/ui-smoke.json'],'typescript':['evidence/typescript-input-5.json','evidence/typescript-input-8.json'],'rust':['evidence/rust.json','evidence/rust-modified.json'],'html':['evidence/ui-smoke.json','evidence/html.png'],'css':['evidence/ui-smoke.json']}
    adapter['evidence']=evidence.get(adapter['id'],adapter['evidence'])
    if all((root/f).exists() for f in adapter['evidence']):adapter['verification']='tested'
for platform in data['platforms']:
    platform['verification']='tested' if platform['id'] in ('windows','android') else 'untested'
    if platform['id'] not in ('windows','android'):platform['implementation']='blocked'
data['platformNote']='Windows native window and packaged Python execution tested. Android 16 emulator local WASM tested; physical-device and paired TLS acceptance untested. Fedora acceptance blocked: user confirmed no host/VM. Native trusted mode is not a sandbox.'
data['platformNoteVi']='Đã kiểm thử cửa sổ gốc Windows và Python đóng gói. Đã kiểm thử WASM cục bộ trên máy ảo Android 16; chưa kiểm chứng thiết bị thật/ghép nối TLS. Fedora bị chặn vì không có máy/VM. Chế độ tin cậy không phải sandbox.'
data['isaEvidence']=[{'profile':profile,'implementation':'limited','verification':'tested','execution':'Unicorn 2.1.4','assembler':'Zig/LLVM' if profile.startswith('rv') else 'Keystone 0.9.2','endianness':'little','abi':'freestanding','evidence':'evidence/isa-'+profile+'.json'} for profile in ['x86-16','x86-32','x86-64','arm32','thumb','arm64','rv32','rv64']]
p.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
