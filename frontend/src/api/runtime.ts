function parseBoolean(value: string | undefined, fallback: boolean): boolean {
  if (value === undefined) {
    return fallback;
  }

  return ['1', 'true', 'yes', 'on'].includes(value.trim().toLowerCase());
}

function parseNumber(value: string | undefined, fallback: number): number {
  if (value === undefined) {
    return fallback;
  }

  const parsedValue = Number(value);
  return Number.isFinite(parsedValue) ? parsedValue : fallback;
}

export const apiRuntime = {
  baseUrl: import.meta.env.VITE_API_URL?.trim() || '/api',
  useMockApi: parseBoolean(
    import.meta.env.VITE_USE_MOCK_API,
    import.meta.env.DEV,
  ),
  refreshEndpoint:
    import.meta.env.VITE_AUTH_REFRESH_ENDPOINT?.trim() || '/auth/refresh',
  timeoutMs: parseNumber(import.meta.env.VITE_API_TIMEOUT_MS, 10_000),
  mockDelayMs: parseNumber(import.meta.env.VITE_MOCK_API_DELAY_MS, 250),
} as const;
