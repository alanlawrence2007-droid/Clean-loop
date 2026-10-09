import { z } from 'zod';

export const WasteCategory = z.enum(['wet', 'dry', 'ewaste', 'hazardous', 'sanitary', 'reuse']);
export type WasteCategory = z.infer<typeof WasteCategory>;

export const UserSchema = z.object({
  id: z.string(),
  name: z.string().nullable().optional(),
  role: z.enum(['citizen', 'ward_officer', 'admin']),
  language: z.enum(['en', 'hi', 'mr']).optional(),
});
export type User = z.infer<typeof UserSchema>;

export const TokenSchema = z.object({ access_token: z.string() });

export const RuleSource = z.object({
  locality: z.string(),
  rule_version: z.string(),
  updated_at: z.string(),
  source: z.string(),
});

export const ClassifyResultSchema = z.object({
  category: WasteCategory,
  material: z.string(),
  confidence: z.number().min(0).max(1),
  needs_clarification: z.boolean().optional(),
  clarifying_question: z.string().nullable().optional(),
  rule: RuleSource.nullable(),
  steps: z.array(z.string()).default([]),
  warning: z.string().nullable().optional(),
});
export type ClassifyResult = z.infer<typeof ClassifyResultSchema>;

export const ApiErrorBodySchema = z.object({ detail: z.unknown().optional() }).passthrough();
export const HealthSchema = z.object({ status: z.string() });
