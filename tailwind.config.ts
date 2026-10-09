import type { Config } from 'tailwindcss';

export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      fontFamily: {
        heading: ['Sora', 'Noto Sans Devanagari', 'system-ui', 'sans-serif'],
        sans: ['Manrope', 'Noto Sans Devanagari', 'system-ui', 'sans-serif'],
      },
      colors: {
        forest: { DEFAULT: '#0B3D32', 2: '#10503F' },
        lime: '#C6F36B',
        ground: '#F2F5F1',
        ink: '#10231D',
        muted: '#4B6158',
        line: '#DCE5E0',
        // waste categories: solid / tint / ink (dark text)
        wet: { DEFAULT: '#2E9E5B', tint: '#DFF3E7', ink: '#0B4A28' },
        dry: { DEFAULT: '#2D6CDF', tint: '#E1EBFC', ink: '#123E8F' },
        ewaste: { DEFAULT: '#7B4FD6', tint: '#ECE4FA', ink: '#3D1E8A' },
        hazardous: { DEFAULT: '#D9402F', tint: '#FBE3E0', ink: '#8A1F14' },
        sanitary: { DEFAULT: '#E08A00', tint: '#FFEFD2', ink: '#6B4000' },
        reuse: { DEFAULT: '#0E8F9B', tint: '#DDF3F5', ink: '#0A5760' },
      },
      borderRadius: { card: '20px', hero: '32px', sheet: '28px' },
      minHeight: { touch: '44px' },
      minWidth: { touch: '44px' },
    },
  },
  plugins: [],
} satisfies Config;
