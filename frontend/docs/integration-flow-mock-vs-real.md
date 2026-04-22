# Fluxo de Integracao (Mock vs Real)

## Objetivo
Documentar o que esta mockado, o que ja esta real e como migrar cada fluxo quando os endpoints do backend estiverem disponiveis.

## Status Atual

Real agora:
- Estrutura do cliente de API e interceptors (`src/api/client.ts`).
- Persistencia de sessao e leitura de configuracao de runtime.
- Configuracao do proxy `/api` no Vite.
- Configuracao do reverse proxy no Nginx para container de producao.

Mockado ou pendente de backend:
- Payload de retorno de refresh token em `src/api/mock-data.ts`.
- Fallback de health em `src/api/health.ts` quando `VITE_USE_MOCK_API=true`.
- Validacao final em runtime de `/api/health` contra endpoint FastAPI real.

## Decisao de Runtime

`VITE_USE_MOCK_API=true`
- O frontend retorna payloads mockados para fluxos criticos de integracao.
- Usado para manter o desenvolvimento do frontend sem bloqueio.

`VITE_USE_MOCK_API=false`
- O frontend chama endpoints reais do backend pela base URL e pelos proxies configurados.

## Checklist de Migracao (Mock -> Real)

1. Garantir que o contrato do endpoint no backend esta estavel.
2. Definir `VITE_USE_MOCK_API=false` no ambiente.
3. Remover ou reduzir ramificacoes de mock em:
- `src/api/mock-data.ts`
- `src/api/health.ts`
- fallback de refresh token em `src/api/client.ts`
4. Atualizar o status em `src/config/integration-map.ts` de `mockado/pendente` para `real`.
5. Validar em desenvolvimento (proxy do Vite) e em runtime de container (proxy do Nginx).

## Alvos de Validacao
- `/api/health` retorna resposta real do backend.
- Interceptors continuam injetando tokens e normalizando erros corretamente.
- Nginx continua servindo SPA e fazendo proxy de `/api/*`.
