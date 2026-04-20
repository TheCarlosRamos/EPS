import axios, { AxiosHeaders, type InternalAxiosRequestConfig } from 'axios';

import { ApiError, normalizeApiError } from './errors';
import { apiRuntime } from './runtime';
import {
  clearSessionTokens,
  getSessionTokens,
  setSessionTokens,
} from './session';
import type { SessionTokens } from './session';
import { mockSessionTokens } from './mock-data';

const contentTypeHeader = { 'Content-Type': 'application/json' };

const refreshTransport = axios.create({
  baseURL: apiRuntime.baseUrl,
  timeout: apiRuntime.timeoutMs,
  headers: contentTypeHeader,
});

export const apiClient = axios.create({
  baseURL: apiRuntime.baseUrl,
  timeout: apiRuntime.timeoutMs,
  headers: contentTypeHeader,
});

let refreshPromise: Promise<SessionTokens> | null = null;

function delay(milliseconds: number): Promise<void> {
  return new Promise((resolve) => {
    window.setTimeout(resolve, milliseconds);
  });
}

function shouldTryRefreshToken(config: InternalAxiosRequestConfig): boolean {
  const requestUrl = config.url?.split('?')[0] ?? '';
  return requestUrl !== apiRuntime.refreshEndpoint;
}

async function refreshSessionTokens(): Promise<SessionTokens> {
  // MOCK: retorna dados simulados se useMockApi ativo
  // Quando backend estiver pronto:
  // 1. Remover este if/else
  // 2. Implementar POST para /auth/refresh com { refreshToken } real
  // 3. Guardar novo accessToken em localStorage via setSessionTokens()
  if (apiRuntime.useMockApi) {
    await delay(apiRuntime.mockDelayMs);
    return mockSessionTokens;
  }

  const { refreshToken } = getSessionTokens();
  if (!refreshToken) {
    throw new ApiError({
      message: 'Nao ha refresh token salvo para renovar a sessao.',
      status: 401,
      code: 'MISSING_REFRESH_TOKEN',
      endpoint: apiRuntime.refreshEndpoint,
      method: 'POST',
      retryable: false,
      details: null,
    });
  }

  const response = await refreshTransport.post<SessionTokens>(
    apiRuntime.refreshEndpoint,
    {
      refreshToken,
    },
  );

  return response.data;
}

apiClient.interceptors.request.use((config) => {
  config.headers = AxiosHeaders.from(config.headers);
  const { accessToken } = getSessionTokens();

  if (accessToken) {
    config.headers.set('Authorization', `Bearer ${accessToken}`);
  }

  config.headers.set('X-Requested-With', 'XMLHttpRequest');

  return config;
});

apiClient.interceptors.response.use(
  (response) => response,
  async (error: unknown) => {
    const normalizedError = normalizeApiError(error);
    const originalConfig =
      axios.isAxiosError(error) && error.config
        ? (error.config as InternalAxiosRequestConfig & { _retry?: boolean })
        : null;

    if (
      normalizedError.status === 401 &&
      originalConfig !== null &&
      originalConfig._retry !== true &&
      shouldTryRefreshToken(originalConfig)
    ) {
      originalConfig._retry = true;

      try {
        if (refreshPromise === null) {
          refreshPromise = refreshSessionTokens().finally(() => {
            refreshPromise = null;
          });
        }

        const sessionTokens = await refreshPromise;
        setSessionTokens(sessionTokens);
        originalConfig.headers = AxiosHeaders.from(originalConfig.headers);
        originalConfig.headers.set(
          'Authorization',
          `Bearer ${sessionTokens.accessToken}`,
        );

        return apiClient.request(originalConfig);
      } catch {
        clearSessionTokens();
      }
    }

    return Promise.reject(normalizedError);
  },
);
