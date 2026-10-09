# Clean-Loop frontend

Stage 1 (Foundation) of the Clean-Loop spec.

    npm install
    npm run dev      # proxies /api/v1 to VITE_BACKEND_URL (default http://localhost:8000)
    npm test
    npm run build

## Demo mode
On startup the app probes `/api/v1/health`. If the backend is unreachable (network error or 502/503/504),
MSW starts and a "Demo data" banner/badge is shown. Set `VITE_FORCE_MOCKS=true` to force it.
To try the role guard in demo mode: `localStorage.setItem('cleanloop.demoRole', 'admin')` and reload.

## Decisions to confirm
- Marketing site at `/`, citizen app under `/app/*` (spec mapped both to `/`).
- `/app/reports` (My reports list) added for the bottom nav; not in the spec's route table.
- Auth endpoints assumed: `POST /auth/refresh` (httpOnly cookie → `{access_token}`), `GET /auth/me` → `{id, role, ...}`.
- Roles assumed: `citizen | ward_officer | admin`. `/admin` allows `admin` and `ward_officer`.
- Language persists to localStorage; profile sync waits for a confirmed profile endpoint.

## Not yet built
Home/Scan/Result (stage 2), Facilities/Collection (3), Report/Tracking/offline queue (4), Admin dashboard (5),
Marketing, Playwright, a11y pass (6). `idb` is installed but unused until stage 4.
