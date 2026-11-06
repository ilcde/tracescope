import {setStandardLibraries} from './instrument';
import {standardLibraries} from './stdlib';
setStandardLibraries(standardLibraries);
import {runQuickJS} from './quickjs';
self.onmessage=async(event:MessageEvent)=>{try{const {source,language,stdin,benchmark,files,entry}=event.data;const trace=await runQuickJS(source,language,stdin,benchmark,t=>self.postMessage({batch:t}),files,entry);self.postMessage({trace})}catch(error){self.postMessage({error:String(error)})}};
