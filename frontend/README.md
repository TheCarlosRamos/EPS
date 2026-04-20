# Frontend - Buscador OSINT

Base inicial da issue #12 (Setup HTTP Client, Nginx Reverse Proxy, Dev Server).

## Etapa Atual

- React 19 + TypeScript + Vite inicializados.
- TypeScript strict habilitado.
- Tela inicial alinhada ao design system institucional (tokens em `src/index.css`).
- Camada HTTP tipada criada em `src/api` com interceptors de autorizacao e renovacao de sessao.

## Comandos

```bash
npm install
npm run dev
npm run type-check
npm run lint
npm run format:check
```

## Padronizacao de codigo

- ESLint com `eslint-plugin-security` ativo.
- Regra `react/no-danger` ativada para bloquear `dangerouslySetInnerHTML`.
- Prettier configurado com `semi`, `singleQuote` e `trailingComma`.

## Variaveis de ambiente

- `VITE_API_URL`: base da API. Padrao: `/api`.
- `VITE_USE_MOCK_API`: ativa o retorno mockado da camada HTTP. Padrao em desenvolvimento: `true`.
- `VITE_AUTH_REFRESH_ENDPOINT`: caminho usado para renovar a sessao. Padrao: `/auth/refresh`.
- `VITE_API_TIMEOUT_MS`: timeout das requisicoes. Padrao: `10000`.
- `VITE_MOCK_API_DELAY_MS`: atraso artificial para o modo mock. Padrao: `250`.
- `VITE_BACKEND_PROXY_TARGET`: alvo do proxy de desenvolvimento do Vite. Padrao: `http://localhost:8000`.

## Mocks e Integracao Futura

Mapa central de status: `src/config/integration-map.ts`

- Onde esta mockado agora:
  - Fluxo JWT/refresh.
  - Tratamento de erro 401/403/5xx.
- O que ainda esta pendente de backend real:
  - Validacao final de `GET /api/health` usando endpoint FastAPI real.

Sempre que um endpoint real ficar pronto no backend, atualizar primeiro o item correspondente em `src/config/integration-map.ts` e depois a camada HTTP (etapa 3/4 da issue).

O health atual esta em `src/api/health.ts`. Enquanto o backend nao expuser o endpoint final e o proxy nao estiver configurado, a tela usa o modo mock para continuar funcional.

Em desenvolvimento, o Vite encaminha requisicoes que comecam com `/api` para o backend definido em `VITE_BACKEND_PROXY_TARGET`.
