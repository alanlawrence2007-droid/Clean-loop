import { Outlet } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { BottomNav } from '@/components/ui/BottomNav';
import { LanguageSwitch } from '@/components/ui/LanguageSwitch';
import { DemoBadge } from '@/components/ui/DemoBadge';
import { demoMode } from '@/mocks/demoMode';

export function CitizenLayout() {
  const { t } = useTranslation();
  return (
    <div className="mx-auto min-h-screen max-w-md bg-ground pb-20">
      {demoMode.get() && (
        <p role="status" className="bg-sanitary-tint px-4 py-2 text-sm font-semibold text-sanitary-ink">{t('demo.banner')}</p>
      )}
      <header className="flex items-center justify-between px-4 py-3">
        <span className="font-heading text-lg font-extrabold text-forest">{t('app.name')}</span>
        <div className="flex items-center gap-2">{demoMode.get() && <DemoBadge />}<LanguageSwitch /></div>
      </header>
      <main id="main" className="px-4"><Outlet /></main>
      <BottomNav />
    </div>
  );
}
