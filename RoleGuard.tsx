import { Navigate, useLocation } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useAuth } from '@/app/auth';
import type { User } from '@/api';
import type { ReactNode } from 'react';

export function RoleGuard({ roles, children }: { roles: User['role'][]; children: ReactNode }) {
  const { user, loading } = useAuth();
  const { t } = useTranslation();
  const location = useLocation();
  if (loading) return <p role="status" className="p-6">{t('common.loading')}</p>;
  if (!user) return <Navigate to="/app" replace state={{ from: location.pathname }} />;
  if (!roles.includes(user.role)) {
    return (
      <div role="alert" className="mx-auto max-w-md p-6">
        <h1 className="text-xl font-bold">{t('errors.forbidden')}</h1>
      </div>
    );
  }
  return <>{children}</>;
}
