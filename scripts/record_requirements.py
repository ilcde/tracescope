"""Stable paragraph-level ledger; no requirement is silently discarded."""
import json,re
from pathlib import Path
root=Path(__file__).resolve().parent.parent
text=(root/'docs/PRODUCT-BRIEF.md').read_text(encoding='utf-8')
sections=re.split(r'^## (\d+)\. (.+)$',text,flags=re.M)
records=[]
for i in range(1,len(sections),3):
    number,title,body=sections[i:i+3]
    body=body.split('## Official implementation references')[0]
    paragraphs=[p.strip() for p in re.split(r'\n\s*\n',body) if p.strip()]
    for j,paragraph in enumerate(paragraphs,1):
        state='limited';verification='untested';reason='Partially addressed; the full paragraph has not passed acceptance. See scoped capability evidence.'
        if any(s in paragraph for s in ('Fedora is the primary','Test normal Fedora','representative Ubuntu/Debian')):
            state='blocked';reason='User confirmed no Fedora host/VM is available. Linux runtime and packaging acceptance cannot be established on this Windows host.'
        if any(s in paragraph for s in ('native JIT code only','Native JIT instruction','complete Kotlin/JVM path','Implement authenticated pairing')):
            reason='Baseline route exists, but the advanced requirements in this paragraph are not complete or verified.'
        if 'native JIT code only' in paragraph:state='unavailable'
        records.append({'id':f'TS-{int(number):02d}.{j:02d}','section':title,'requirement':paragraph,'implementation':state,'verification':verification,'accepted':False,'note':reason})
data={'schema':'tracescope-requirements/1','acceptance':'incomplete','source':'docs/PRODUCT-BRIEF.md','items':records}
(root/'requirements.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
rows=['# Requirements ledger','',f'{len(records)} stable paragraph-level requirements retained from the complete brief. **Product acceptance: incomplete.**','',
      'Implementation and verification are separate. `limited` means a useful subset exists, not that the paragraph is accepted. `untested` here means the complete paragraph has not passed acceptance; individual working baselines have actual evidence in `capabilities.json` and `evidence/`. Fedora blocking is based on the user confirming no host/VM is available.','',
      '## Delivered, individually verified slices','',
      '- All ten named language baselines have real execution/observation paths. Python, Java, Kotlin, C, C++, Rust, JavaScript and TypeScript have modified-source/input evidence. HTML/CSS use actual WASM syntax and browser rendering.','- Eight ISA/mode profiles pass register, memory, branch and call tests. x86-16 is real mode on a 386+ instruction set, not a claim of a cycle-accurate 8086 machine.','- Immutable replay, exact large integers, safe bounded object inspection, Python live pause/step, per-build native disassembly, optimized-out native values, measured phases, a conservative complexity subset, bilingual UI, Windows native window and Android emulator local WASM.','',
      '## Open completion gate','',
      'Multi-file/project build formats; true isolation of compilation and native execution; authenticated paired-device TLS acceptance; full DOM/event bridge; browser-native JS adapter; WASM/JIT instruction state; complete heap lifetimes, ownership and dependency graphs; conditional breakpoints/watchpoints; multi-thread causal reconstruction; all requested static complexity patterns; packaged Linux acceptance; physical Android/Poco testing and comprehensive accessibility/rendering budgets remain open.','']
section=None
for r in records:
    if r['section']!=section:section=r['section'];rows+=['## '+section,'']
    rows += [f"- [ ] **{r['id']}** — {r['implementation']} / {r['verification']}: "+r['requirement'].replace('\n',' '),'']
(root/'docs/REQUIREMENTS.md').write_text('\n'.join(rows),encoding='utf-8')
print(f'Retained {len(records)} requirements')
