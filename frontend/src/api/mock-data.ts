import type { SessionTokens } from './session';
import type { HealthSnapshot } from './types';

/**
 * MOCK: dados de exemplo
 * 
 * Quando o backend estiver pronto:
 * 1. Remover este arquivo
 * 2. Em client.ts: implementar fluxo real de POST /auth/refresh com credenciais
 * 3. Em health.ts: mudar VITE_USE_MOCK_API=false para chamar endpoint real
 * 4. Atualizar integration-map.ts: marcar endpoints como "real"
 */

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
