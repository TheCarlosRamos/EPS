import type { SessionTokens } from './session';
import type { HealthSnapshot } from './types';

export const mockSessionTokens: SessionTokens = {
  accessToken: 'mock-access-token',
  refreshToken: 'mock-refresh-token',
};

export function createMockHealthSnapshot(): HealthSnapshot {
  return {
    service: 'buscador-osint-api',
    status: 'ok',
    timestamp: new Date().toISOString(),
    version: 'mock',
    transportMode: 'mock',
    source: 'mock',
    description:
      'Resposta simulada da camada HTTP enquanto o backend e o proxy ainda nao estao prontos.',
  };
}
