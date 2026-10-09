import { NavLink, Outlet } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { Icon } from '@/components/ui/Icon';
import { LanguageSwitch } from '@/components/ui/LanguageSwitch';
import { DemoBadge } from '@/components/ui/DemoBadge';
import { demoMode } from '@/mocks/demoMode';

export function AdminLayout() {
  const { t } = useTranslation();
  return (
    <div className="min-h-screen bg-ground md:grid md:grid-cols-[240px_1fr]">
      <aside className="on-dark bg-forest px-4 py-4 text-white md:min-h-screen">
        <p className="mb-3 font-heading text-lg font-extrabold">{t('app.name')}</p>
        <nav aria-label={t('admin.nav')}>
          <ul className="flex gap-2 md:flex-col">
            <li>
              <NavLink to="/admin" end className={({ isActive }) =>
                `flex min-h-touch items-center gap-2 rounded-full px-4 text-sm font-semibold ${isActive ? 'bg-lime text-forest' : ''}`}>
                <Icon name="dashboard" width={20} height={20} />{t('admin.dashboard')}
              </NavLink>
            </li>
          </ul>
        </nav>
      </aside>
      <div>
        <header className="flex items-center justify-end gap-2 px-6 py-3">
          {demoMode.get() && <DemoBadge />}<LanguageSwitch />
        </header>
        <main id="main" className="px-6 pb-8"><Outlet /></main>
      </div>
    </div>
  );
}
