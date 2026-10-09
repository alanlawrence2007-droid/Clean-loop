import { Route, Routes } from 'react-router-dom';
import { CitizenLayout } from '@/components/layout/CitizenLayout';
import { AdminLayout } from '@/components/layout/AdminLayout';
import { RoleGuard } from '@/components/layout/RoleGuard';
import { Placeholder } from './routes/Placeholder';

export function App() {
  return (
    <Routes>
      {/* Marketing site is public at "/"; the citizen app lives under /app (see README). */}
      <Route path="/" element={<main className="p-6"><Placeholder titleKey="pages.marketing" stage={6} /></main>} />
      <Route path="/try" element={<main className="p-6"><Placeholder titleKey="pages.try" stage={6} /></main>} />
      <Route path="/app" element={<CitizenLayout />}>
        <Route index element={<Placeholder titleKey="pages.home" stage={2} />} />
        <Route path="scan" element={<Placeholder titleKey="pages.scan" stage={2} />} />
        <Route path="result" element={<Placeholder titleKey="pages.result" stage={2} />} />
        <Route path="facilities" element={<Placeholder titleKey="pages.facilities" stage={3} />} />
        <Route path="collection" element={<Placeholder titleKey="pages.collection" stage={3} />} />
        <Route path="report" element={<Placeholder titleKey="pages.report" stage={4} />} />
        <Route path="reports" element={<Placeholder titleKey="pages.reports" stage={4} />} />
        <Route path="reports/:id" element={<Placeholder titleKey="pages.reportDetail" stage={4} />} />
      </Route>
      <Route path="/admin" element={<RoleGuard roles={['admin', 'ward_officer']}><AdminLayout /></RoleGuard>}>
        <Route index element={<Placeholder titleKey="pages.admin" stage={5} />} />
      </Route>
    </Routes>
  );
}
