package app.tracescope;
import android.app.Activity;
import android.os.Bundle;
import android.content.Intent;
import android.net.Uri;
import android.webkit.*;
import android.view.View;
import java.io.*;
import java.util.*;

/** Offline asset origin; no JavaScript/native bridge is exposed to preview frames. */
public final class MainActivity extends Activity {
  private WebView web;
  private ValueCallback<Uri[]> fileCallback;
  private byte[] pendingExport;
  @Override public void onCreate(Bundle state) {
    super.onCreate(state);
    getWindow().setStatusBarColor(0xff10171f);getWindow().setNavigationBarColor(0xff10171f);
    web=new WebView(this);setContentView(web);WebView.setWebContentsDebuggingEnabled(true);
    WebSettings settings=web.getSettings();settings.setJavaScriptEnabled(true);settings.setDomStorageEnabled(true);
    settings.setAllowFileAccess(false);settings.setAllowContentAccess(false);settings.setMixedContentMode(WebSettings.MIXED_CONTENT_NEVER_ALLOW);
    settings.setMediaPlaybackRequiresUserGesture(true);settings.setSupportZoom(false);settings.setSafeBrowsingEnabled(true);
    web.setWebViewClient(new WebViewClient(){
      @Override public WebResourceResponse shouldInterceptRequest(WebView view,WebResourceRequest request){
        Uri url=request.getUrl();
        if(!"https".equals(url.getScheme())||!"appassets.androidplatform.net".equals(url.getHost()))return null;
        String path=url.getPath();if(path==null||!path.startsWith("/assets/")||path.contains(".."))return new WebResourceResponse("text/plain","UTF-8",new ByteArrayInputStream(new byte[0]));
        path=path.substring(8);
        try{String mime=path.endsWith(".wasm")?"application/wasm":path.endsWith(".js")?"text/javascript":path.endsWith(".css")?"text/css":path.endsWith(".html")?"text/html":"application/octet-stream";
          Map<String,String>headers=new HashMap<>();headers.put("X-Content-Type-Options","nosniff");headers.put("Access-Control-Allow-Origin","https://appassets.androidplatform.net");
          return new WebResourceResponse(mime,"UTF-8",200,"OK",headers,getAssets().open(path));
        }catch(IOException error){return new WebResourceResponse("text/plain","UTF-8",404,"Not Found",null,new ByteArrayInputStream(new byte[0]));}
      }
      @Override public boolean shouldOverrideUrlLoading(WebView view,WebResourceRequest request){
        return request.isForMainFrame()&&!"appassets.androidplatform.net".equals(request.getUrl().getHost());
      }
    });
    web.setWebChromeClient(new WebChromeClient(){
      @Override public boolean onShowFileChooser(WebView view,ValueCallback<Uri[]> callback,FileChooserParams params){
        if(fileCallback!=null)fileCallback.onReceiveValue(null);fileCallback=callback;
        Intent intent=new Intent(Intent.ACTION_OPEN_DOCUMENT);intent.addCategory(Intent.CATEGORY_OPENABLE);intent.setType("*/*");
        startActivityForResult(intent,41);return true;
      }
    });
    web.setDownloadListener(new DownloadListener(){ public void onDownloadStart(String url,String userAgent,String disposition,String mime,long length){
      if(!url.startsWith("data:")||url.length()>34000000)return;
      int comma=url.indexOf(',');if(comma<0||!url.substring(0,comma).endsWith(";base64"))return;
      try{pendingExport=android.util.Base64.decode(url.substring(comma+1),android.util.Base64.DEFAULT);
        String type=url.substring(5,url.indexOf(';'));
        Intent save=new Intent(Intent.ACTION_CREATE_DOCUMENT);save.addCategory(Intent.CATEGORY_OPENABLE);save.setType(type);
        save.putExtra(Intent.EXTRA_TITLE,type.contains("svg")?"TraceScope-diagram.svg":type.contains("json")?"TraceScope-trace.json":"TraceScope-source.txt");startActivityForResult(save,42);
      }catch(Exception ignored){pendingExport=null;}
    }});
    if(state!=null)web.restoreState(state);else web.loadUrl("https://appassets.androidplatform.net/assets/index.html");
  }
  @Override protected void onActivityResult(int request,int result,Intent data){super.onActivityResult(request,result,data);if(request==41&&fileCallback!=null){fileCallback.onReceiveValue(result==RESULT_OK&&data!=null?new Uri[]{data.getData()}:null);fileCallback=null;}if(request==42&&pendingExport!=null){if(result==RESULT_OK&&data!=null)try(OutputStream output=getContentResolver().openOutputStream(data.getData())){output.write(pendingExport);}catch(IOException ignored){}pendingExport=null;}}
  @Override protected void onSaveInstanceState(Bundle state){super.onSaveInstanceState(state);web.saveState(state);}
  @Override protected void onPause(){web.onPause();super.onPause();}
  @Override protected void onResume(){super.onResume();web.onResume();}
  @Override public void onBackPressed(){if(web.canGoBack())web.goBack();else super.onBackPressed();}
  @Override protected void onDestroy(){web.destroy();super.onDestroy();}
}
