import { request } from './client';
import { HealthSchema, UserSchema } from './schemas';

export const api = {
  health: () => request('/health', { schema: HealthSchema, auth: false }),
  me: () => request('/auth/me', { schema: UserSchema }),
};
export * from './client';
export * from './schemas';
export { tokenStore } from './auth';
