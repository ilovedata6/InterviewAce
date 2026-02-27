/* ──────────────────────────────────────────────────────────
 * Typed Zod resolver wrapper
 *
 * Works around a Zod v4 minor version mismatch with
 * @hookform/resolvers type signatures. The runtime code
 * in resolvers@5.x fully supports Zod v4 — only the
 * TypeScript overload types are incompatible when the
 * Zod minor version differs from what was compiled against.
 *
 * This wrapper provides a properly typed `zodResolver`
 * that accepts Zod v4 schemas without type errors.
 * ────────────────────────────────────────────────────────── */

import { zodResolver as _zodResolver } from "@hookform/resolvers/zod";
import type { FieldValues, Resolver } from "react-hook-form";
import type { z } from "zod";

/**
 * Type-safe zodResolver wrapper for Zod v4 schemas.
 *
 * Usage:
 *   const form = useForm({ resolver: zodResolver(mySchema) });
 */
// eslint-disable-next-line @typescript-eslint/no-explicit-any
export function zodResolver<T extends z.ZodType<any, any>>(schema: T): Resolver<z.infer<T>> {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  return _zodResolver(schema as any) as unknown as Resolver<z.infer<T>>;
}
