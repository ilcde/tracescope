import type {TraceEvent,Value} from './model';
export interface GraphNode {id:string;name:string;value:Value;x:number;y:number;kind:'scope'|'value'|'object';changed:boolean}
export interface GraphEdge {from:string;to:string;relation:'scope'|'references'|'contains'}
export function observationGraph(event:TraceEvent,limit=100){
 const nodes:GraphNode[]=[],edges:GraphEdge[]=[];const objects=new Map<string,GraphNode>();const expanded=new Set<string>();let omitted=0;
 const columns=[0,0,0,0];
 function add(id:string,name:string,value:Value,column:number,kind:GraphNode['kind'],changed=false){if(nodes.length>=limit){omitted++;return null}const node={id,name,value,x:45+column*330,y:45+columns[column]++*122,kind,changed};nodes.push(node);return node}
 const scope=add('scope',event.function,{type:'execution frame',value:event.frame,state:'available'},0,'scope');
 function object(v:Value,depth:number):GraphNode|null{
  if(!v.identity)return null;let node=objects.get(v.identity);
  if(!node){node=add('object:'+v.identity,'@'+v.identity,v,Math.min(3,depth),'object')||undefined;if(!node)return null;objects.set(v.identity,node)}
  if(v.children&&!expanded.has(v.identity)){expanded.add(v.identity);node.value=v;for(const [key,child]of Object.entries(v.children)){
   if(child.identity){const target=object(child,depth+1);if(target)edges.push({from:node.id,to:target.id,relation:'references'})}
   else{const target=add(node.id+'.'+key,key,child,Math.min(3,depth+1),'value');if(target)edges.push({from:node.id,to:target.id,relation:'contains'})}
  }}return node;
 }
 for(const [name,value]of Object.entries(event.values).filter(([,v])=>v.type!=='function')){const node=add('value:'+name,name,value,1,'value',!!event.delta.set[name]);if(!node)continue;if(scope)edges.push({from:scope.id,to:node.id,relation:'scope'});const target=object(value,2);if(target)edges.push({from:node.id,to:target.id,relation:'references'})}
 return {nodes,edges,omitted,width:Math.max(760,...nodes.map(n=>n.x+300)),height:Math.max(400,...nodes.map(n=>n.y+110))};
}
