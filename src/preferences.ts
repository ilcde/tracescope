/** Preferences remain usable when a private/embedded browser disables storage. */
function storage(kind:'localStorage'|'sessionStorage'){
 const fallback=new Map<string,string>();
 return {
  getItem(key:string):string|null{try{return window[kind].getItem(key)??fallback.get(key)??null}catch{return fallback.get(key)??null}},
  setItem(key:string,value:string){fallback.set(key,value);try{window[kind].setItem(key,value)}catch{/* Export remains available; this browser session keeps the draft in memory. */}},
  removeItem(key:string){fallback.delete(key);try{window[kind].removeItem(key)}catch{}}
 };
}
export const preferences=storage('localStorage');
export const sessionPreferences=storage('sessionStorage');
