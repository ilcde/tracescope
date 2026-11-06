import com.sun.jdi.*;
import com.sun.jdi.connect.*;
import com.sun.jdi.event.*;
import com.sun.jdi.request.*;
import java.util.*;
import java.io.*;

/** JDI client: never invokes target methods, getters, or toString. */
public class TraceAgent {
  static String quote(String s) { return "\""+s.replace("\\","\\\\").replace("\"","\\\"").replace("\n","\\n").replace("\r","\\r").replace("\t","\\t").replace("\b","\\b").replace("\f","\\f")+"\""; }
  static String json(Object o) {
    if(o==null)return "null"; if(o instanceof String)return quote((String)o);
    if(o instanceof Map<?,?> m){ List<String>x=new ArrayList<>();m.forEach((k,v)->x.add(quote(k.toString())+":"+json(v)));return "{"+String.join(",",x)+"}";}
    if(o instanceof List<?> l)return "["+String.join(",",l.stream().map(TraceAgent::json).toList())+"]";
    return o.toString();
  }
  static Map<String,Object> val(Value v,int depth,Set<Long> seen){
    Map<String,Object> m=new LinkedHashMap<>();m.put("state","available");
    if(v==null){m.put("type","null");m.put("value","null");return m;}
    m.put("type",v.type().name());
    if(v instanceof PrimitiveValue){m.put("value",v.toString());return m;}
    if(v instanceof StringReference s){String text=s.value();m.put("value",text.substring(0,Math.min(300,text.length())));if(text.length()>300)m.put("state","truncated");return m;}
    if(v instanceof ObjectReference o){
      m.put("identity",Long.toString(o.uniqueID()));m.put("value","@"+o.uniqueID());
      if(seen.contains(o.uniqueID())){m.put("relation","aliases");return m;}seen.add(o.uniqueID());
      if(depth>=2){m.put("state","truncated");return m;}
      Map<String,Object> children=new LinkedHashMap<>();
      if(o instanceof ArrayReference a){m.put("length",a.length());for(int i=0;i<Math.min(24,a.length());i++)children.put(""+i,val(a.getValue(i),depth+1,seen));}
      else{int count=0;for(Field f:o.referenceType().allFields()){if(count++>=24)break;if(!f.isStatic())try{children.put(f.name(),val(o.getValue(f),depth+1,seen));}catch(Exception ignored){}}}
      m.put("children",children);
    }else{m.put("value","<unavailable>");m.put("state","unavailable");}
    return m;
  }
  static void emit(ThreadReference thread,String kind) throws Exception{
    StackFrame top=thread.frame(0);Location loc=top.location();Map<String,Object>values=new LinkedHashMap<>();
    try{for(LocalVariable v:top.visibleVariables())values.put(v.name(),val(top.getValue(v),0,new HashSet<>()));}catch(AbsentInformationException ignored){}
    List<Object>stack=new ArrayList<>();int index=0;
    for(StackFrame f:thread.frames()){stack.add(Map.of("id",""+index++,"name",f.location().method().name(),"line",Math.max(0,f.location().lineNumber())));if(index>=32)break;}
    Map<String,Object> e=new LinkedHashMap<>();e.put("kind",kind);e.put("line",Math.max(0,loc.lineNumber()));e.put("function",loc.method().name());e.put("values",values);e.put("thread",Long.toString(thread.uniqueID()));e.put("depth",thread.frameCount());e.put("stack",stack);e.put("instruction",Long.toString(loc.codeIndex()));e.put("frame",thread.uniqueID()+":"+thread.frameCount());
    try{e.put("file",loc.sourcePath().replace('\\','/'));}catch(AbsentInformationException ignored){}
    System.out.println(json(e));System.out.flush();
  }
  public static void main(String[]args)throws Exception{
    LaunchingConnector connector=Bootstrap.virtualMachineManager().defaultConnector();var options=connector.defaultArguments();
    options.get("main").setValue(args[1]);options.get("options").setValue("-Xmx128m -cp \""+args[0]+"\"");
    VirtualMachine vm=connector.launch(options);Process process=vm.process();
    byte[] input=java.nio.file.Files.readAllBytes(java.nio.file.Path.of(args[2]));process.getOutputStream().write(input);process.getOutputStream().close();
    ByteArrayOutputStream stdout=new ByteArrayOutputStream();ByteArrayOutputStream stderr=new ByteArrayOutputStream();
    Thread out=Thread.ofPlatform().start(()->copy(process.getInputStream(),stdout));Thread err=Thread.ofPlatform().start(()->copy(process.getErrorStream(),stderr));
    EventRequestManager manager=vm.eventRequestManager();ClassPrepareRequest prep=manager.createClassPrepareRequest();prep.addClassFilter(args[1].split(" ")[0]+"*");prep.setSuspendPolicy(EventRequest.SUSPEND_ALL);prep.enable();
    ExceptionRequest exception=manager.createExceptionRequest(null,false,true);exception.setSuspendPolicy(EventRequest.SUSPEND_EVENT_THREAD);exception.enable();
    boolean done=false;Set<Long>stepping=new HashSet<>();
    try{while(!done){EventSet events=vm.eventQueue().remove(15000);if(events==null)throw new RuntimeException("JDI event timeout");
      for(Event event:events){
        if(event instanceof ClassPrepareEvent prepared){for(Method method:prepared.referenceType().methodsByName("main")){if(!method.isAbstract()){try{var locations=method.allLineLocations();if(!locations.isEmpty()){BreakpointRequest bp=manager.createBreakpointRequest(locations.get(0));bp.enable();}}catch(AbsentInformationException ignored){}}}}
        if(event instanceof BreakpointEvent bp){emit(bp.thread(),"line");if(stepping.add(bp.thread().uniqueID())){StepRequest step=manager.createStepRequest(bp.thread(),StepRequest.STEP_LINE,StepRequest.STEP_INTO);for(String filter:List.of("java.*","javax.*","jdk.*","sun.*","kotlin.*"))step.addClassExclusionFilter(filter);step.enable();}}
        if(event instanceof StepEvent step){emit(step.thread(),"line");}
        if(event instanceof ExceptionEvent ex){emit(ex.thread(),"exception");}
        if(event instanceof VMDeathEvent || event instanceof VMDisconnectEvent)done=true;
      }if(!done)events.resume();
    }}catch(VMDisconnectedException ignored){}finally{try{vm.dispose();}catch(Exception ignored){}}
    process.waitFor();out.join(2000);err.join(2000);
    System.out.println(json(Map.of("kind","io","output",stdout.toString("UTF-8")+stderr.toString("UTF-8"),"values",Map.of(),"line",0)));
    if(process.exitValue()!=0)throw new RuntimeException("Target exit "+process.exitValue());
  }
  static void copy(InputStream in,ByteArrayOutputStream out){try{byte[]b=new byte[4096];int n;while((n=in.read(b))!=-1){if(out.size()+n>65536)throw new IOException("Output quota");out.write(b,0,n);}}catch(IOException ignored){}}
}
