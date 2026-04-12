/**
 * Backend URL.
 * - Local dev: Vite on :5173 and Flask on :5001 → full URL (same hostname as the tab).
 * - Production (Flask serves `static/spa/`): leave unset → "" so requests hit the same origin.
 */
export const API_BASE =
  import.meta.env.VITE_API_URL ||
  (import.meta.env.DEV ? "http://localhost:5001" : "");
