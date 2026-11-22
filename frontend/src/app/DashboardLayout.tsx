import {useEffect, useState, type ReactNode} from 'react';
import {Activity, ChevronRight, HeartPulse, LayoutDashboard, LogOut, Menu, Settings, ShieldCheck, Users, X} from 'lucide-react';
import {Link, NavLink, Outlet, useLocation} from 'react-router-dom';
import {cn, initials} from '../lib/utils';
import {useAuth} from './AuthProvider';

const navigation = [
  {to: '/dashboard', label: 'Overview', description: 'Clinical priorities', icon: LayoutDashboard},
  {to: '/patients', label: 'Patients', description: 'Synthetic records', icon: Users},
  {to: '/settings', label: 'Settings', description: 'Workspace preferences', icon: Settings},
] as const;

const routeLabels: Record<string, string> = {
  dashboard: 'Overview', patients: 'Patients', new: 'New record', consultations: 'Consultations',
  review: 'Clinical review', analytics: 'AI analysis', documents: 'Documents', settings: 'Settings',
};

function isRecordId(value: string) {
  return /^[0-9a-f-]{16,}$/i.test(value);
}

function Breadcrumbs({pathname}: {pathname: string}) {
  const segments = pathname.split('/').filter(Boolean);
  return <nav aria-label="Breadcrumb" className="min-w-0"><ol className="flex min-w-0 items-center gap-1.5 text-sm text-slate-500">
    <li className="hidden sm:block"><Link className="rounded font-medium hover:text-brand-700" to="/dashboard">Workspace</Link></li>
    {segments.map((segment, index) => {
      const isLast = index === segments.length - 1;
      const label = isRecordId(segment) ? 'Record' : (routeLabels[segment] ?? segment.replaceAll('-', ' '));
      const to = `/${segments.slice(0, index + 1).join('/')}`;
      return <li className="flex min-w-0 items-center gap-1.5" key={`${segment}-${index}`}>
        <ChevronRight aria-hidden="true" className="hidden size-3.5 shrink-0 text-slate-300 sm:block" />
        {isLast ? <span aria-current="page" className="truncate font-semibold capitalize text-slate-800">{label}</span> :
          <Link className="hidden truncate rounded capitalize hover:text-brand-700 sm:block" to={to}>{label}</Link>}
      </li>;
    })}
  </ol></nav>;
}

export function DashboardLayout() {
  const [mobileNavigationOpen, setMobileNavigationOpen] = useState(false);
  const {doctor, logout} = useAuth();
  const location = useLocation();

  useEffect(() => setMobileNavigationOpen(false), [location.pathname]);
  useEffect(() => {
    if (!mobileNavigationOpen) return;
    const closeOnEscape = (event: KeyboardEvent) => { if (event.key === 'Escape') setMobileNavigationOpen(false); };
    document.addEventListener('keydown', closeOnEscape);
    return () => document.removeEventListener('keydown', closeOnEscape);
  }, [mobileNavigationOpen]);

  return <div className="min-h-screen bg-canvas text-slate-950">
    <a className="fixed left-4 top-3 z-[60] -translate-y-20 rounded-lg bg-white px-4 py-2 text-sm font-semibold text-brand-700 shadow-lg transition-transform focus:translate-y-0" href="#main-content">Skip to main content</a>

    <aside aria-label="Workspace navigation" className={cn('fixed inset-y-0 left-0 z-50 flex w-72 flex-col border-r border-white/10 bg-slate-950 text-white shadow-2xl shadow-slate-950/20 transition-transform duration-200 lg:translate-x-0 lg:shadow-none', mobileNavigationOpen ? 'translate-x-0' : '-translate-x-full')}>
      <div className="flex h-20 items-center justify-between border-b border-white/10 px-5">
        <Link className="flex items-center gap-3 rounded-lg" to="/dashboard" aria-label="DiagnoVision overview">
          <span className="grid size-10 place-items-center rounded-xl bg-brand-500 text-slate-950 shadow-lg shadow-brand-500/20"><HeartPulse aria-hidden="true" className="size-6" /></span>
          <span><span className="block text-[15px] font-bold tracking-tight">DiagnoVision</span><span className="block text-[11px] font-medium uppercase tracking-[0.16em] text-slate-400">Clinical workspace</span></span>
        </Link>
        <button aria-label="Close navigation" className="grid size-10 place-items-center rounded-lg text-slate-400 hover:bg-white/10 hover:text-white lg:hidden" onClick={() => setMobileNavigationOpen(false)} type="button"><X aria-hidden="true" className="size-5" /></button>
      </div>

      <div className="flex-1 overflow-y-auto px-4 py-6">
        <p className="px-3 text-[11px] font-bold uppercase tracking-[0.16em] text-slate-500">Workspace</p>
        <nav className="mt-3 space-y-1" aria-label="Primary navigation">
          {navigation.map(({to, label, description, icon: Icon}) => <NavLink className={({isActive}) => cn('group flex items-center gap-3 rounded-xl px-3 py-3 text-slate-300 transition-colors hover:bg-white/[0.07] hover:text-white', isActive && 'bg-brand-700 text-white shadow-md shadow-slate-950/20 hover:bg-brand-700')} key={to} to={to}>
            {({isActive}) => <><span className={cn('grid size-9 shrink-0 place-items-center rounded-lg bg-white/[0.06] text-slate-400 group-hover:text-white', isActive && 'bg-white/10 text-white')}><Icon aria-hidden="true" className="size-[18px]" /></span><span className="min-w-0"><span className="block text-sm font-semibold">{label}</span><span className={cn('block truncate text-xs text-slate-500', isActive && 'text-brand-100')}>{description}</span></span></>}
          </NavLink>)}
        </nav>
        <div className="mt-8 rounded-xl border border-amber-300/15 bg-amber-300/[0.06] p-4">
          <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-[0.12em] text-amber-300"><Activity aria-hidden="true" className="size-4" />Research mode</div>
          <p className="mt-2 text-xs leading-5 text-slate-400">Synthetic data only. Every AI output requires physician review.</p>
        </div>
      </div>

      <div className="border-t border-white/10 p-4">
        <div className="flex items-center gap-3 rounded-xl bg-white/[0.05] p-3">
          <span className="grid size-10 shrink-0 place-items-center rounded-full bg-brand-700 text-xs font-bold ring-2 ring-white/10">{initials(doctor?.full_name)}</span>
          <div className="min-w-0 flex-1"><p className="truncate text-sm font-semibold">{doctor?.full_name}</p><p className="truncate text-xs text-slate-400">Authenticated physician</p></div>
        </div>
        <button className="mt-2 flex min-h-10 w-full items-center gap-3 rounded-lg px-3 text-sm font-medium text-slate-400 transition-colors hover:bg-white/[0.07] hover:text-white" onClick={() => void logout()} type="button"><LogOut aria-hidden="true" className="size-4" />Sign out</button>
      </div>
    </aside>

    <div className="min-h-screen lg:pl-72">
      <header className="sticky top-0 z-30 flex h-16 items-center gap-3 border-b border-slate-200/80 bg-white/90 px-4 backdrop-blur-xl lg:px-8">
        <button aria-expanded={mobileNavigationOpen} aria-label="Open navigation" className="grid size-10 shrink-0 place-items-center rounded-lg border bg-white text-slate-600 shadow-sm hover:bg-slate-50 lg:hidden" onClick={() => setMobileNavigationOpen(true)} type="button"><Menu aria-hidden="true" className="size-5" /></button>
        <Breadcrumbs pathname={location.pathname} />
        <div className="ml-auto flex shrink-0 items-center gap-3">
          <span className="hidden items-center gap-2 rounded-full border border-amber-200 bg-amber-50 px-3 py-1.5 text-xs font-semibold text-amber-900 sm:flex"><span className="size-1.5 rounded-full bg-amber-500" />Research prototype</span>
          <span className="hidden h-6 w-px bg-slate-200 sm:block" aria-hidden="true" />
          <span className="grid size-9 place-items-center rounded-full bg-brand-50 text-brand-700" title="Protected clinical session"><ShieldCheck aria-hidden="true" className="size-[18px]" /><span className="sr-only">Protected clinical session</span></span>
        </div>
      </header>
      <main className="mx-auto w-full max-w-[1600px] p-4 sm:p-6 lg:p-8" id="main-content" tabIndex={-1}><Outlet /></main>
    </div>

    {mobileNavigationOpen && <button aria-label="Close navigation overlay" className="fixed inset-0 z-40 bg-slate-950/50 backdrop-blur-[2px] lg:hidden" onClick={() => setMobileNavigationOpen(false)} type="button" />}
  </div>;
}

export function PageHeader({title, description, action}: {title: string; description: string; action?: ReactNode}) {
  return <div className="mb-8 flex flex-wrap items-start justify-between gap-4 border-b border-slate-200/80 pb-6"><div><h1 className="page-title">{title}</h1><p className="mt-2 max-w-2xl text-slate-500">{description}</p></div>{action && <div className="shrink-0">{action}</div>}</div>;
}
