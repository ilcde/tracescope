import {useEffect,useRef} from 'react';
import {EditorState,StateEffect,StateField,Compartment} from '@codemirror/state';
import {EditorView,Decoration,gutter,GutterMarker} from '@codemirror/view';
import {basicSetup} from 'codemirror';
import {python} from '@codemirror/lang-python';
import {javascript} from '@codemirror/lang-javascript';
import {syntaxHighlighting,HighlightStyle,StreamLanguage} from '@codemirror/language';
import {java} from '@codemirror/lang-java';
import {cpp} from '@codemirror/lang-cpp';
import {rust} from '@codemirror/lang-rust';
import {html} from '@codemirror/lang-html';
import {css} from '@codemirror/lang-css';
import {kotlin} from '@codemirror/legacy-modes/mode/clike';
import {gas} from '@codemirror/legacy-modes/mode/gas';
import {tags} from '@lezer/highlight';
import type {Language} from './model';
const active=StateEffect.define<number>();
const markerField=StateField.define({create:()=>Decoration.none,update(value,tr){value=value.map(tr.changes);for(const effect of tr.effects)if(effect.is(active)){const n=effect.value;value=n>0&&n<=tr.state.doc.lines?Decoration.set([Decoration.line({class:'executing-line'}).range(tr.state.doc.line(n).from)]):Decoration.none;}return value},provide:f=>EditorView.decorations.from(f)});
class Breakpoint extends GutterMarker{toDOM(){const el=document.createElement('span');el.textContent='●';el.className='breakpoint';return el}}
const breakEffect=StateEffect.define<number[]>();
const breakField=StateField.define<number[]>({create:()=>[],update(v,tr){for(const e of tr.effects)if(e.is(breakEffect))return e.value;return v}});
export function Editor({source,language,line,onChange,onCursor,breakpoints,onBreakpoint,font,readonly}:{source:string;language:Language;line:number;onChange:(s:string)=>void;onCursor:(n:number)=>void;breakpoints:number[];onBreakpoint:(n:number)=>void;font:number;readonly:boolean}){
 const container=useRef<HTMLDivElement>(null);const view=useRef<EditorView|null>(null);const callbacks=useRef({onChange,onCursor,onBreakpoint});callbacks.current={onChange,onCursor,onBreakpoint};const languageComp=useRef(new Compartment()),fontComp=useRef(new Compartment()),readonlyComp=useRef(new Compartment());
 const lang=()=>language==='python'?python():language==='javascript'||language==='typescript'?javascript({typescript:language==='typescript'}):language==='java'?java():language==='kotlin'?StreamLanguage.define(kotlin):language==='c'||language==='cpp'?cpp():language==='rust'?rust():language==='html'?html():language==='css'?css():StreamLanguage.define(gas);
 useEffect(()=>{if(!container.current)return;const v=new EditorView({parent:container.current,state:EditorState.create({doc:source,extensions:[basicSetup,markerField,breakField,gutter({class:'breakpoint-gutter',lineMarker:(v,line)=>v.state.field(breakField).includes(v.state.doc.lineAt(line.from).number)?new Breakpoint():null,initialSpacer:()=>new Breakpoint(),domEventHandlers:{mousedown:(v,line)=>{callbacks.current.onBreakpoint(v.state.doc.lineAt(line.from).number);return true}}}),languageComp.current.of(lang()),fontComp.current.of(EditorView.theme({'&':{fontSize:font+'px'}})),readonlyComp.current.of(EditorState.readOnly.of(readonly)),EditorView.lineWrapping,syntaxHighlighting(HighlightStyle.define([{tag:tags.keyword,color:'#c78ff1'},{tag:[tags.string,tags.special(tags.string)],color:'#b6ce88'},{tag:[tags.number,tags.bool],color:'#e5ad75'},{tag:tags.comment,color:'#71828c'},{tag:[tags.function(tags.variableName),tags.definition(tags.variableName)],color:'#7ecac3'},{tag:tags.typeName,color:'#e3c87d'}])),EditorView.updateListener.of(update=>{if(update.docChanged)callbacks.current.onChange(update.state.doc.toString());if(update.selectionSet)callbacks.current.onCursor(update.state.doc.lineAt(update.state.selection.main.head).number)})]})});view.current=v;return()=>v.destroy()},[]);
 useEffect(()=>{const v=view.current;if(v&&v.state.doc.toString()!==source)v.dispatch({changes:{from:0,to:v.state.doc.length,insert:source}})},[source]);
 useEffect(()=>{view.current?.dispatch({effects:languageComp.current.reconfigure(lang())})},[language]);
 useEffect(()=>{view.current?.dispatch({effects:[active.of(line),breakEffect.of(breakpoints),fontComp.current.reconfigure(EditorView.theme({'&':{fontSize:font+'px'}})),readonlyComp.current.reconfigure(EditorState.readOnly.of(readonly))]})},[line,breakpoints,font,readonly]);
 return <div ref={container} className="editor-host"/>;
}
