import {QueryClient, QueryClientProvider} from '@tanstack/react-query';
import {cleanup, fireEvent, render, screen, waitFor} from '@testing-library/react';
import {MemoryRouter} from 'react-router-dom';
import {afterEach, describe, expect, it, vi} from 'vitest';
import {DashboardPage} from '../src/features/dashboard/DashboardPage';
import {dashboardRepo} from '../src/lib/repositories';
import type {DashboardOverview} from '../src/types/api';

vi.mock('../src/lib/repositories', () => ({
  dashboardRepo: {overview: vi.fn()},
}));

const overviewMock = vi.mocked(dashboardRepo.overview);

const populatedOverview: DashboardOverview = {
  patient_count: 12,
  pending_reviews: 3,
  recent_consultations: [
    {
      id: 'consultation-1',
      patient_id: 'patient-1',
      mode: 'manual',
      status: 'approved',
      occurred_at: '2026-11-21T09:30:00Z',
    },
  ],
  latest_analyses: [
    {
      id: 'analysis-1',
      patient_id: 'patient-1',
      status: 'completed',
      summary: 'Synthetic longitudinal summary.',
      model_version: 'mock-v1',
      created_at: '2026-11-21T10:00:00Z',
    },
  ],
  relevant_observations: [
    {
      id: 'observation-1',
      patient_id: 'patient-1',
      code: 'heart-rate',
      name: 'Heart rate',
      value: 72,
      unit: 'bpm',
      observed_at: '2026-11-21T08:00:00Z',
      status: 'approved',
      source_reference: 'consultation-1',
    },
  ],
};

function renderDashboard() {
  const queryClient = new QueryClient({
    defaultOptions: {queries: {retry: false}},
  });

  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter>
        <DashboardPage />
      </MemoryRouter>
    </QueryClientProvider>,
  );
}

afterEach(() => {
  cleanup();
  vi.clearAllMocks();
});

describe('clinical dashboard', () => {
  it('renders the population metrics, recent work and clinical safety notice', async () => {
    overviewMock.mockResolvedValue(populatedOverview);

    renderDashboard();

    expect(await screen.findByRole('heading', {name: /clinical overview/i})).toBeInTheDocument();
    expect(screen.getByText('Active patients')).toBeInTheDocument();
    expect(screen.getByText('12')).toBeInTheDocument();
    expect(screen.getByText('Pending reviews')).toBeInTheDocument();
    expect(screen.getByText('3')).toBeInTheDocument();
    expect(screen.getByRole('link', {name: /add patient/i})).toHaveAttribute('href', '/patients/new');
    expect(screen.getByRole('link', {name: /consultation record/i})).toHaveAttribute(
      'href',
      '/consultations/consultation-1',
    );
    expect(screen.getByText('approved')).toBeInTheDocument();
    expect(screen.getByText('Heart rate')).toBeInTheDocument();
    expect(screen.getByText('72 bpm')).toBeInTheDocument();
    expect(screen.getByRole('link', {name: /patient record for heart rate/i})).toHaveAttribute(
      'href',
      '/patients/patient-1',
    );
    expect(screen.getByLabelText('Clinical safety notice')).toHaveTextContent(
      /AI outputs remain drafts until physician validation/i,
    );
  });

  it('shows explicit empty states when no approved observations or consultations exist', async () => {
    overviewMock.mockResolvedValue({
      ...populatedOverview,
      patient_count: 0,
      pending_reviews: 0,
      recent_consultations: [],
      latest_analyses: [],
      relevant_observations: [],
    });

    renderDashboard();

    expect(await screen.findByText('No approved indicators')).toBeInTheDocument();
    expect(screen.getByText('No consultations yet')).toBeInTheDocument();
  });

  it('lets the clinician retry after a dashboard request fails', async () => {
    overviewMock
      .mockRejectedValueOnce(new Error('Dashboard unavailable'))
      .mockResolvedValueOnce(populatedOverview);

    renderDashboard();

    expect(await screen.findByText('Unable to load this view')).toBeInTheDocument();
    expect(screen.getByText(/Dashboard unavailable/i)).toBeInTheDocument();

    fireEvent.click(screen.getByRole('button', {name: /try again/i}));

    await waitFor(() => expect(overviewMock).toHaveBeenCalledTimes(2));
    expect(await screen.findByRole('heading', {name: /clinical overview/i})).toBeInTheDocument();
  });
});
