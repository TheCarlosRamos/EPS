export interface SessionTokens {
  accessToken: string;
  refreshToken: string;
}

const accessTokenKey = 'buscador-osint.access-token';
const refreshTokenKey = 'buscador-osint.refresh-token';

function isBrowserStorageAvailable(): boolean {
  return (
    typeof window !== 'undefined' && typeof window.localStorage !== 'undefined'
  );
}

function readValue(storageKey: string): string {
  if (!isBrowserStorageAvailable()) {
    return '';
  }

  return window.localStorage.getItem(storageKey) || '';
}

export function getSessionTokens(): SessionTokens {
  return {
    accessToken: readValue(accessTokenKey),
    refreshToken: readValue(refreshTokenKey),
  };
}

export function setSessionTokens(tokens: SessionTokens): void {
  if (!isBrowserStorageAvailable()) {
    return;
  }

  window.localStorage.setItem(accessTokenKey, tokens.accessToken);
  window.localStorage.setItem(refreshTokenKey, tokens.refreshToken);
}

export function clearSessionTokens(): void {
  if (!isBrowserStorageAvailable()) {
    return;
  }

  window.localStorage.removeItem(accessTokenKey);
  window.localStorage.removeItem(refreshTokenKey);
}
