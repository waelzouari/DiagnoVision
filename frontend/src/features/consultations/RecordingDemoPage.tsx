import {useQuery} from '@tanstack/react-query';
import {AlertTriangle,ArrowLeft,Check,CheckCircle2,Database,Mic,Pause,Play,RotateCcw,ShieldCheck,Sparkles,Square,WandSparkles} from 'lucide-react';
import {useEffect,useMemo,useState} from 'react';
import {Link,useParams} from 'react-router-dom';
import {PageHeader} from '../../app/DashboardLayout';
import {Badge,Button,Card,ErrorState,SectionTitle,Spinner} from '../../components/ui';
import {useRecorder} from '../../hooks/useRecorder';
import {errorMessage} from '../../lib/api';
import {patientsRepo} from '../../lib/repositories';

const rawTranscript='Um, I have had headaches for, like, three days. No chest pain. My temperature was thirty-eight point two this morning, and I took paracetamol 500 milligrams. The headache is still there.';
const cleanedTranscript='The patient reports headaches for three days. The patient denies chest pain. Temperature was 38.2 °C this morning. The patient took paracetamol 500 mg. The headache persists.';
const facts=[
  {label:'Chief complaint',value:'Persistent headache for 3 days'},
  {label:'Negated symptom',value:'Chest pain denied'},
  {label:'Observation',value:'Temperature: 38.2 °C'},
  {label:'Medication reported',value:'Paracetamol 500 mg'},
] as const;
const cleaningChanges=[
  {rule:'Filler removal',before:'Um … like',after:'Removed without changing clinical meaning'},
  {rule:'Number normalization',before:'thirty-eight point two',after:'38.2'},
  {rule:'Unit normalization',before:'500 milligrams',after:'500 mg'},
  {rule:'Negation preservation',before:'No chest pain',after:'Chest pain denied'},
] as const;
const qualityChecks=[
  'Original transcript preserved',
  'Clinical negation retained',
  'Values and units normalized',
  'Unknown information not invented',
] as const;
type DemoStage='capture'|'ready'|'cleaning'|'review';

export function RecordingDemoPage(){
  const {patientId=''}=useParams();
  const patient=useQuery({queryKey:['patient',patientId],queryFn:()=>patientsRepo.one(patientId)});
  const recorder=useRecorder();
  const [consent,setConsent]=useState(false);
  const [stage,setStage]=useState<DemoStage>('capture');
  const [source,setSource]=useState<'microphone'|'sample'|null>(null);
  const [message,setMessage]=useState('');
  const [cleaned,setCleaned]=useState(cleanedTranscript);
  const audioUrl=useMemo(()=>recorder.blob&&typeof URL.createObjectURL==='function'?URL.createObjectURL(recorder.blob):'',[recorder.blob]);
  useEffect(()=>()=>{if(audioUrl)URL.revokeObjectURL(audioUrl)},[audioUrl]);
  useEffect(()=>{if(recorder.state==='stopped'&&recorder.blob){setSource('microphone');setStage('ready')}},[recorder.state,recorder.blob]);
  const start=async()=>{setMessage('');try{await recorder.start();setSource('microphone')}catch(error){setMessage(errorMessage(error))}};
  const loadSample=()=>{recorder.cancel();setSource('sample');setStage('ready');setMessage('Synthetic jury sample loaded. No microphone or backend was used.')};
  const clean=()=>{setStage('cleaning');setMessage('');window.setTimeout(()=>setStage('review'),700)};
  const reset=()=>{recorder.cancel();setStage('capture');setSource(null);setMessage('');setCleaned(cleanedTranscript)};
  if(patient.isLoading)return <Spinner label="Loading recording workspace…"/>;
  if(patient.error)return <ErrorState message={errorMessage(patient.error)} onRetry={()=>void patient.refetch()}/>;
  const value=patient.data!;
  const clock=`${String(Math.floor(recorder.seconds/60)).padStart(2,'0')}:${String(recorder.seconds%60).padStart(2,'0')}`;
  return <>
    <PageHeader title="Consultation recording demo" description={`Frontend-only recording and data-cleaning workflow for ${value.full_name}.`} action={<Link className="btn-secondary" to={`/patients/${patientId}`}><ArrowLeft className="size-4"/>Patient record</Link>}/>
    <div className="mb-6 flex items-start gap-3 rounded-xl border border-blue-200 bg-blue-50 p-4 text-sm text-blue-950"><Database className="mt-0.5 size-5 shrink-0"/><div className="flex-1"><p className="font-bold">Private frontend demonstration</p><p className="mt-1 text-blue-800">Audio remains in this browser session and is never uploaded. Transcription and extracted facts below are explicitly simulated for the jury demo.</p></div><Badge tone="blue">Local only</Badge></div>
    <div className="grid items-start gap-6 xl:grid-cols-[minmax(0,1fr)_minmax(22rem,.72fr)]">
      <div className="space-y-6">
        <Card className="p-6"><SectionTitle title="1. Record the conversation" description="Explicit consent is required before microphone activation."/>
          <label className="flex items-start gap-3 rounded-xl border border-amber-200 bg-amber-50 p-4"><input className="mt-1 size-4 accent-teal-700" type="checkbox" checked={consent} onChange={event=>setConsent(event.target.checked)} disabled={recorder.state==='recording'||recorder.state==='paused'}/><span><strong className="block text-amber-950">Patient recording consent confirmed</strong><span className="mt-1 block text-sm text-amber-800">For this synthetic demonstration, consent is kept only in page memory.</span></span></label>
          <div className="mt-5 flex min-h-64 flex-col items-center justify-center rounded-2xl border bg-slate-50 p-6 text-center"><span className={`grid size-20 place-items-center rounded-full ${recorder.state==='recording'?'animate-pulse bg-red-100 text-red-600':'bg-brand-100 text-brand-700'}`}><Mic className="size-9"/></span><p className="mt-5 text-4xl font-bold tabular-nums tracking-tight">{clock}</p><p className="mt-1 text-sm font-semibold capitalize text-slate-500">{recorder.state==='idle'?'Ready to record':recorder.state}</p>
            <div className="mt-6 flex flex-wrap justify-center gap-2">{(recorder.state==='idle'||recorder.state==='stopped')&&<Button disabled={!consent||stage==='cleaning'} onClick={()=>void start()}><Mic className="size-4"/>Start recording</Button>}{recorder.state==='recording'&&<><Button variant="secondary" onClick={recorder.pause}><Pause className="size-4"/>Pause</Button><Button variant="danger" onClick={recorder.stop}><Square className="size-4"/>Stop recording</Button></>}{recorder.state==='paused'&&<><Button onClick={recorder.resume}><Play className="size-4"/>Resume</Button><Button variant="danger" onClick={recorder.stop}><Square className="size-4"/>Stop recording</Button></>}<Button variant="secondary" disabled={!consent||recorder.state==='recording'||recorder.state==='paused'} onClick={loadSample}><Sparkles className="size-4"/>Use jury demo sample</Button></div>
          </div>
          {audioUrl&&<audio className="mt-4 w-full" controls src={audioUrl}/>} {message&&<p role="status" className="mt-4 rounded-lg bg-slate-100 p-3 text-sm text-slate-700">{message}</p>}
        </Card>
        {stage!=='capture'&&<Card className="p-6"><SectionTitle title="2. Raw transcript" description="Simulated speech-to-text output, preserved before cleaning." action={<Badge tone="amber">Unreviewed</Badge>}/><p className="rounded-xl border bg-slate-50 p-4 leading-7 text-slate-700">{rawTranscript}</p><div className="mt-5 flex justify-end"><Button onClick={clean} disabled={stage==='cleaning'||stage==='review'}><WandSparkles className="size-4"/>{stage==='cleaning'?'Cleaning data…':'Run data cleaning'}</Button></div></Card>}
        {stage==='review'&&<><Card className="p-6"><SectionTitle title="3. Cleaned transcript" description="Fillers removed, units normalized and negations preserved." action={<Badge tone="green">Ready for review</Badge>}/><label className="label" htmlFor="cleaned-transcript">Physician-editable transcript</label><textarea id="cleaned-transcript" className="input min-h-36 py-3 leading-7" value={cleaned} onChange={event=>setCleaned(event.target.value)}/><div className="mt-4 flex items-center justify-between gap-3"><p className="text-xs text-slate-500">Original audio and raw text remain unchanged in this demo.</p><Button variant="secondary" onClick={reset}><RotateCcw className="size-4"/>Reset demo</Button></div></Card><Card className="overflow-hidden"><div className="border-b px-6 py-5"><SectionTitle title="Data-cleaning report" description="Transparent before/after transformations applied to the static sample."/></div><div className="overflow-x-auto"><table className="w-full text-left text-sm"><thead className="bg-slate-50 text-xs uppercase tracking-wide text-slate-500"><tr><th className="px-6 py-3">Rule</th><th className="px-6 py-3">Raw input</th><th className="px-6 py-3">Clean result</th></tr></thead><tbody className="divide-y">{cleaningChanges.map(change=><tr key={change.rule}><td className="px-6 py-4 font-semibold text-slate-900">{change.rule}</td><td className="px-6 py-4 text-slate-500">{change.before}</td><td className="px-6 py-4 text-brand-800">{change.after}</td></tr>)}</tbody></table></div></Card></>}
      </div>
      <div className="space-y-6"><Card className="p-6"><SectionTitle title="Demo pipeline" description="A jury-friendly view of each transformation."/><ol className="space-y-3"><PipelineStep done={stage!=='capture'} active={stage==='capture'} number="1" title="Audio captured" detail={source==='sample'?'Synthetic sample selected':'Local browser recording'}/><PipelineStep done={stage==='review'} active={stage==='ready'||stage==='cleaning'} number="2" title="Transcript cleaned" detail="Noise, fillers and units normalized"/><PipelineStep done={stage==='review'} active={stage==='review'} number="3" title="Facts structured" detail="Draft only — physician validation required"/></ol></Card>
        {stage==='review'?<><Card className="p-6"><SectionTitle title="Structured clinical draft" description="Static extraction for demonstration; not a diagnosis."/><div className="space-y-3">{facts.map(fact=><div className="rounded-xl border p-4" key={fact.label}><div className="flex items-center gap-2"><CheckCircle2 className="size-4 text-brand-700"/><p className="text-xs font-bold uppercase tracking-wide text-slate-500">{fact.label}</p></div><p className="mt-2 font-semibold text-slate-900">{fact.value}</p><p className="mt-1 text-xs text-slate-500">Source: cleaned transcript</p></div>)}</div><div className="mt-4 flex gap-2 rounded-lg bg-amber-50 p-3 text-sm text-amber-900"><AlertTriangle className="mt-0.5 size-4 shrink-0"/><p><strong>Missing:</strong> pain intensity and relevant medical history remain unknown.</p></div></Card><Card className="p-6"><SectionTitle title="Quality controls" description="Safety checks demonstrated before physician review." action={<ShieldCheck className="size-5 text-brand-700"/>}/><ul className="space-y-3">{qualityChecks.map(check=><li className="flex items-start gap-2 text-sm text-slate-700" key={check}><CheckCircle2 className="mt-0.5 size-4 shrink-0 text-green-600"/>{check}</li>)}</ul><div className="mt-5 rounded-lg border border-violet-200 bg-violet-50 p-3 text-sm text-violet-900"><strong>Demo boundary:</strong> no clinical accuracy score is claimed because this extraction is static and synthetic.</div></Card></>:<Card className="p-6 text-center"><WandSparkles className="mx-auto size-8 text-slate-300"/><p className="mt-3 font-semibold">Structured draft pending</p><p className="mt-1 text-sm text-slate-500">Record or load the jury sample, then run data cleaning.</p></Card>}
      </div>
    </div>
  </>;
}

function PipelineStep({done,active,number,title,detail}:{done:boolean;active:boolean;number:string;title:string;detail:string}){return <li className={`flex gap-3 rounded-xl border p-4 ${active?'border-brand-300 bg-brand-50':''}`}><span className={`grid size-8 shrink-0 place-items-center rounded-full text-sm font-bold ${done?'bg-green-100 text-green-700':active?'bg-brand-700 text-white':'bg-slate-100 text-slate-500'}`}>{done?<Check className="size-4"/>:number}</span><div><p className="text-sm font-bold text-slate-900">{title}</p><p className="mt-1 text-xs text-slate-500">{detail}</p></div></li>}
