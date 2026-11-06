import test from 'node:test';
import assert from 'node:assert/strict';
import {validateProject,fileLanguage} from '../src/project';
test('projects reject malformed paths, oversized content and invalid configuration',()=>{
 const base={schema:'tracescope-project/1',language:'python',entry:'main.py',files:{'main.py':'import helper','helper.py':'value=21'}};
 assert.equal(validateProject(base).files['helper.py'],'value=21');
 for(const files of [{'../main.py':'x'},{'C:/main.py':'x'},{'main.py':{}},{'main.py':'x'.repeat(100001)}])assert.throws(()=>validateProject({...base,files}));
 assert.throws(()=>validateProject({...base,config:{args:'not an array'}}));
 assert.equal(fileLanguage('styles.css','html'),'css');
});
