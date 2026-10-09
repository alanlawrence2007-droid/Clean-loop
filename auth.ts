/** Access token lives in memory only (never localStorage). Refresh uses an httpOnly cookie. */
let accessToken: string | null = null;
export const tokenStore = {
  get: () => accessToken,
  set: (t: string | null) => { accessToken = t; },
  clear: () => { accessToken = null; },
};
