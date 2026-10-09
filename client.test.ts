import { http, HttpResponse } from 'msw';
import { z } from 'zod';
import { server } from './setup';
import { ApiError, request, tokenStore } from '@/api';

const schema = z.object({ ok: z.boolean() });
const url = '/api/v1/thing';
const abs = (p: string) => new URL(p, 'http://localhost:3000').toString();

beforeEach(() => tokenStore.clear());

describe('api client', () => {
  it('parses a valid response', async () => {
    server.use(http.get(abs(url), () => HttpResponse.json({ ok: true })));
    await expect(request('/thing', { schema })).resolves.toEqual({ ok: true });
  });

  it('rejects a response that breaks the Zod contract', async () => {
    server.use(http.get(abs(url), () => HttpResponse.json({ ok: 'yes' })));
    await expect(request('/thing', { schema })).rejects.toMatchObject({ kind: 'schema' });
  });

  it.each([
    [401, 'unauthenticated'], [403, 'forbidden'], [422, 'validation'], [429, 'rate_limited'], [503, 'unavailable'],
  ])('maps HTTP %i to %s', async (status, kind) => {
    server.use(
      http.get(abs(url), () => new HttpResponse(null, { status })),
      http.post(abs('/api/v1/auth/refresh'), () => new HttpResponse(null, { status: 401 })),
    );
    const err = await request('/thing', { schema }).catch((e) => e);
    expect(err).toBeInstanceOf(ApiError);
    expect(err.kind).toBe(kind);
  });

  it('reads Retry-After on 429', async () => {
    server.use(http.get(abs(url), () => new HttpResponse(null, { status: 429, headers: { 'Retry-After': '7' } })));
    const err = await request('/thing', { schema }).catch((e) => e);
    expect(err.retryAfterSeconds).toBe(7);
  });

  it('refreshes once on 401 and retries with the new token', async () => {
    let calls = 0;
    server.use(
      http.get(abs(url), ({ request: r }) => {
        calls++;
        return r.headers.get('Authorization') === 'Bearer fresh'
          ? HttpResponse.json({ ok: true }) : new HttpResponse(null, { status: 401 });
      }),
      http.post(abs('/api/v1/auth/refresh'), () => HttpResponse.json({ access_token: 'fresh' })),
    );
    await expect(request('/thing', { schema })).resolves.toEqual({ ok: true });
    expect(calls).toBe(2);
    expect(tokenStore.get()).toBe('fresh');
  });

  it('reports network failure as kind "network"', async () => {
    server.use(http.get(abs(url), () => HttpResponse.error()));
    await expect(request('/thing', { schema })).rejects.toMatchObject({ kind: 'network' });
  });
});
