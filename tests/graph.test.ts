import test from 'node:test';
import assert from 'node:assert/strict';
import {observationGraph} from '../src/graph';
import type {TraceEvent,Value} from '../src/model';
test('network graph preserves identities, cycles, types and visible budgets',()=>{
 const object:Value={type:'list',value:'list[1]',identity:'42',state:'available',children:{'0':{type:'list',value:'@42',identity:'42',state:'available'}}};
 const event={function:'main',frame:'f1',values:{a:object,b:{type:'list',value:'@42',identity:'42',state:'available'}},delta:{set:{a:object},remove:[]}} as unknown as TraceEvent;
 const graph=observationGraph(event);assert.equal(graph.nodes.filter(n=>n.id==='object:42').length,1);assert.equal(graph.edges.filter(e=>e.to==='object:42').length,3);assert.ok(graph.nodes.every(n=>n.value.type));assert.ok(observationGraph(event,2).omitted>0);
});
test('native aggregate fields expand without inventing object identities',()=>{
 const pair:Value={type:'Pair',value:'{2 fields}',state:'available',children:{public:{type:'C++ access group',value:'{2 fields}',state:'available',children:{right:{type:'int',value:'21',state:'available'}}}}};
 const event={function:'main',frame:'f1',values:{pair},delta:{set:{pair},remove:[]}} as unknown as TraceEvent;
 const graph=observationGraph(event);assert.ok(graph.nodes.some(n=>n.name==='right'&&n.value.value==='21'));assert.equal(graph.nodes.filter(n=>n.kind==='object').length,0);assert.equal(graph.edges.filter(e=>e.relation==='contains').length,2);
});
