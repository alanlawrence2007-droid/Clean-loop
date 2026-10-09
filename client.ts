import { z } from 'zod';
import { tokenStore } from './auth';
import { TokenSchema } from './schemas';

export const API_BASE: string = import.meta.env.VITE_API_BASE ?? '/api/v1';

export type ApiErrorKind =
  | 'unauthenticated' | 'forbidden' | 'validation' | 'rate_limited'
  | 'unavailable' | 'network' | 'schema' | 'unknown';

export class ApiError extends Error {
  constructor(
    public status: number,
    public kind: ApiErrorKind,
    message: string,
    public details?: unknown,
    public retryAfterSeconds?: number,
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

function kindFromStatus(status: number): ApiErrorKind {
  if (status === 401) return 'unauthenticated';
  if (status === 403) return 'forbidden';
  if (status === 422) return 'validation';
  if (status === 429) return 'rate_limited';
  if (status === 503) return 'unavailable';
  return 'unknown';
}

let refreshing: Promise<boolean> | null = null;

/** One refresh at a time; concurrent 401s share the same attempt. */
export function refreshSession(): Promise<boolean> {
  refreshing ??= (async () => {
    try {
      const res = await fetch(`${API_BASE}/auth/refresh`, { method: 'POST', credentials: 'include' });
      if (!res.ok) { tokenStore.clear(); return false; }
      const parsed = TokenSchema.safeParse(await res.json());
      if (!parsed.success) { tokenStore.clear(); return false; }
      tokenStore.set(parsed.data.access_token);
      return true;
    } catch {
      return false;
    } finally {
      refreshing = null;
    }
  })();
  return refreshing;
}

export interface RequestOptions<T> {
  method?: 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE';
  /** Plain objects are sent as JSON, FormData as multipart. */
  body?: unknown;
  schema: z.ZodType<T>;
  auth?: boolean;
  signal?: AbortSignal;
}

export async function request<T>(path: string, opts: RequestOptions<T>, retried = false): Promise<T> {
  const { method = 'GET', body, schema, auth = true, signal } = opts;
  const headers: Record<string, string> = { Accept: 'application/json' };
  const token = tokenStore.get();
  if (auth && token) headers.Authorization = `Bearer ${token}`;
  let payload: BodyInit | undefined;
  if (body instanceof FormData) payload = body;
  else if (body !== undefined) { headers['Content-Type'] = 'application/json'; payload = JSON.stringify(body); }

  let res: Response;
  try {
    res = await fetch(`${API_BASE}${path}`, { method, headers, body: payload, credentials: 'include', signal });
  } catch (err) {
    if ((err as Error).name === 'AbortError') throw err;
    throw new ApiError(0, 'network', 'Network unreachable');
  }

  if (res.status === 401 && auth && !retried && (await refreshSession())) {
    return request(path, opts, true);
  }

  if (!res.ok) {
    let details: unknown;
    try { details = await res.json(); } catch { /* non-JSON error body */ }
    const retryAfter = Number(res.headers.get('Retry-After'));
    throw new ApiError(res.status, kindFromStatus(res.status), `HTTP ${res.status}`, details,
      Number.isFinite(retryAfter) && retryAfter > 0 ? retryAfter : undefined);
  }

  const json: unknown = res.status === 204 ? undefined : await res.json();
  const parsed = schema.safeParse(json);
  if (!parsed.success) throw new ApiError(res.status, 'schema', 'Response did not match contract', parsed.error.flatten());
  return parsed.data;
}

/** Maps an error to the i18n key under `errors.*`. */
export function errorMessageKey(err: unknown): string {
  const kind = err instanceof ApiError ? err.kind : 'unknown';
  return `errors.${kind === 'rate_limited' ? 'rateLimited' : kind}`;
}
