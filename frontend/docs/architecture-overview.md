# Visao Geral de Arquitetura do Frontend

## Objetivo
Fornecer a infraestrutura base do frontend, com foco em configuracao do cliente HTTP, proxy de desenvolvimento local e reverse proxy de producao com Docker/Nginx.

## Componentes de Alto Nivel

1. Camada de UI
- App principal e componentes visuais em `src/`.
- Usa funcoes de servico da API em vez de chamadas de rede diretas.

2. Camada de API
- `src/api/client.ts`: instancia Axios, interceptors de request/response, injecao de token e normalizacao central de erros.
- `src/api/health.ts`: ponto de entrada da integracao do endpoint de health.
- `src/api/session.ts`: persistencia de tokens em localStorage.
- `src/api/errors.ts`: modelo e normalizacao de erros da API.
- `src/api/runtime.ts`: leitura de variaveis de ambiente e defaults.
- `src/api/types.ts`: contratos tipados da API.
- `src/api/mock-data.ts`: fallback mock enquanto endpoints do backend nao estiverem disponiveis.

3. Mapa de Integracao
- `src/config/integration-map.ts` e a fonte unica de verdade para status (`real`, `mockado`, `pendente`).

4. Runtime de Desenvolvimento
- `vite.config.ts` faz proxy de `/api` para o alvo definido em `VITE_BACKEND_PROXY_TARGET`.

5. Runtime de Producao
- `Dockerfile` gera os arquivos estaticos e serve via Nginx.
- `docker/nginx.conf.template` configura HTTPS, fallback de SPA e reverse proxy de `/api`.
- `docker/entrypoint.sh` renderiza a configuracao final do Nginx com variaveis de ambiente e cria certificados autoassinados para dev.

## Fluxo de Requisicao

Desenvolvimento:
Browser -> Vite (`npm run dev`) -> proxy `/api/*` -> backend alvo

Producao (container):
Browser -> Nginx (HTTPS) -> arquivos estaticos em `/` e reverse proxy em `/api/*`

## Base de Seguranca e Qualidade
- TypeScript em modo strict.
- ESLint + eslint-plugin-security.
- Prettier para formatacao.
- Headers de seguranca no Nginx e redirecionamento HTTP -> HTTPS.

## Limites Atuais
- A camada de infraestrutura e integracao esta implementada.
- Alguns endpoints dependentes de backend ainda usam fallback mock para nao bloquear trabalho paralelo do grupo.
