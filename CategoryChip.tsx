import { useTranslation } from 'react-i18next';
import type { WasteCategory } from '@/api';

// Full class strings so Tailwind can see them.
const STYLES: Record<WasteCategory, string> = {
  wet: 'bg-wet-tint text-wet-ink',
  dry: 'bg-dry-tint text-dry-ink',
  ewaste: 'bg-ewaste-tint text-ewaste-ink',
  hazardous: 'bg-hazardous-tint text-hazardous-ink',
  sanitary: 'bg-sanitary-tint text-sanitary-ink',
  reuse: 'bg-reuse-tint text-reuse-ink',
};
const DOT: Record<WasteCategory, string> = {
  wet: 'bg-wet', dry: 'bg-dry', ewaste: 'bg-ewaste', hazardous: 'bg-hazardous', sanitary: 'bg-sanitary', reuse: 'bg-reuse',
};

export function CategoryChip({ category }: { category: WasteCategory }) {
  const { t } = useTranslation();
  return (
    <span className={`inline-flex min-h-[32px] items-center gap-2 rounded-full px-3 text-sm font-semibold ${STYLES[category]}`}>
      <span aria-hidden className={`h-2.5 w-2.5 rounded-full ${DOT[category]}`} />
      {t(`category.${category}`)}
    </span>
  );
}
