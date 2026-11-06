import {spawn,execFileSync} from 'node:child_process';
import path from 'node:path';
import fs from 'node:fs/promises';
import assert from 'node:assert/strict';
import {chromium} from '@playwright/test';
const executable=path.resolve('packages/TraceScope-Windows/TraceScope.exe');
const child=spawn(executable,['desktop'],{env:{...process.env,TRACESCOPE_DATA_DIR:path.resolve('.runs/windows-ui'),WEBVIEW2_ADDITIONAL_BROWSER_ARGUMENTS:'--remote-debugging-port=9224'},stdio:'ignore',windowsHide:true});
let browser;
try{
 const deadline=Date.now()+45000;
 for(;;){try{const info=await fetch('http://127.0.0.1:9224/json/version');if(info.ok)break}catch{}if(Date.now()>deadline)throw Error('Packaged WebView2 did not start');await new Promise(r=>setTimeout(r,300))}
 browser=await chromium.connectOverCDP('http://127.0.0.1:9224');const page=browser.contexts()[0].pages()[0];
 await page.getByRole('button',{name:'Run & trace'}).click();await page.waitForFunction(()=>document.querySelector('.status-label')?.textContent?.includes('Completed'),{timeout:30000});
 const timeline=page.getByRole('slider',{name:'Execution timeline'});await timeline.fill(await timeline.getAttribute('max'));
 assert.ok(await page.locator('.neuron-node').count()>3);
 await page.getByRole('button',{name:'Fullscreen diagram',exact:true}).click();await page.getByTitle('Fit diagram',{exact:true}).click();
 assert.equal(await page.locator('.source-panel').isVisible(),false);
 await page.screenshot({path:'evidence/windows-native-fullscreen.png'});
 await fs.writeFile('evidence/windows-desktop.json',JSON.stringify({status:'passed',runtime:'bundled CPython / native WebView2',javascriptExecution:true,neuronGraph:true,fullscreen:true},null,2));
 console.log('Packaged Windows WebView2: execution, neuron graph and fullscreen passed');
}finally{
 if(browser)await browser.close();
 if(child.pid)try{execFileSync('taskkill',['/PID',String(child.pid),'/T','/F'],{stdio:'ignore',windowsHide:true})}catch{}
}
