import { beforeEach, describe, expect, it, vi } from 'vitest';

const { getMock, createMockHealthSnapshotMock } = vi.hoisted(() => ({
  getMock: vi.fn(),
  createMockHealthSnapshotMock: vi.fn(),
}));

vi.mock('./client', () => ({
  apiClient: {
    get: getMock,
  },
}));

vi.mock('./runtime', () => ({
  apiRuntime: {
    useMockApi: true,
  },
}));

vi.mock('./mock-data', () => ({
  createMockHealthSnapshot: createMockHealthSnapshotMock,
}));

import { getHealthSnapshot } from './health';
import { apiRuntime } from './runtime';

const mutableRuntime = apiRuntime as unknown as { useMockApi: boolean };

describe('getHealthSnapshot', () => {
  beforeEach(() => {
    getMock.mockReset();
    createMockHealthSnapshotMock.mockReset();
  });

  it('retorna mock quando useMockApi=true', async () => {
    const mockSnapshot = {
      service: 'buscador-osint-api',
      status: 'ok' as const,
      timestamp: '2026-04-22T12:00:00.000Z',
      version: 'mock',
      transportMode: 'mock' as const,
      source: 'mock' as const,
      description: 'mock',
    };

    mutableRuntime.useMockApi = true;
    createMockHealthSnapshotMock.mockReturnValue(mockSnapshot);

    const result = await getHealthSnapshot();

    expect(createMockHealthSnapshotMock).toHaveBeenCalledTimes(1);
    expect(getMock).not.toHaveBeenCalled();
    expect(result).toEqual(mockSnapshot);
  });

  it('consulta backend e mapeia resposta quando useMockApi=false', async () => {
    mutableRuntime.useMockApi = false;
    getMock.mockResolvedValue({
      data: {
        service: 'buscador-osint-api',
        status: 'ok',
        timestamp: '2026-04-22T12:00:00.000Z',
        version: '1.0.0',
      },
    });

    const result = await getHealthSnapshot();

    expect(getMock).toHaveBeenCalledWith('/health');
    expect(result).toEqual({
      service: 'buscador-osint-api',
      status: 'ok',
      timestamp: '2026-04-22T12:00:00.000Z',
      version: '1.0.0',
      transportMode: 'real',
      source: 'real',
      description:
        'Resposta recebida do backend real. O mesmo contrato continua valido depois do proxy.',
    });
  });
});
