import {useEffect,useMemo,useState} from 'react';
import {observationGraph} from './graph';
import type {TraceEvent,Value} from './model';
import type {Key} from './i18n';
export function NeuronGraph({event,onSelect,t}:{event:TraceEvent;onSelect:(name:string,value:Value)=>void;t:(key:Key)=>string}){
 const [compact,setCompact]=useState(()=>matchMedia('(max-width:680px)').matches);
 useEffect(()=>{const media=matchMedia('(max-width:680px)');const change=()=>setCompact(media.matches);media.addEventListener('change',change);return()=>media.removeEventListener('change',change)},[]);
 const graph=useMemo(()=>{const data=observationGraph(event);if(compact){data.nodes=data.nodes.map((n,i)=>({...n,x:30,y:30+i*122}));data.width=330;data.height=data.nodes.length*122+40}return data},[event,compact]);const byId=new Map(graph.nodes.map(n=>[n.id,n]));
 return <><p className="graph-explanation">{t('neuronHelp')}</p><svg className="neuron-graph" width={graph.width} height={graph.height} role="group" aria-label={t('neuron')}>
  <defs><marker id="graph-arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10Z" fill="currentColor"/></marker></defs>
  {graph.edges.map((edge,i)=>{const a=byId.get(edge.from)!,b=byId.get(edge.to)!;const x1=a.x+270,y1=a.y+44,x2=b.x,y2=b.y+44;const same=a.id===b.id;return <g key={i} className={'neuron-edge '+edge.relation}><title>{a.name+' '+t(edge.relation)+' '+b.name}</title><path d={compact?`M${a.x} ${y1} C${3+i%3*6} ${y1},${3+i%3*6} ${y2},${b.x} ${y2}`:same?`M${x1} ${y1} c80 -100 -350 -100 -270 0`:`M${x1} ${y1} C${x1+55} ${y1},${x2-55} ${y2},${x2} ${y2}`} markerEnd="url(#graph-arrow)"/>{!compact&&<text x={same?a.x+110:(x1+x2)/2} y={same?a.y-14:(y1+y2)/2-9}>{t(edge.relation)}</text>}</g>})}
  {graph.nodes.map(node=><g key={node.id} className={'neuron-node '+node.kind+(node.changed?' changed':'')} transform={`translate(${node.x},${node.y})`} role="button" tabIndex={0} aria-label={`${node.name}: ${node.value.type}, ${node.value.value}`} onClick={()=>onSelect(node.name.replace(/^value:/,''),node.value)} onKeyDown={e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();onSelect(node.name,node.value)}}}>
   <rect width="270" height="88" rx="17"/><circle cx="0" cy="44" r="5"/><circle cx="270" cy="44" r="5"/><text x="18" y="25" className="graph-name">{node.name.slice(0,28)}</text><text x="18" y="46" className="graph-type">{node.value.type.slice(0,36)}</text><text x="18" y="71" className="graph-value">{node.value.value.slice(0,28)}</text><title>{node.name+' : '+node.value.type+'\n'+node.value.value}</title>
  </g>)}
 </svg>{graph.omitted>0&&<p role="status">{t('graphLimit')} {graph.omitted}</p>}</>;
}
