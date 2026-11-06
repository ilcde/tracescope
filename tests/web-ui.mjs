import {chromium} from '@playwright/test';
import {createServer} from 'node:http';
import fs from 'node:fs/promises';
import path from 'node:path';
import assert from 'node:assert/strict';
await fs.mkdir('evidence',{recursive:true});
const root=path.resolve('dist');
const mime={'.html':'text/html','.js':'text/javascript','.css':'text/css','.wasm':'application/wasm','.json':'application/json'};
const server=createServer(async(req,res)=>{try{const name=decodeURIComponent((req.url||'/').split('?')[0]).replace(/^\/tracescope\//,'');const file=path.resolve(root,name||'index.html');if(!file.startsWith(root+path.sep))throw Error('path');const data=await fs.readFile(file);res.writeHead(200,{'Content-Type':mime[path.extname(file)]||'application/octet-stream'});res.end(data)}catch{res.writeHead(404);res.end()}});
await new Promise(r=>server.listen(0,'127.0.0.1',r));
const options={headless:true};if(process.platform==='win32')options.executablePath='C:/Program Files/Google/Chrome/Application/chrome.exe';
const browser=await chromium.launch(options);
try{
 const page=await browser.newPage({viewport:{width:1600,height:1000}});const errors=[];page.on('pageerror',e=>errors.push(String(e)));
 await page.goto(`http://127.0.0.1:${server.address().port}/tracescope/`);
 async function run(){await page.getByRole('button',{name:'Run & trace'}).click();await page.waitForFunction(()=>document.querySelector('.status-label')?.textContent?.includes('Completed'),{timeout:30000});const timeline=page.getByRole('slider',{name:'Execution timeline'});await timeline.fill(await timeline.getAttribute('max'))}
 await run();assert.ok(await page.locator('.neuron-node').count()>3);assert.ok(await page.locator('.neuron-edge').count()>2);
 await page.screenshot({path:'evidence/web-network.png'});
 await page.getByRole('button',{name:'Fullscreen diagram',exact:true}).click();assert.equal(await page.locator('.source-panel').isVisible(),false);assert.ok((await page.locator('.visual-panel').boundingBox()).width>1500);
 await page.getByTitle('Fit diagram',{exact:true}).click();await page.screenshot({path:'evidence/web-fullscreen.png'});
 await page.getByRole('button',{name:'Exit fullscreen',exact:true}).click();assert.equal(await page.locator('.source-panel').isVisible(),true);
 await page.getByLabel('Language',{exact:true}).selectOption('typescript');
 await page.locator('input[type=file]').first().setInputFiles({name:'main.ts',mimeType:'text/plain',buffer:Buffer.from('const items: Map<string, number> = new Map([["a", 7]]);\nconst result = Array.from(items.values()).reduce((a, b) => a + b, 0);\nconsole.log(result);')});
 await run();await page.getByRole('button',{name:'Console',exact:true}).click();assert.match(await page.locator('.console-output').innerText(),/7/);
 for(const language of ['html','css']){await page.getByLabel('Language',{exact:true}).selectOption(language);await run();assert.ok(await page.frameLocator('iframe').locator('h1').isVisible())}
 await page.getByLabel('Language',{exact:true}).selectOption('javascript');await run();await page.setViewportSize({width:393,height:873});await page.getByTitle('Language',{exact:true}).click();assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);await page.screenshot({path:'evidence/web-phone-vi.png'});
 assert.deepEqual(errors,[]);await fs.writeFile('evidence/web-ui.json',JSON.stringify({status:'passed',network:true,fullscreen:true,typescriptStandardLibrary:true,html:true,css:true,phoneOverflow:false,errors},null,2));
 console.log('Web UI: network edges, fullscreen, full TypeScript standard declarations, HTML/CSS and Vietnamese phone checks passed');
}finally{await browser.close();await new Promise(r=>server.close(r))}
