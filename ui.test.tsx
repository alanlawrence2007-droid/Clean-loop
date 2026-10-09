import { render, screen } from '@testing-library/react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { BottomNav } from '@/components/ui/BottomNav';
import { ConfidenceBar } from '@/components/ui/ConfidenceBar';
import { RoleGuard } from '@/components/layout/RoleGuard';
import { AuthContext } from '@/app/auth';
import type { User } from '@/api';

describe('BottomNav', () => {
  it('has the five citizen destinations as real links and marks the current one', () => {
    render(<MemoryRouter initialEntries={['/app/scan']}><BottomNav /></MemoryRouter>);
    const links = screen.getAllByRole('link');
    expect(links).toHaveLength(5);
    expect(screen.getByRole('link', { name: /scan/i })).toHaveAttribute('aria-current', 'page');
    expect(screen.getByRole('link', { name: /my reports/i })).toHaveAttribute('href', '/app/reports');
  });
});

describe('ConfidenceBar', () => {
  it('is labelled as an AI estimate with its percentage', () => {
    render(<ConfidenceBar value={0.72} />);
    expect(screen.getByRole('meter')).toHaveAttribute('aria-valuenow', '72');
    expect(screen.getAllByText(/AI estimate/i).length).toBeGreaterThan(0);
  });
});

function renderAdmin(user: User | null, loading = false) {
  render(
    <AuthContext.Provider value={{ user, loading }}>
      <MemoryRouter initialEntries={['/admin']}>
        <Routes>
          <Route path="/app" element={<p>citizen home</p>} />
          <Route path="/admin" element={<RoleGuard roles={['admin']}><p>admin area</p></RoleGuard>} />
        </Routes>
      </MemoryRouter>
    </AuthContext.Provider>,
  );
}

describe('RoleGuard', () => {
  it('lets an admin in', () => {
    renderAdmin({ id: '1', role: 'admin' });
    expect(screen.getByText('admin area')).toBeInTheDocument();
  });
  it('shows a forbidden message to a citizen', () => {
    renderAdmin({ id: '2', role: 'citizen' });
    expect(screen.getByRole('alert')).toHaveTextContent(/access/i);
    expect(screen.queryByText('admin area')).not.toBeInTheDocument();
  });
  it('sends anonymous visitors to /app', () => {
    renderAdmin(null);
    expect(screen.getByText('citizen home')).toBeInTheDocument();
  });
  it('waits while auth is loading', () => {
    renderAdmin(null, true);
    expect(screen.getByRole('status')).toBeInTheDocument();
  });
});
