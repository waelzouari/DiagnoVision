import {QueryClient,QueryClientProvider} from '@tanstack/react-query';
import {fireEvent,render,screen} from '@testing-library/react';
import {MemoryRouter,Route,Routes} from 'react-router-dom';
import {describe,expect,it,vi} from 'vitest';
import {RecordingDemoPage} from '../src/features/consultations/RecordingDemoPage';
import {patientsRepo} from '../src/lib/repositories';

const cancel=vi.fn();
vi.mock('../src/hooks/useRecorder',()=>({useRecorder:()=>({state:'idle',seconds:0,blob:null,mime:'audio/webm',supported:true,start:vi.fn(),pause:vi.fn(),resume:vi.fn(),stop:vi.fn(),cancel})}));
vi.mock('../src/lib/repositories',()=>({patientsRepo:{one:vi.fn()}}));

describe('frontend-only consultation recording demo',()=>{
  it('requires consent and demonstrates raw-to-clean clinical data',async()=>{
    vi.mocked(patientsRepo.one).mockResolvedValue({id:'patient-1',full_name:'Leila Mansour',date_of_birth:'1970-01-01',created_at:'2026-01-01'});
    const client=new QueryClient({defaultOptions:{queries:{retry:false}}});
    render(<QueryClientProvider client={client}><MemoryRouter initialEntries={['/patients/patient-1/recording-demo']}><Routes><Route path="/patients/:patientId/recording-demo" element={<RecordingDemoPage/>}/></Routes></MemoryRouter></QueryClientProvider>);
    expect(await screen.findByRole('heading',{name:'Consultation recording demo'})).toBeInTheDocument();
    const start=screen.getByRole('button',{name:/start recording/i});
    expect(start).toBeDisabled();
    fireEvent.click(screen.getByRole('checkbox',{name:/patient recording consent confirmed/i}));
    expect(start).toBeEnabled();
    fireEvent.click(screen.getByRole('button',{name:/use jury demo sample/i}));
    expect(screen.getByRole('heading',{name:/raw transcript/i})).toBeInTheDocument();
    fireEvent.click(screen.getByRole('button',{name:/run data cleaning/i}));
    expect(await screen.findByRole('heading',{name:/cleaned transcript/i},{timeout:1500})).toBeInTheDocument();
    expect(screen.getAllByText('Chest pain denied')).toHaveLength(2);
    expect(screen.getByText(/pain intensity and relevant medical history remain unknown/i)).toBeInTheDocument();
    expect(screen.getByRole('heading',{name:/data-cleaning report/i})).toBeInTheDocument();
    expect(screen.getByText('Negation preservation')).toBeInTheDocument();
    expect(screen.getByText('Values and units normalized')).toBeInTheDocument();
    expect(screen.getByText(/no clinical accuracy score is claimed/i)).toBeInTheDocument();
  });
});
