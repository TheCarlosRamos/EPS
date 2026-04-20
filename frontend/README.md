# Frontend - Buscador OSINT

Base inicial da issue #12 (Setup HTTP Client, Nginx Reverse Proxy, Dev Server).

## Etapa Atual

- React 19 + TypeScript + Vite inicializados.
- TypeScript strict habilitado.
- Tela inicial alinhada ao design system institucional (tokens em `src/index.css`).

## Comandos

```bash
npm install
npm run dev
npm run type-check
npm run lint
```

## Mocks e Integracao Futura

Mapa central de status: `src/config/integration-map.ts`

- Onde esta mockado agora:
  - Fluxo JWT/refresh.
  - Tratamento de erro 401/403/5xx.
- O que ainda esta pendente de backend real:
  - Validacao final de `GET /api/health` usando endpoint FastAPI real.

Sempre que um endpoint real ficar pronto no backend, atualizar primeiro o item correspondente em `src/config/integration-map.ts` e depois a camada HTTP (etapa 3/4 da issue).
