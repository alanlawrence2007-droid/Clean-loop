// ⚠️ DEMO DATA ONLY. These handlers never run when the real backend responds.
// Role for the demo session: localStorage 'cleanloop.demoRole' = 'citizen' | 'admin'.
import { http, HttpResponse } from 'msw';

const BASE = '/api/v1';

function demoRole(): 'citizen' | 'admin' | null {
  try {
    const r = localStorage.getItem('cleanloop.demoRole');
    return r === 'admin' || r === 'citizen' ? r : null;
  } catch { return null; }
}

export const handlers = [
  http.get(`${BASE}/health`, () => HttpResponse.json({ status: 'demo' })),
  http.post(`${BASE}/auth/refresh`, () => {
    const role = demoRole();
    return role ? HttpResponse.json({ access_token: `demo-${role}` }) : new HttpResponse(null, { status: 401 });
  }),
  http.get(`${BASE}/auth/me`, ({ request }) => {
    const role = request.headers.get('Authorization')?.replace('Bearer demo-', '');
    if (role !== 'admin' && role !== 'citizen') return new HttpResponse(null, { status: 401 });
    return HttpResponse.json({ id: 'demo-user', name: 'Demo user', role, language: 'en' });
  }),
];
