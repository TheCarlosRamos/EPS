/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_URL?: string;
  readonly VITE_USE_MOCK_API?: string;
  readonly VITE_AUTH_REFRESH_ENDPOINT?: string;
  readonly VITE_API_TIMEOUT_MS?: string;
  readonly VITE_MOCK_API_DELAY_MS?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
