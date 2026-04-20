# Frontend - Buscador OSINT

Infraestrutura completa para issue #12: cliente HTTP tipado, proxy Vite, Nginx reverse proxy e Docker.

## Escopo Implementado

### HTTP Client Configuration
- ✅ Cliente Axios com base URL `/api`
- ✅ Interceptors tipados para injeção JWT e renovação de sessão
- ✅ Tratamento centralizado de erro (401/403/5xx)
- ✅ Interfaces TypeScript alinhadas com contrato backend Pydantic

### Vite Dev Server
- ✅ React 19 + TypeScript strict habilitado
- ✅ Proxy `/api/` em `vite.config.ts` para backend local
- ✅ ESLint com `eslint-plugin-security` (bloqueia `dangerouslySetInnerHTML`)
- ✅ Prettier + formatação padronizada

### Nginx Reverse Proxy
- ✅ Configuração em `infra/nginx/nginx.conf` (produção) + `frontend/docker/nginx.conf.template` (container)
- ✅ Roteamento `/api/*` para backend FastAPI
- ✅ Roteamento `/` para SPA (fallback `index.html`)
- ✅ Headers de segurança: `X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy`, `CSP`, `Permissions-Policy`
- ✅ TLS 1.2/1.3 com cert autoassinado para dev (via `openssl` no entrypoint)
- ✅ Redirect HTTP → HTTPS (301)

## Execução

```bash
npm install
npm run dev         # Vite dev server com proxy /api
npm run build       # Build de produção
npm run type-check  # Validar tipos TS
npm run lint        # ESLint + regras de segurança
npm run format:check # Prettier
```

## Stack

- **Frontend:** React 19 + TypeScript strict + Vite
- **HTTP:** Axios com interceptors (JWT, refresh, erro centralizado)
- **Dev:** Proxy Vite para backend em `VITE_BACKEND_PROXY_TARGET` (default: `http://localhost:8000`)
- **Produção:** Nginx reverse proxy (HTTPS + SPA fallback + /api proxy) no Docker
- **Qualidade:** ESLint (com `eslint-plugin-security`), Prettier, TypeScript strict

## Estrutura & Integração

| Arquivo | Status | Notas |
|---------|--------|-------|
| `src/api/client.ts` | ✅ Real | Axios tipado com interceptors de auth e erro |
| `src/api/health.ts` | 🔄 Pendente | Pronto para real; hoje em mock |
| `src/api/session.ts` | ✅ Real | Persistência de tokens (localStorage) |
| `src/api/mock-data.ts` | ⚙️ Mock | **Ver comentários internos para substituição** |
| `src/config/integration-map.ts` | ⚙️ Mock | Mapa de status de cada endpoint |
| `vite.config.ts` | ✅ Real | Proxy `/api` para backend local |
| `Dockerfile` + `docker/nginx.conf.template` | ✅ Real | Build multi-stage + Nginx container |
| `docker-compose.yml` | ✅ Real | Frontend em porta 8080/8443 |

## Critérios de Aceitação

- [x] `npm run dev` em `frontend/` inicia Vite sem erros
- [x] `npm run lint` passa com zero erros (ESLint + security plugin ativo)
- [x] `npm run type-check` passa com zero erros (TypeScript strict)
- [x] Cliente HTTP com interceptors tipados para injeção JWT e error handling (401/403/5xx)
- [x] Nginx configurado para servir SPA e fazer proxy `/api` para backend
- [x] Headers de segurança presentes no Nginx (validação com `curl -kI` pendente de Docker ativo)
- [x] API requests para `/api/health` corretamente estruturadas (proxy e contrato prontos; resposta real pendente de backend FastAPI)
- [x] ESLint security plugin configurado e bloqueando `dangerouslySetInnerHTML`

## Mock vs Real

**Mockados agora (sem backend):**
- JWT/refresh token em `src/api/mock-data.ts`
- GET /api/health em `src/api/health.ts`
- Erro 401/403/5xx tratamento simulado

**Como substituir:**
1. Quando endpoint FastAPI estiver pronto, mudar `VITE_USE_MOCK_API=false` ou implementar a resposta real.
2. Editar `src/api/mock-data.ts` e remover as funções mock.
3. Atualizar status em `src/config/integration-map.ts` de "mockado" para "real".

## Variáveis de Ambiente

```
VITE_API_URL=                       # Base da API (default: /api)
VITE_USE_MOCK_API=true              # Ativa mock (default: true em dev)
VITE_AUTH_REFRESH_ENDPOINT=/auth/refresh
VITE_API_TIMEOUT_MS=10000
VITE_MOCK_API_DELAY_MS=250
VITE_BACKEND_PROXY_TARGET=http://localhost:8000
```

Ver `.env.example` para template completo.
