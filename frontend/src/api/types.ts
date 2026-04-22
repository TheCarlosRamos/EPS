export type TransportMode = 'mock' | 'real';

export interface HealthApiResponse {
  service: string;
  status: 'ok' | 'degraded' | 'error';
  timestamp: string;
  version?: string;
}

export interface HealthSnapshot extends HealthApiResponse {
  transportMode: TransportMode;
  source: TransportMode;
  description: string;
}
