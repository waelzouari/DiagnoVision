import {QueryClient,QueryClientProvider} from '@tanstack/react-query';
import {cleanup,render,screen} from '@testing-library/react';
import {MemoryRouter,Route,Routes} from 'react-router-dom';
import {afterEach,beforeEach,describe,expect,it,vi} from 'vitest';
import {AnalyticsPage} from '../src/features/ai-analysis/AnalyticsPage';
import {patientsRepo} from '../src/lib/repositories';

vi.mock('../src/lib/repositories',()=>({patientsRepo:{one:vi.fn()}}));
function renderWorkspace(){const client=new QueryClient({defaultOptions:{queries:{retry:false}}});return render(<QueryClientProvider client={client}><MemoryRouter initialEntries={['/patients/patient-1/analytics']}><Routes><Route path="/patients/:patientId/analytics" element={<AnalyticsPage/>}/></Routes></MemoryRouter></QueryClientProvider>)}

describe('static patient multi-agent demo',()=>{
  beforeEach(()=>vi.clearAllMocks());
  afterEach(cleanup);
  it('combines voice, document, risk and priority results for a high-priority profile',async()=>{
    vi.mocked(patientsRepo.one).mockResolvedValue({id:'patient-1',full_name:'Sami Gharbi',date_of_birth:'1970-01-01',created_at:'2026-01-01'});
    renderWorkspace();
    expect(await screen.findByRole('heading',{name:'Patient AI review'})).toBeInTheDocument();
    expect(screen.getByText('Voice Agent')).toBeInTheDocument();
    expect(screen.getByText('Document Agent')).toBeInTheDocument();
    expect(screen.getByText('Possible anemia-related pattern')).toBeInTheDocument();
    expect(screen.getByText('Hemoglobin 9.2 g/dL')).toBeInTheDocument();
    expect(screen.getByText('82')).toBeInTheDocument();
    expect(screen.getByText('High review priority')).toBeInTheDocument();
    expect(screen.getByText(/not an emergency-triage score/i)).toBeInTheDocument();
  });
  it('abstains and avoids a score when the demo record is incomplete',async()=>{
    vi.mocked(patientsRepo.one).mockResolvedValue({id:'patient-1',full_name:'Youssef Ayari',date_of_birth:'1970-01-01',created_at:'2026-01-01'});
    renderWorkspace();
    expect(await screen.findByText('Unable to estimate risk')).toBeInTheDocument();
    expect(screen.getByText('Insufficient data')).toBeInTheDocument();
    expect(screen.getAllByText('0').length).toBeGreaterThan(0);
  });
});
