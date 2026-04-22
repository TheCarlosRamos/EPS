import { describe, expect, it } from 'vitest';

import { integrationItems } from './integration-map';

describe('integrationItems', () => {
  it('mantem os blocos principais do escopo da issue', () => {
    const keys = integrationItems.map((item) => item.key);

    expect(keys).toEqual(
      expect.arrayContaining([
        'http-client-core',
        'api-health',
        'auth-refresh',
        'error-routing',
      ]),
    );
  });

  it('mantem status coerente entre real e dependencias mockadas/pendentes', () => {
    const statusByKey = Object.fromEntries(
      integrationItems.map((item) => [item.key, item.status]),
    );

    expect(statusByKey['http-client-core']).toBe('real');
    expect(statusByKey['api-health']).toBe('pendente');
    expect(statusByKey['auth-refresh']).toBe('mockado');
    expect(statusByKey['error-routing']).toBe('mockado');
  });
});
