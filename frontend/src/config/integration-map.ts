export type IntegrationStatus = 'mockado' | 'real' | 'pendente';

export interface IntegrationItem {
  key: string;
  title: string;
  status: IntegrationStatus;
  currentState: string;
  updateWhenReady: string;
}

// Fonte unica para deixar claro o que esta mockado agora e o que deve virar integracao real.
export const integrationItems: IntegrationItem[] = [
  {
    key: 'api-health',
    title: 'GET /api/health',
    status: 'pendente',
    currentState:
      'Ainda sem cliente HTTP implementado nesta etapa. Sera validado na etapa de proxy + client.',
    updateWhenReady:
      'Quando o endpoint estiver estavel no backend FastAPI, ligar o client HTTP para usar retorno real.',
  },
  {
    key: 'auth-refresh',
    title: 'Fluxo JWT e refresh token',
    status: 'mockado',
    currentState:
      'Sera iniciado com mock na camada de client para destravar frontend sem dependencia de backend completo.',
    updateWhenReady:
      'Substituir mock por contrato real dos endpoints de login/refresh assim que a issue de autenticacao backend estiver pronta.',
  },
  {
    key: 'error-routing',
    title: 'Tratamento de erro 401/403/5xx',
    status: 'mockado',
    currentState:
      'Comportamento inicial sera testado com respostas simuladas para garantir fluxo da UI.',
    updateWhenReady:
      'Trocar simulacoes por codigos retornados pelo backend real e revisar navegacao final.',
  },
];
