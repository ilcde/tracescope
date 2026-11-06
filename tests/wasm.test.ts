import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import {runQuickJS} from '../src/wasm/quickjs';
import {validateTrace,playbackStep} from '../src/model';
import {instrument} from '../src/wasm/instrument';
import {fitGrowth} from '../src/experiments';
import {en,vi} from '../src/i18n';
await fs.mkdir('evidence',{recursive:true});
test('real project modules preserve source-file observations',async()=>{
 for(const language of ['javascript','typescript'] as const){const extension=language==='typescript'?'ts':'js';const entry='main.'+extension;const helper='helper.'+extension;const source='import {triple} from "./helper";\nconst result=triple(7);\nconsole.log(result);';const files={[entry]:source,[helper]:'export function triple(n'+(language==='typescript'?':number':'')+'){\n const value=n*3;\n return value;\n}'};const trace=await runQuickJS(source,language,'',false,undefined,files,entry);assert.equal(trace.status,'completed',JSON.stringify(trace.diagnostics));assert.equal(trace.events.filter(e=>e.output).map(e=>e.output).join(''),'21\n');assert.ok(trace.events.some(e=>e.file===helper&&e.values.value?.value==='21'));}
});

test('real WASM execution: changed input, exact bigint, baseline and pure replay',async()=>{
 const source='const n=Number(input()); let sum=0; for(let i=0;i<n;i++){sum+=i;} const huge=9007199254740993n; console.log(sum,huge);';
 for(const language of ['javascript','typescript'] as const){const outputs=[];for(const n of ['5','8']){const trace=await runQuickJS(source,language,n);assert.equal(trace.status,'completed',JSON.stringify(trace.diagnostics));await validateTrace(trace);const out=trace.events.filter(e=>e.output).map(e=>e.output).join('');const plain=await runQuickJS(source,language,n,true);assert.equal(out,plain.events.filter(e=>e.output).map(e=>e.output).join(''));outputs.push(out);assert(out.includes('9007199254740993'));const original=JSON.stringify(trace);for(let i=0;i<trace.events.length;i++)playbackStep(trace.events,i,'back');assert.equal(JSON.stringify(trace),original);await fs.writeFile(`evidence/${language}-input-${n}.json`,JSON.stringify(trace,null,2))}assert.notEqual(outputs[0],outputs[1]);}
});
test('closures, aliases, cycles, getters, promises, short circuit and exceptions',async()=>{
 const source=`let calls=0; const a={x:1};a.self=a;const b=a;Object.defineProperty(a,'trap',{get(){calls++;return 9;}});function make(x){return ()=>x+1;}const f=make(4);let answer=f();false && calls++;Promise.resolve(1).then(x=>{answer+=x;console.log('async',answer);});console.log(calls);`;
 const trace=await runQuickJS(source,'javascript');assert.equal(trace.status,'completed',JSON.stringify(trace.diagnostics));const output=trace.events.filter(e=>e.output).map(e=>e.output).join('');assert.equal(output,'0\nasync 6\n');const v=trace.events.find(e=>e.values.a?.children?.trap&&e.values.b?.identity)?.values;assert(v);assert.equal(v.a.identity,v.b.identity);assert.equal(v.a.children?.self.identity,v.a.identity);assert.equal(v.a.children?.trap.state,'uncaptured');
 const bad=await runQuickJS('throw new Error("observed");','javascript');assert.equal(bad.status,'failed');assert(bad.events.some(e=>e.kind==='exception'));
});
test('TypeScript checker catches errors and preserves source locations',async()=>{const bad=await runQuickJS('const n: number="wrong";','typescript');assert.equal(bad.status,'failed');assert.equal(bad.events.length,0);const code='const x: number=1;\nconst y: number=x+1;\nconsole.log(y);';const trace=await runQuickJS(code,'typescript');assert.equal(trace.status,'completed');assert(trace.events.some(e=>e.line===3&&e.values.y.value==='2'))});
test('runaway scripts have a bounded interrupted trace',async()=>{const trace=await runQuickJS('let i=0;while(true){i++;}','javascript');assert(['failed','truncated'].includes(trace.status));assert(trace.events.length<=3001)});
test('locale keys and empirical fit',()=>{assert.deepEqual(Object.keys(en).sort(),Object.keys(vi).sort());const fit=fitGrowth([10,20,40,80].map(n=>({n,ms:2*n})));assert.equal(fit[0].name,'n');assert(fit[0].error<1e-12)});
