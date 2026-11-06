// Bundle TypeScript's actual version-pinned standard declarations for offline checking.
const raw=import.meta.glob('../../node_modules/typescript/lib/lib.*.d.ts',{eager:true,query:'?raw',import:'default'}) as Record<string,string>;
export const standardLibraries=Object.fromEntries(Object.entries(raw).map(([path,source])=>[path.split('/').at(-1)!,source]));
