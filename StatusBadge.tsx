import type { ReactNode } from 'react';

export type StatusTone = 'verified' | 'stale' | 'unverified' | 'info';
const TONES: Record<StatusTone, string> = {
  verified: 'bg-wet-tint text-wet-ink',
  stale: 'bg-sanitary-tint text-sanitary-ink',
  unverified: 'bg-line text-ink',
  info: 'bg-dry-tint text-dry-ink',
};

export function StatusBadge({ tone, children }: { tone: StatusTone; children: ReactNode }) {
  return <span className={`inline-flex min-h-[28px] items-center rounded-full px-3 text-xs font-bold ${TONES[tone]}`}>{children}</span>;
}
