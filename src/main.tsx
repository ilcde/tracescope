import React from 'react';
import {createRoot} from 'react-dom/client';
import App from './App';
import './styles.css';
import './readability.css';
class ApplicationBoundary extends React.Component<React.PropsWithChildren,{error:string}>{
 state={error:''};
 static getDerivedStateFromError(error:unknown){return {error:error instanceof Error?error.message:String(error)}}
 render(){if(!this.state.error)return this.props.children;const vi=document.documentElement.lang==='vi';return <main className="startup-error" role="alert"><h1>TraceScope</h1><h2>{vi?'Không thể mở không gian làm việc':'The workspace could not open'}</h2><p>{vi?'Mã đã lưu vẫn còn trên thiết bị. Xem chẩn đoán dưới đây rồi thử lại.':'Saved source remains on this device. Review the diagnostic below and reload to retry.'}</p><pre>{this.state.error}</pre><button onClick={()=>location.reload()}>{vi?'Tải lại':'Reload'}</button></main>}
}
createRoot(document.getElementById('root')!).render(<React.StrictMode><ApplicationBoundary><App/></ApplicationBoundary></React.StrictMode>);
