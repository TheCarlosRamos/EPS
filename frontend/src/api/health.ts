import { apiClient } from './client';
import { apiRuntime } from './runtime';
import { createMockHealthSnapshot } from './mock-data';
import type { HealthApiResponse, HealthSnapshot } from './types';

function mapHealthResponse(response: HealthApiResponse): HealthSnapshot {
  return {
    ...response,
    transportMode: 'real',
    source: 'real',
    description:
      'Resposta recebida do backend real. O mesmo contrato continua valido depois do proxy.',
  };
}

export async function getHealthSnapshot(): Promise<HealthSnapshot> {
  // MOCK: usa dados simulados se VITE_USE_MOCK_API=true (padrão em dev)
  // Quando GET /api/health estiver disponível no backend FastAPI:
  // 1. Mudar VITE_USE_MOCK_API=false em .env.local (ou runtime)
  // 2. O else abaixo fará chamada real via apiClient
  // 3. Atualizar integration-map.ts: api-health status → "real"
  if (apiRuntime.useMockApi) {
    return createMockHealthSnapshot();
  }

  const response = await apiClient.get<HealthApiResponse>('/health');
  return mapHealthResponse(response.data);
}
