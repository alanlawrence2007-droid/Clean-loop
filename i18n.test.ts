import en from '@/i18n/locales/en.json';
import hi from '@/i18n/locales/hi.json';
import mr from '@/i18n/locales/mr.json';

function keys(obj: Record<string, unknown>, prefix = ''): string[] {
  return Object.entries(obj).flatMap(([k, v]) =>
    typeof v === 'object' && v !== null ? keys(v as Record<string, unknown>, `${prefix}${k}.`) : [`${prefix}${k}`]);
}

describe('locales', () => {
  const base = keys(en).sort();
  it('hi has exactly the same keys as en', () => expect(keys(hi).sort()).toEqual(base));
  it('mr has exactly the same keys as en', () => expect(keys(mr).sort()).toEqual(base));
  it('no value is empty', () => {
    for (const l of [en, hi, mr]) for (const k of keys(l)) {
      const v = k.split('.').reduce<any>((o, p) => o[p], l);
      expect(String(v).trim()).not.toBe('');
    }
  });
});
