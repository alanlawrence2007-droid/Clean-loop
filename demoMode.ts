/** True only while MSW is serving DEMO data because the real backend is unreachable. */
let demo = false;
export const demoMode = { get: () => demo, set: (v: boolean) => { demo = v; } };
