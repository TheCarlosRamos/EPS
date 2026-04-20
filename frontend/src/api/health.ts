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
  if (apiRuntime.useMockApi) {
    return createMockHealthSnapshot();
  }

  const response = await apiClient.get<HealthApiResponse>('/health');
  return mapHealthResponse(response.data);
}
