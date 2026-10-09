import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import './i18n';
import './styles/index.css';
import { App } from './app/App';
import { AuthProvider } from './app/auth';
import { API_BASE } from './api';
import { demoMode } from './mocks/demoMode';

const queryClient = new QueryClient({
  defaultOptions: { queries: { retry: 1, refetchOnWindowFocus: false } },
});

/** Real API first. Only if it is unreachable (network error / 502-504) start labelled MSW demo data. */
async function backendReachable(): Promise<boolean> {
  try {
    const res = await fetch(`${API_BASE}/health`, { signal: AbortSignal.timeout(2500) });
    return ![502, 503, 504].includes(res.status);
  } catch {
    return false;
  }
}

async function bootstrap() {
  if (import.meta.env.VITE_FORCE_MOCKS === 'true' || !(await backendReachable())) {
    const { worker } = await import('./mocks/browser');
    await worker.start({ onUnhandledRequest: 'bypass', quiet: true });
    demoMode.set(true);
  }
  ReactDOM.createRoot(document.getElementById('root')!).render(
    <React.StrictMode>
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <AuthProvider><App /></AuthProvider>
        </BrowserRouter>
      </QueryClientProvider>
    </React.StrictMode>,
  );
}
void bootstrap();
