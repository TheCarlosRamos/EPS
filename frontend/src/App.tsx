import './App.css';
import { integrationItems } from './config/integration-map';

function App() {
  return (
    <main className="app-shell">
      <header className="hero-block">
        <p className="eyebrow">EPS5 · Grupo 13 · PCDF</p>
        <h1>Buscador OSINT Frontend</h1>
        <p className="subtitle">
          Base inicial da issue #12 com React 19 + TypeScript + Vite.
        </p>
      </header>

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
