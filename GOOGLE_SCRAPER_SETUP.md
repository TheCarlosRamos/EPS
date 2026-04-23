# 📈 Google Scraper - Guia de Configuração com Proxy

## Status Atual
- ✅ **Instagram Scraper**: Funcionando perfeitamente
- ✅ **Jusbrasil Scraper**: Funcionando perfeitamente
- ✅ **Evidências (Playwright)**: Capturando screenshots
- ⏸️ **Google Scraper**: Desabilitado (requer proxy/VPN)

## Por que Google está desabilitado?

Google detecta requisições de datacenters Docker e retorna página vazia (6KB).
**Solução**: Usar Proxy ou VPN para parecer um usuário real.

---

## 🔌 Como Habilitar Google Scraper com Proxy

### Pré-requisito: Ter Tor ou VPN rodando

#### **Opção 1: Tor Browser (Recomendado)**

**Windows:**
1. Baixe [Tor Browser](https://www.torproject.org/download)
2. Instale e abra (deixe rodando)
3. Tor abre SOCKS5 na porta **9050**

**Linux:**
```bash
sudo apt install tor
sudo systemctl start tor
# Tor roda na porta 9050
```

**Mac:**
```bash
brew install tor
tor --socks-port 9050  # em terminal separado
```

#### **Opção 2: VPN Local**
Use qualquer VPN que ofereça proxy SOCKS5 ou HTTP na sua máquina.

---

## 📝 Configurar .env.proxy

Edite ou crie `.env.proxy` na raiz do projeto:

```bash
# Para Tor Browser:
HTTP_PROXY=socks5://localhost:9050
HTTPS_PROXY=socks5://localhost:9050

# Para outro proxy:
# HTTP_PROXY=http://seu-proxy:porta
# HTTPS_PROXY=http://seu-proxy:porta
```

---

## 🚀 Iniciar com Proxy

```bash
# Parar aplicação atual
docker compose down

# Iniciar COM arquivo de proxy
docker compose --env-file .env.proxy up -d

# Verificar logs
docker logs buscador_osint-worker-1 --tail=50
```

---

## ✅ Verificar se Proxy Funciona

**PowerShell:**
```powershell
curl.exe -x socks5://localhost:9050 https://www.google.com -I

# Se retornar "200 OK", funciona!
```

**Linux/Mac:**
```bash
curl -x socks5://localhost:9050 https://www.google.com -I
```

---

## 🔄 Habilitar Google Scraper

Edite `backend/workers/tasks.py` linha ~17:

**De:**
```python
# register(GoogleScraper())  # ⚠️ DESABILITADO
register(InstagramScraper())
register(JusbrasilScraper())
```

**Para:**
```python
register(GoogleScraper())  # ✅ HABILITADO COM PROXY
register(InstagramScraper())
register(JusbrasilScraper())
```

Depois reconstrua:
```bash
docker compose down
docker compose --env-file .env.proxy up --build -d
```

---

## 🧪 Testar Busca com Google

1. Abra http://localhost:3000
2. Busque por: `"João Silva"`
3. Deve retornar:
   - ✅ Instagram
   - ✅ Jusbrasil
   - ✅ **Google** (agora com proxy!)

---

## 📊 Performance Esperado

Com Tor/VPN:
- 1-2s por scraperComfundido por Tor: 3-5s (mas com máximo anonimato)

---

## 🆘 Troubleshooting

**Erro: "Cannot reach proxy"**
- Verifique se Tor/VPN estão rodando
- Teste com `curl` manualmente

**Erro: "Timeout"**
- Tor pode estar lento, aguarde 5-10s
- Tente com outro proxy

**Google ainda retorna vazio**
- Proxy pode estar detectado
- Tente com Tor Browser em vez de `tor` CLI
- Aguarde mais tempo entre buscas

---

## 📚 Referências

- [Tor Project](https://www.torproject.org)
- [Playwright Proxy](https://playwright.dev/python/docs/api/class-browserlaunchcontext#browser-launch-context-proxy)
- [OSINT Ethics](https://www.sans.org/white-papers/osint-introduction/)

---

**Próximos Passos:**
1. Instale Tor Browser ou configure seu proxy
2. Edit `.env.proxy` com seus detalhes
3. Habilite Google Scraper em `tasks.py`
4. Teste busca em http://localhost:3000
5. Aproveite os 3 scrapers funcionando! 🚀
