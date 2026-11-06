import ts from 'typescript';
// Node tests load libraries from the installed compiler; browsers use the bundled map.
let libraries:Record<string,string>|null=null;
export function setStandardLibraries(value:Record<string,string>){libraries=value}

export function instrument(source:string,typescript=false,enabled=true){
  const filename=typescript?'main.ts':'main.js';
  const file=ts.createSourceFile(filename,source,ts.ScriptTarget.ES2020,true,typescript?ts.ScriptKind.TS:ts.ScriptKind.JS);
  if(/\b__tscope\w*/.test(source))throw Error('Identifiers beginning __tscope are reserved for the tracer.');
  const diagnostics:{message:string;line:number}[]=[];
  const runtimeLib='declare var console:{log(...v:unknown[]):void}; declare function input():string;';
  if(typescript){
    const files:Record<string,ts.SourceFile>={[filename]:file,'runtime.d.ts':ts.createSourceFile('runtime.d.ts',runtimeLib,ts.ScriptTarget.ES2022,true)};
    const get=(n:string)=>{const key=n.replace(/\\/g,'/').split('/').at(-1)!;if(files[key])return files[key];const text=libraries?.[key]??ts.sys?.readFile?.(ts.getDefaultLibFilePath({}).replace(/[^/\\]+$/,'')+key);return text?files[key]=ts.createSourceFile(key,text,ts.ScriptTarget.ES2022,true):undefined};
    const host:ts.CompilerHost={getSourceFile:get,getDefaultLibFileName:()=> 'lib.es2022.d.ts',writeFile:()=>{},getCurrentDirectory:()=>'',getDirectories:()=>[],fileExists:n=>!!get(n),readFile:n=>get(n)?.text,getCanonicalFileName:n=>n,useCaseSensitiveFileNames:()=>true,getNewLine:()=> '\n'};
    const program=ts.createProgram([filename,'runtime.d.ts'],{target:ts.ScriptTarget.ES2022,strict:true,noEmit:true},host);
    for(const d of ts.getPreEmitDiagnostics(program))diagnostics.push({message:ts.flattenDiagnosticMessageText(d.messageText,'\n'),line:d.file&&d.start!==undefined?d.file.getLineAndCharacterOfPosition(d.start).line+1:0});
  }
  const scopes:string[][]=[];let fn='<script>';
  function binding(name:ts.BindingName):string[]{if(ts.isIdentifier(name))return[name.text];return name.elements.flatMap(e=>ts.isOmittedExpression(e)?[]:binding(e.name))}
  const transformer:ts.TransformerFactory<ts.SourceFile>=context=>{
    const f=context.factory;
    function hook(node:ts.Node,kind='line'):ts.Statement{const pos=file.getLineAndCharacterOfPosition(node.getStart(file));const names=[...new Set(scopes.flat())].filter(n=>n!=='__tscope');return f.createExpressionStatement(f.createCallExpression(f.createIdentifier('__tscope'),undefined,[f.createNumericLiteral(pos.line+1),f.createNumericLiteral(pos.character),f.createStringLiteral(fn),f.createArrayLiteralExpression(names.map(n=>f.createArrayLiteralExpression([f.createStringLiteral(n),f.createArrowFunction(undefined,undefined,[],undefined,f.createToken(ts.SyntaxKind.EqualsGreaterThanToken),f.createIdentifier(n))]))),f.createStringLiteral(kind)]))}
    function statements(nodes:ts.NodeArray<ts.Statement>):ts.Statement[]{return nodes.flatMap(node=>{const visited=ts.visitNode(node,visit) as ts.Statement;if(!enabled||ts.isFunctionDeclaration(node)||ts.isInterfaceDeclaration(node)||ts.isTypeAliasDeclaration(node)||ts.isImportDeclaration(node)||ts.isEmptyStatement(node)||ts.isExpressionStatement(node)&&ts.isStringLiteral(node.expression))return[visited];return[hook(node),visited]})}
    function visit(node:ts.Node):ts.VisitResult<ts.Node>{
      if(ts.isFunctionLike(node)&&'body' in node&&node.body){const old=fn;fn=node.name&&ts.isIdentifier(node.name)?node.name.text:'<closure>';scopes.push(node.parameters.flatMap(p=>binding(p.name)));const value=ts.visitEachChild(node,visit,context);scopes.pop();fn=old;return value}
      if(ts.isForStatement(node)||ts.isForOfStatement(node)||ts.isForInStatement(node)){const init=node.initializer;scopes.push(init&&ts.isVariableDeclarationList(init)?init.declarations.flatMap(d=>binding(d.name)):[]);let value=ts.visitEachChild(node,visit,context);if(enabled&&ts.isForStatement(value)&&!ts.isBlock(value.statement))value=f.updateForStatement(value,value.initializer,value.condition,value.incrementor,f.createBlock([hook(node.statement),value.statement],true));else if(enabled&&ts.isForOfStatement(value)&&!ts.isBlock(value.statement))value=f.updateForOfStatement(value,value.awaitModifier,value.initializer,value.expression,f.createBlock([hook(node.statement),value.statement],true));else if(enabled&&ts.isForInStatement(value)&&!ts.isBlock(value.statement))value=f.updateForInStatement(value,value.initializer,value.expression,f.createBlock([hook(node.statement),value.statement],true));scopes.pop();return value}
      if(ts.isSourceFile(node)||ts.isBlock(node)){
        const names=node.statements.flatMap(s=>ts.isVariableStatement(s)?s.declarationList.declarations.flatMap(d=>binding(d.name)):ts.isFunctionDeclaration(s)&&s.name?[s.name.text]:[]);scopes.push(names);
        const result=statements(node.statements);if(enabled&&ts.isSourceFile(node))result.push(hook(node.statements.at(-1)||node,'snapshot'));scopes.pop();
        return ts.isSourceFile(node)?f.updateSourceFile(node,result):f.updateBlock(node,result)
      }
      if(ts.isWhileStatement(node)){const body=ts.visitNode(node.statement,visit) as ts.Statement;return f.updateWhileStatement(node,ts.visitNode(node.expression,visit) as ts.Expression,enabled&&!ts.isBlock(body)?f.createBlock([hook(node.statement),body],true):body)}
      if(ts.isDoStatement(node)){const body=ts.visitNode(node.statement,visit) as ts.Statement;return f.updateDoStatement(node,enabled&&!ts.isBlock(body)?f.createBlock([hook(node.statement),body],true):body,ts.visitNode(node.expression,visit) as ts.Expression)}
      // Unbraced control bodies need their own observed entry event.
      if(ts.isIfStatement(node)){const branch=(s:ts.Statement)=>ts.isBlock(s)?ts.visitNode(s,visit) as ts.Statement:f.createBlock([...(enabled?[hook(s)]:[]),ts.visitNode(s,visit) as ts.Statement],true);return f.updateIfStatement(node,ts.visitNode(node.expression,visit) as ts.Expression,branch(node.thenStatement),node.elseStatement?branch(node.elseStatement):undefined)}
      return ts.visitEachChild(node,visit,context)
    }
    return root=>ts.visitNode(root,visit) as ts.SourceFile;
  };
  const result=ts.transpileModule(source,{fileName:filename,compilerOptions:{target:ts.ScriptTarget.ES2020,module:ts.ModuleKind.None,sourceMap:true},transformers:{before:[transformer]},reportDiagnostics:true});
  for(const d of result.diagnostics||[])diagnostics.push({message:ts.flattenDiagnosticMessageText(d.messageText,'\n'),line:0});
  return {code:result.outputText,sourceMap:result.sourceMapText,diagnostics};
}
