import axios from 'axios';

function getErrorMessageByStatus(status: number | null): string {
  if (status === 401) {
    return 'Sessao expirada. A autenticacao precisa ser renovada.';
  }

  if (status === 403) {
    return 'Acesso negado para este recurso.';
  }

  if (status !== null && status >= 500) {
    return 'Falha temporaria no backend. Tente novamente em instantes.';
  }

  return 'Falha na comunicacao com a API.';
}

export class ApiError extends Error {
  readonly status: number | null;
  readonly code: string;
  readonly endpoint: string | null;
  readonly method: string | null;
  readonly retryable: boolean;
  readonly details: unknown;

  constructor(options: {
    message: string;
    status: number | null;
    code: string;
    endpoint: string | null;
    method: string | null;
    retryable: boolean;
    details: unknown;
  }) {
    super(options.message);
    this.name = 'ApiError';
    this.status = options.status;
    this.code = options.code;
    this.endpoint = options.endpoint;
    this.method = options.method;
    this.retryable = options.retryable;
    this.details = options.details;
  }
}

export function normalizeApiError(error: unknown): ApiError {
  if (error instanceof ApiError) {
    return error;
  }

  if (axios.isAxiosError(error)) {
    const status = error.response?.status ?? null;
    const method = error.config?.method?.toUpperCase() ?? null;
    const endpoint = error.config?.url ?? null;

    return new ApiError({
      message: getErrorMessageByStatus(status),
      status,
      code:
        error.code || (status !== null ? `HTTP_${status}` : 'NETWORK_ERROR'),
      endpoint,
      method,
      retryable: status === null || status >= 500,
      details: error.response?.data ?? error.message,
    });
  }

  if (error instanceof Error) {
    return new ApiError({
      message: error.message,
      status: null,
      code: 'UNEXPECTED_ERROR',
      endpoint: null,
      method: null,
      retryable: false,
      details: error,
    });
  }

  return new ApiError({
    message: 'Falha inesperada na comunicacao com a API.',
    status: null,
    code: 'UNEXPECTED_ERROR',
    endpoint: null,
    method: null,
    retryable: false,
    details: error,
  });
}
