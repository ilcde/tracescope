import type {Language} from './model';
import {preferences} from './preferences';
export interface Project {schema:'tracescope-project/1';language:Language;entry:string;files:Record<string,string>;activeFile?:string;config?:{stdin?:string;args?:string[];env?:Record<string,string>;mainClass?:string}}
const extensions:Record<string,Language>={py:'python',js:'javascript',mjs:'javascript',ts:'typescript',java:'java',kt:'kotlin',c:'c',h:'c',cpp:'cpp',cc:'cpp',cxx:'cpp',hpp:'cpp',rs:'rust',html:'html',css:'css',s:'assembly',asm:'assembly'};
export function fileLanguage(name:string,fallback:Language):Language{return extensions[name.split('.').pop()?.toLowerCase()||'']||fallback}
export function validateProject(value:unknown):Project{
 const p=value as Project;
 if(!p||p.schema!=='tracescope-project/1'||!Object.values(extensions).includes(p.language)||typeof p.entry!=='string'||!p.files||Array.isArray(p.files)||typeof p.files!=='object')throw Error('Invalid project');
 let bytes=0;const entries=Object.entries(p.files);if(!entries.length||entries.length>64)throw Error('Project file quota (1–64 files)');
 for(const [name,source]of entries){if(!name||name.startsWith('/')||/[\\:\0]/.test(name)||name.split('/').some(part=>!part||['.','..','.git'].includes(part)||part.startsWith('.env'))||typeof source!=='string')throw Error('Invalid project path or source');const length=new TextEncoder().encode(source).length;bytes+=length;if(length>100000)throw Error('Each source file must be at most 100 KB')}
 if(bytes>1000000)throw Error('Project exceeds 1 MB');if(!Object.hasOwn(p.files,p.entry))throw Error('Project entry file is missing');
 if(p.config){if(typeof p.config!=='object'||(p.config.stdin!==undefined&&typeof p.config.stdin!=='string')||(p.config.mainClass!==undefined&&typeof p.config.mainClass!=='string')||(p.config.args!==undefined&&(!Array.isArray(p.config.args)||p.config.args.some(v=>typeof v!=='string')))||(p.config.env!==undefined&&(!p.config.env||Array.isArray(p.config.env)||typeof p.config.env!=='object'||Object.entries(p.config.env).some(([k,v])=>!k||typeof v!=='string'))))throw Error('Invalid project run configuration')}
 return p;
}
export function loadProject():Project|null{try{return validateProject(JSON.parse(preferences.getItem('tracescope-project')||'null'))}catch{return null}}
