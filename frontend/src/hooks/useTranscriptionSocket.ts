import {useCallback,useEffect,useRef,useState} from 'react';

export function useTranscriptionSocket(consultationId?:string){
  const socket=useRef<WebSocket|null>(null);
  const [status,setStatus]=useState<'idle'|'connecting'|'open'|'closed'|'error'>('idle');
  const [partial,setPartial]=useState('');
  const [finalText,setFinalText]=useState('');
  const connect=useCallback(()=>{
    if(!consultationId)return;
    socket.current?.close();setStatus('connecting');
    const protocol=location.protocol==='https:'?'wss':'ws';
    const ws=new WebSocket(`${protocol}://${location.host}/api/v1/consultations/${consultationId}/stream`);socket.current=ws;
    ws.onopen=()=>{setStatus('open');ws.send(JSON.stringify({event:'start',session_id:crypto.randomUUID(),timestamp:Date.now()}))};
    ws.onmessage=e=>{try{const value=JSON.parse(String(e.data));if(value.event==='partial')setPartial(value.text||'');if(value.event==='final'){setFinalText(value.text||'');setPartial('')}}catch{setStatus('error')}};
    ws.onerror=()=>setStatus('error');ws.onclose=()=>setStatus('closed');
  },[consultationId]);
  useEffect(()=>()=>socket.current?.close(1000,'view closed'),[]);
  const send=(blob:Blob,sequence:number)=>{if(socket.current?.readyState===WebSocket.OPEN){socket.current.send(JSON.stringify({event:'audio_chunk',sequence,timestamp:Date.now(),mime_type:blob.type,size:blob.size}));socket.current.send(blob)}};
  const finish=()=>socket.current?.send(JSON.stringify({event:'stop',timestamp:Date.now()}));
  return {connect,send,finish,status,partial,finalText};
}
