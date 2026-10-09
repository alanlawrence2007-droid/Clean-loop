import { NavLink } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { Icon, type IconName } from './Icon';

const ITEMS: { to: string; key: string; icon: IconName; end?: boolean }[] = [
  { to: '/app', key: 'home', icon: 'home', end: true },
  { to: '/app/scan', key: 'scan', icon: 'scan' },
  { to: '/app/facilities', key: 'map', icon: 'map' },
  { to: '/app/report', key: 'report', icon: 'report' },
  { to: '/app/reports', key: 'myReports', icon: 'list' },
];

export function BottomNav() {
  const { t } = useTranslation();
  return (
    <nav aria-label={t('nav.label')} className="fixed inset-x-0 bottom-0 z-20 border-t border-line bg-white">
      <ul className="mx-auto flex max-w-md justify-between px-2">
        {ITEMS.map(({ to, key, icon, end }) => (
          <li key={to} className="flex-1">
            <NavLink to={to} end={end}
              className={({ isActive }) =>
                `flex min-h-[56px] min-w-touch flex-col items-center justify-center gap-0.5 text-xs font-semibold ${isActive ? 'text-forest' : 'text-muted'}`}>
              <Icon name={icon} />
              <span>{t(`nav.${key}`)}</span>
            </NavLink>
          </li>
        ))}
      </ul>
    </nav>
  );
}
