import {useQuery} from '@tanstack/react-query';
import {Activity,AlertCircle,ArrowRight,BrainCircuit,CalendarDays,CheckCircle2,ClipboardCheck,FileClock,Plus,Settings,ShieldCheck,Sparkles,Target,Users} from 'lucide-react';
import {Link} from 'react-router-dom';
import {PageHeader} from '../../app/DashboardLayout';
import {Badge,Card,EmptyState,ErrorState,Spinner} from '../../components/ui';
import {getPatientAiDemo} from '../ai-analysis/demoAiData';
import {dashboardRepo,patientsRepo} from '../../lib/repositories';
import {formatDate} from '../../lib/utils';
import type {Consultation,Patient} from '../../types/api';

const consultationTone=(status:string):'green'|'amber'|'blue'|'neutral'=>{if(status==='approved')return 'green';if(status==='draft'||status==='review')return 'amber';if(status==='processing')return 'blue';return 'neutral'};

type PatientWithPriority = Patient & {priorityScore:number;priorityLabel:string;priorityClass:'red'|'amber'|'green'|'neutral'};

function getPriorityClass(score:number):'red'|'amber'|'green'|'neutral'{
  if(score>=75)return 'red';
  if(score>=45)return 'amber';
  if(score>0)return 'green';
  return 'neutral';
}

function PriorityScoreBar({score,max=100}:{score:number;max?:number}){
  const pct=max>0?Math.min(100,Math.round(score/max*100)):0;
  const colorClass=score>=75?'bg-red-500':score>=45?'bg-amber-500':score>0?'bg-emerald-500':'bg-slate-200';
  return (
    <div className="mt-1.5 h-1.5 w-full overflow-hidden rounded-full bg-slate-100" role="progressbar" aria-valuenow={score} aria-valuemin={0} aria-valuemax={max}>
      <div className={`h-full rounded-full transition-all ${colorClass}`} style={{width:`${pct}%`}}/>
    </div>
  );
}

function PriorityBadge({patientClass}:{patientClass:'red'|'amber'|'green'|'neutral'}){
  if(patientClass==='red')return <Badge tone="red">High priority</Badge>;
  if(patientClass==='amber')return <Badge tone="amber">Review recommended</Badge>;
  if(patientClass==='green')return <Badge tone="green">Routine review</Badge>;
  return <Badge>Insufficient data</Badge>;
}

function PatientPriorityRow({patient,rank}:{patient:PatientWithPriority;rank:number}){
  const scoreTextClass=patient.priorityClass==='red'?'text-red-700':patient.priorityClass==='amber'?'text-amber-700':patient.priorityClass==='green'?'text-emerald-700':'text-slate-400';
  return (
    <li className="grid items-center gap-3 border-b border-slate-100 px-5 py-4 last:border-b-0 sm:grid-cols-[2rem_minmax(0,1fr)_minmax(10rem,auto)_minmax(5rem,auto)_auto] lg:px-6">
      <span className="text-sm font-bold text-slate-400">#{rank}</span>
      <div className="min-w-0">
        <p className="truncate font-semibold text-slate-900">{patient.full_name}</p>
        <p className="mt-0.5 text-xs text-slate-500">{patient.priorityLabel}</p>
      </div>
      <div className="hidden sm:block">
        <PriorityBadge patientClass={patient.priorityClass}/>
      </div>
      <div className="hidden sm:block min-w-[5rem]">
        <p className={`text-lg font-bold ${scoreTextClass}`}>{patient.priorityScore}<span className="text-xs font-normal text-slate-400">/100</span></p>
        <PriorityScoreBar score={patient.priorityScore}/>
      </div>
      <Link className="inline-flex min-h-9 items-center justify-center gap-1.5 rounded-lg px-3 text-sm font-semibold text-brand-700 hover:bg-brand-50" to={`/patients/${patient.id}/analytics`} aria-label={`View AI analysis for ${patient.full_name}`}>
        AI Analysis<ArrowRight className="size-4" aria-hidden="true"/>
      </Link>
    </li>
  );
}

function PatientPrioritySection(){
  const patientsQuery=useQuery({queryKey:['patients','all-for-priority'],queryFn:()=>patientsRepo.list({page_size:50,sort_by:'name'})});
  if(patientsQuery.isLoading)return <div className="p-6"><Spinner label="Loading patient priorities…"/></div>;
  if(patientsQuery.error||!patientsQuery.data?.items?.length){
    return <div className="p-5 lg:p-6"><EmptyState title="No patients yet" description="Add a patient and run an AI analysis to see priority scores here."/></div>;
  }
  const enriched:PatientWithPriority[]=patientsQuery.data.items.map(p=>{
    const demo=getPatientAiDemo(p.full_name);
    const cls=getPriorityClass(demo.priority.score);
    return {...p,priorityScore:demo.priority.score,priorityLabel:demo.priority.label,priorityClass:cls};
  }).sort((a,b)=>b.priorityScore-a.priorityScore);
  return (
    <ul aria-label="Patients ordered by priority score">
      {enriched.map((p,i)=><PatientPriorityRow patient={p} rank={i+1} key={p.id}/>)}
    </ul>
  );
}

function MetricCard({label,value,detail,icon:Icon,iconClass,href}:{label:string;value:number;detail:string;icon:typeof Users;iconClass:string;href:string}){return <Card className="group relative overflow-hidden p-5 transition hover:border-slate-300 hover:shadow-md"><div className="flex items-start justify-between gap-4"><div><p className="text-sm font-medium text-slate-500">{label}</p><p className="mt-2 text-3xl font-bold tracking-tight text-slate-950">{value}</p><p className="mt-1 text-xs text-slate-500">{detail}</p></div><span className={`grid size-11 shrink-0 place-items-center rounded-xl ${iconClass}`} aria-hidden="true"><Icon className="size-5"/></span></div><Link className="absolute inset-0 rounded-xl focus-visible:ring-inset" to={href} aria-label={`View ${label.toLowerCase()}`}/></Card>}

function ConsultationRow({consultation}:{consultation:Consultation}){const needsReview=consultation.status!=='approved';return <li className="group grid gap-3 border-b border-slate-100 px-5 py-4 last:border-b-0 sm:grid-cols-[minmax(0,1.5fr)_minmax(7rem,.7fr)_minmax(8rem,.8fr)_auto] sm:items-center lg:px-6"><div className="flex min-w-0 items-center gap-3"><span className="grid size-10 shrink-0 place-items-center rounded-xl bg-blue-50 text-blue-700" aria-hidden="true"><FileClock className="size-5"/></span><div className="min-w-0"><Link className="font-semibold text-slate-900 hover:text-brand-700" to={`/consultations/${consultation.id}`}>Consultation record</Link><p className="mt-0.5 truncate text-xs text-slate-500">Patient record · {consultation.mode} capture</p></div></div><div className="text-sm text-slate-600"><span className="sm:hidden">Recorded </span>{formatDate(consultation.occurred_at)}</div><div><Badge tone={consultationTone(consultation.status)}>{consultation.status}</Badge></div><Link className="inline-flex min-h-9 items-center justify-center gap-1.5 rounded-lg px-3 text-sm font-semibold text-brand-700 hover:bg-brand-50" to={needsReview?`/consultations/${consultation.id}/review`:`/consultations/${consultation.id}`}>{needsReview?'Review':'Open'}<ArrowRight className="size-4" aria-hidden="true"/></Link></li>}

export function DashboardPage(){const query=useQuery({queryKey:['dashboard'],queryFn:dashboardRepo.overview});if(query.isLoading)return <Spinner label="Loading clinical overview…"/>;if(query.error)return <ErrorState message={String(query.error)} onRetry={()=>void query.refetch()}/>;const overview=query.data!;const recentReviewCandidates=overview.recent_consultations.filter(item=>item.status!=='approved').length;return <>
  <PageHeader title="Clinical overview" description="A focused view of patient activity, review work, and recent AI-assisted analysis." action={<div className="flex flex-wrap gap-2"><Link className="btn-secondary" to="/patients"><Users className="size-4" aria-hidden="true"/>View patients</Link><Link className="btn-primary" to="/patients/new"><Plus className="size-4" aria-hidden="true"/>Add patient</Link></div>}/>
  <section aria-label="Workspace summary" className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4"><MetricCard label="Active patients" value={overview.patient_count} detail="Accessible in this workspace" icon={Users} iconClass="bg-brand-50 text-brand-700" href="/patients"/><MetricCard label="Pending reviews" value={overview.pending_reviews} detail="Awaiting physician validation" icon={ClipboardCheck} iconClass="bg-amber-50 text-amber-700" href="/patients"/><MetricCard label="Recent records" value={overview.recent_consultations.length} detail="Latest consultations returned" icon={CalendarDays} iconClass="bg-blue-50 text-blue-700" href="/patients"/><MetricCard label="Recent analyses" value={overview.latest_analyses.length} detail="Latest analysis runs returned" icon={BrainCircuit} iconClass="bg-violet-50 text-violet-700" href="/patients"/></section>
  <section aria-labelledby="attention-title" className={`mt-6 overflow-hidden rounded-xl border p-5 ${overview.pending_reviews?'border-amber-200 bg-amber-50':'border-emerald-200 bg-emerald-50'}`}><div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between"><div className="flex items-start gap-3"><span className={`grid size-10 shrink-0 place-items-center rounded-full ${overview.pending_reviews?'bg-amber-100 text-amber-800':'bg-emerald-100 text-emerald-700'}`} aria-hidden="true">{overview.pending_reviews?<AlertCircle className="size-5"/>:<CheckCircle2 className="size-5"/>}</span><div><h2 id="attention-title" className="font-bold text-slate-950">{overview.pending_reviews?'Physician review required':'Review queue is clear'}</h2><p className="mt-1 text-sm text-slate-600">{overview.pending_reviews?`${overview.pending_reviews} AI-assisted ${overview.pending_reviews===1?'draft requires':'drafts require'} explicit validation. ${recentReviewCandidates} appear in the recent activity shown below.`:'No AI-assisted drafts are currently waiting for validation.'}</p></div></div><Link className="btn-secondary shrink-0 bg-white" to="/patients">Open patient records<ArrowRight className="size-4" aria-hidden="true"/></Link></div></section>
  <section aria-labelledby="priority-title" className="mt-6">
    <Card className="overflow-hidden">
      <div className="flex flex-wrap items-center justify-between gap-3 border-b px-5 py-5 lg:px-6">
        <div className="flex items-center gap-3">
          <span className="grid size-10 shrink-0 place-items-center rounded-xl bg-rose-50 text-rose-700" aria-hidden="true"><Target className="size-5"/></span>
          <div>
            <h2 id="priority-title" className="font-bold text-slate-950">Clinical priorities</h2>
            <p className="mt-0.5 text-sm text-slate-500">Patients ordered by AI review priority score — highest first</p>
          </div>
        </div>
        <Badge tone="red">Priority ranking</Badge>
      </div>
      <PatientPrioritySection/>
    </Card>
  </section>
  <div className="mt-6 grid items-start gap-6 xl:grid-cols-[minmax(0,1.45fr)_minmax(20rem,.75fr)]"><div className="space-y-6"><Card className="overflow-hidden"><div className="flex flex-wrap items-start justify-between gap-3 border-b px-5 py-5 lg:px-6"><div><h2 className="font-bold text-slate-950">Recent consultations</h2><p className="mt-1 text-sm text-slate-500">Latest documentation and review activity</p></div><Badge tone="blue">{overview.recent_consultations.length} recent</Badge></div>{overview.recent_consultations.length?<ul aria-label="Recent consultations">{overview.recent_consultations.map(item=><ConsultationRow consultation={item} key={item.id}/>)}</ul>:<div className="p-5 lg:p-6"><EmptyState title="No consultations yet" description="Open a patient record to create the first consultation." action={<Link className="btn-secondary" to="/patients">Browse patients</Link>}/></div>}</Card>
      <Card className="overflow-hidden"><div className="flex flex-wrap items-start justify-between gap-3 border-b px-5 py-5 lg:px-6"><div><h2 className="font-bold text-slate-950">Recent clinical indicators</h2><p className="mt-1 text-sm text-slate-500">Latest approved, source-backed observations</p></div><Badge tone="teal">Approved facts</Badge></div>{overview.relevant_observations.length?<div className="overflow-x-auto"><table className="w-full text-left text-sm"><thead className="bg-slate-50 text-xs uppercase tracking-wide text-slate-500"><tr><th className="px-5 py-3 font-semibold lg:px-6">Indicator</th><th className="px-5 py-3 font-semibold">Value</th><th className="px-5 py-3 font-semibold">Observed</th><th className="px-5 py-3 font-semibold"><span className="sr-only">Patient record</span></th></tr></thead><tbody className="divide-y divide-slate-100">{overview.relevant_observations.slice(0,6).map(observation=><tr key={observation.id}><td className="px-5 py-4 font-semibold text-slate-900 lg:px-6">{observation.name}</td><td className="whitespace-nowrap px-5 py-4 text-slate-700">{observation.value}{observation.unit?` ${observation.unit}`:''}</td><td className="whitespace-nowrap px-5 py-4 text-slate-500"><time dateTime={observation.observed_at}>{formatDate(observation.observed_at)}</time></td><td className="px-5 py-4 text-right"><Link className="font-semibold text-brand-700 hover:text-brand-900" to={`/patients/${observation.patient_id}`}>Open<span className="sr-only"> patient record for {observation.name}</span></Link></td></tr>)}</tbody></table></div>:<div className="p-5 lg:p-6"><EmptyState title="No approved indicators" description="Approved clinical observations will appear here with their recorded values."/></div>}</Card></div>
    <div className="space-y-6"><Card className="overflow-hidden"><div className="flex items-start justify-between gap-3 border-b px-5 py-5"><div><h2 className="font-bold text-slate-950">Latest AI analyses</h2><p className="mt-1 text-sm text-slate-500">Evidence summaries for physician review</p></div><Sparkles className="size-5 text-violet-600" aria-hidden="true"/></div>{overview.latest_analyses.length?<ul className="divide-y divide-slate-100" aria-label="Latest AI analyses">{overview.latest_analyses.slice(0,4).map(analysis=>{const concernCount=analysis.worsening?.length??0;return <li className="p-5" key={analysis.id}><div className="flex items-center justify-between gap-3"><Badge tone={analysis.reviewed_at?'green':'amber'}>{analysis.reviewed_at?'Reviewed':'Needs review'}</Badge><time className="text-xs text-slate-500" dateTime={analysis.created_at}>{formatDate(analysis.created_at)}</time></div><p className="mt-3 line-clamp-2 text-sm leading-6 text-slate-700">{analysis.summary}</p><div className="mt-3 flex items-center justify-between gap-3"><span className={`text-xs font-medium ${concernCount?'text-red-700':'text-slate-500'}`}>{concernCount?`${concernCount} worsening ${concernCount===1?'indicator':'indicators'}`:'No worsening indicator reported'}</span><Link className="inline-flex items-center gap-1 text-sm font-semibold text-brand-700 hover:text-brand-900" to={`/patients/${analysis.patient_id}/analytics`}>Open<ArrowRight className="size-3.5" aria-hidden="true"/></Link></div></li>})}</ul>:<div className="p-5"><EmptyState title="No analyses yet" description="Analysis runs started from a patient record will appear here."/></div>}</Card>
      <Card className="p-5"><h2 className="font-bold text-slate-950">Quick actions</h2><nav className="mt-3 space-y-1" aria-label="Dashboard quick actions"><Link className="flex items-center gap-3 rounded-lg p-3 text-sm font-semibold text-slate-700 hover:bg-slate-50 hover:text-brand-700" to="/patients/new"><Plus className="size-4 text-brand-700" aria-hidden="true"/>Create synthetic patient<ArrowRight className="ml-auto size-4 text-slate-400" aria-hidden="true"/></Link><Link className="flex items-center gap-3 rounded-lg p-3 text-sm font-semibold text-slate-700 hover:bg-slate-50 hover:text-brand-700" to="/patients"><Activity className="size-4 text-blue-700" aria-hidden="true"/>Explore patient records<ArrowRight className="ml-auto size-4 text-slate-400" aria-hidden="true"/></Link><Link className="flex items-center gap-3 rounded-lg p-3 text-sm font-semibold text-slate-700 hover:bg-slate-50 hover:text-brand-700" to="/settings"><Settings className="size-4 text-slate-600" aria-hidden="true"/>Workspace settings<ArrowRight className="ml-auto size-4 text-slate-400" aria-hidden="true"/></Link></nav></Card></div></div>
  <aside className="mt-6 flex items-start gap-3 rounded-xl border border-slate-200 bg-white p-4 text-sm text-slate-600" aria-label="Clinical safety notice"><ShieldCheck className="mt-0.5 size-5 shrink-0 text-brand-700" aria-hidden="true"/><p><strong className="text-slate-900">Clinical safety:</strong> DiagnoVision is a research prototype using synthetic data. AI outputs remain drafts until physician validation and are not diagnoses or treatment recommendations.</p></aside>
</>}
