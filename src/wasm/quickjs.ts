import {getQuickJS} from 'quickjs-emscripten';
import {addEvent,emptyTrace,hash,type Trace} from '../model';
import {instrument} from './instrument';

const PRELUDE=String.raw`
const __tscopeIds=new WeakMap();let __tscopeNext=1;
const __tscopeProxies=new WeakSet();const __tscopeProxy=Proxy;const __tscopeRevocable=Proxy.revocable;
globalThis.Proxy=new __tscopeProxy(__tscopeProxy,{construct(target,args){const p=new target(...args);__tscopeProxies.add(p);return p;}});
Proxy.revocable=(...args)=>{const pair=__tscopeRevocable(...args);__tscopeProxies.add(pair.proxy);return pair;};
function __tscopeValue(v,seen=new Set(),depth=0){
 const type=v===null?'null':typeof v;
 if(v===null||type==='undefined')return {type,value:String(v),state:'available'};
 if(type==='bigint')return {type,value:v.toString(),state:'available',encoding:'decimal'};
 if(type==='number'||type==='boolean'||type==='string')return {type,value:String(v).slice(0,300),state:type==='string'&&v.length>300?'truncated':'available'};
 if(type==='function'||type==='symbol')return {type,value:'<'+type+'>',state:'uncaptured'};
 if(__tscopeProxies.has(v))return {type:'Proxy',value:'<uncaptured>',state:'uncaptured'};
 if(!__tscopeIds.has(v))__tscopeIds.set(v,String(__tscopeNext++));const identity=__tscopeIds.get(v);
 const out={type:Array.isArray(v)?'Array':'object',value:'@'+identity,identity,state:'available'};
 if(seen.has(v))return {...out,relation:'aliases'};if(depth>=3)return {...out,state:'truncated'};seen.add(v);
 const props=Object.getOwnPropertyDescriptors(v);out.children={};let count=0;
 for(const [key,descriptor] of Object.entries(props)){if(key==='length'&&Array.isArray(v)){out.length=descriptor.value;continue;}if(++count>32){out.state='truncated';break;}out.children[key]=('value' in descriptor)?__tscopeValue(descriptor.value,seen,depth+1):{type:'accessor',value:'<not invoked>',state:'uncaptured'};}
 return out;
}
function __tscope(line,column,fn,bindings,kind){const values={};for(const [name,get] of bindings){try{values[name]=__tscopeValue(get());}catch{values[name]={type:'unknown',value:'<uninitialized>',state:'uninitialized'};}}__tscopeEmit(JSON.stringify({kind,phase:kind==='snapshot'?'observed':'before',line,column,function:fn,values}));}
globalThis.console={log:(...args)=>__tscopeEmit(JSON.stringify({kind:'io',line:0,phase:'observed',values:{},output:args.map(v=>{const s=__tscopeValue(v);return s.type==='object'||s.type==='Array'?JSON.stringify(s):s.value}).join(' ')+'\n'}))};
globalThis.input=()=>__tscopeInput();
`;
export async function runQuickJS(source:string,language:'javascript'|'typescript',stdin='',benchmark=false,onBatch?:(t:Trace)=>void){
  const trace=await emptyTrace(language,source);const compilation=performance.now();const transformed=instrument(source,language==='typescript',!benchmark);trace.metrics.compileMs=performance.now()-compilation;
  trace.diagnostics=transformed.diagnostics;if(transformed.diagnostics.length){trace.status='failed';return trace}
  trace.buildHash=await hash(transformed.code);trace.artifacts=[{kind:'generated JavaScript',label:'TypeScript 5.9.2 → ES2020 + trace hooks',instructions:[],text:transformed.code,buildHash:trace.buildHash}];
  trace.limitations=['Actual QuickJS VM running in WASM. Statement instrumentation is not WASM instruction stepping. No Node, network, filesystem or browser globals.','Snapshots before statements; unbraced loop bodies and expression substeps are not individually observed. Known Proxy objects and accessors are not inspected.'];
  const init=performance.now();const engine=await getQuickJS();trace.metrics.vmInitMs=performance.now()-init;const vm=engine.newContext();
  vm.runtime.setMemoryLimit(64*1024*1024);vm.runtime.setMaxStackSize(1024*1024);
  const start=performance.now();vm.runtime.setInterruptHandler(()=>performance.now()-start>4000||trace.events.length>=3000);
  let output=0;const lines=stdin.split('\n');let inputIndex=0;
  const emit=vm.newFunction('__tscopeEmit',arg=>{const event=JSON.parse(vm.getString(arg));output+=(event.output||'').length;if(output>65536||trace.events.length>=3000)throw Error('Trace/output quota');addEvent(trace,event,start);if(trace.events.length%100===0)onBatch?.(trace);});vm.setProp(vm.global,'__tscopeEmit',emit);emit.dispose();
  const input=vm.newFunction('__tscopeInput',()=>vm.newString(lines[inputIndex++]??''));vm.setProp(vm.global,'__tscopeInput',input);input.dispose();
  try{
    const setup=vm.evalCode(PRELUDE);if(setup.error){const error=vm.dump(setup.error);setup.error.dispose();throw Error(JSON.stringify(error));}setup.value.dispose();
    const result=vm.evalCode(transformed.code,trace.filename);
    if(result.error){const error=vm.dump(result.error);result.error.dispose();throw Error(JSON.stringify(error));}result.value.dispose();
    while(vm.runtime.hasPendingJob()){const pending=vm.runtime.executePendingJobs(1);if(pending.error){const error=vm.dump(pending.error);pending.error.dispose();throw Error(JSON.stringify(error));}}
    trace.status='completed';
  }catch(error){trace.status=performance.now()-start>=4000||trace.events.length>=3000?'truncated':'failed';trace.diagnostics.push({message:String(error)});addEvent(trace,{kind:'exception',exception:String(error),phase:'observed'},start)}
  finally{trace.metrics.executionMs=performance.now()-start;trace.metrics.measurement=benchmark?'Separate VM execution without statement hooks; console bridge overhead remains':'instrumented WASM VM wall time';trace.metrics.eventCount=trace.events.length;vm.dispose();}
  return trace;
}
