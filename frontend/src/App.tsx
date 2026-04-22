import { useEffect, useState } from 'react';

import './App.css';

import { getHealthSnapshot } from './api/health';
import type { HealthSnapshot } from './api/types';
import { integrationItems } from './config/integration-map';

function App() {
  const [healthSnapshot, setHealthSnapshot] = useState<HealthSnapshot | null>(
    null,
  );
  const [healthError, setHealthError] = useState('');

  useEffect(() => {
    let isActive = true;

    getHealthSnapshot()
      .then((snapshot) => {
        if (isActive) {
          setHealthSnapshot(snapshot);
          setHealthError('');
        }
      })
      .catch((error: unknown) => {
        if (!isActive) {
          return;
        }

        setHealthSnapshot(null);
        setHealthError(
          error instanceof Error
            ? error.message
            : 'Falha ao consultar /api/health.',
        );
      });

    return () => {
      isActive = false;
    };
  }, []);

  return (
    <main className="app-shell">
      <header className="hero-block">
        <p className="eyebrow">EPS5 · Grupo 13 · PCDF</p>
        <h1>Buscador OSINT Frontend</h1>
        <p className="subtitle">
          Base inicial da issue #12 com React 19 + TypeScript + Vite.
        </p>
      </header>

      <section className="http-panel" aria-label="Status da camada HTTP">
        <div className="http-panel-header">
          <div>
            <p className="eyebrow">Camada HTTP</p>
            <h2>Cliente tipado com interceptors</h2>
          </div>
          <span
            className={`transport-tag transport-${healthSnapshot?.transportMode ?? 'mock'}`}
          >
            {healthSnapshot?.transportMode ?? 'carregando'}
          </span>
        </div>

        <p className="http-summary">
          {healthSnapshot?.description ||
            healthError ||
            'Consultando /api/health...'}
        </p>

        <dl className="http-metrics">
          <div>
            <dt>Status</dt>
            <dd>{healthSnapshot?.status ?? 'pendente'}</dd>
          </div>
          <div>
            <dt>Servico</dt>
            <dd>{healthSnapshot?.service ?? 'buscador-osint-api'}</dd>
          </div>
          <div>
            <dt>Versao</dt>
            <dd>{healthSnapshot?.version ?? 'mock'}</dd>
          </div>
          <div>
            <dt>Origem</dt>
            <dd>{healthSnapshot?.source ?? 'mock'}</dd>
          </div>
        </dl>
      </section>

      <section className="status-panel" aria-label="Status de integracao">
        <h2>Status de mocks e integracao futura</h2>
        <ul>
          {integrationItems.map((item) => (
            <li key={item.key} className="status-item">
              <div>
                <strong>{item.title}</strong>
                <p>{item.currentState}</p>
                <p className="future-note">
                  Proxima troca: {item.updateWhenReady}
                </p>
              </div>
              <span className="status-tag">{item.status}</span>
            </li>
          ))}
        </ul>
      </section>
    </main>
  );
}

export default App;
