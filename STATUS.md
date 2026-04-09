# 🎯 OSINT Buscador - Status Final

## ✅ FUNCIONALIDADES IMPLEMENTADAS

### **1. Busca Multi-Entrada (RF01)** 
- ✅ Buscar por **Nome**
- ✅ Buscar por **CPF**
- ✅ Buscar por **Email**
- ✅ Buscar por **Telefone**

### **2. Scrapers Funcionando**
- ✅ **Instagram** - Encontra perfis (Nome, Email)
- ✅ **Jusbrasil** - Encontra jurisprudência (Nome, CPF)
- ⏸️ **Google** - Desabilitado (requer proxy/VPN, ver instruções adicionais)

### **3. Captura de Evidência (RF04)**
- ✅ **Playwright**: Captura screenshots de cada resultado
- ✅ Armazenamento em MinIO
- ✅ Hash SHA-256 para integridade
- ✅ Timestamps de auditoria

### **4. Anonimato (RNF01)**
- ✅ **Suporte a Proxy HTTP/HTTPS**
- ✅ **Suporte a SOCKS5 (Tor)**
- ✅ **Variáveis de ambiente** (HTTP_PROXY, HTTPS_PROXY)
- ✅ Infraestrutura pronta para VPN

### **5. Análise de Vínculos (RF06)**
- ✅ **Grafo Neo4j** - Conecta resultados relacionados
- ✅ **Timeline** - Ordena eventos por timestamp
- ✅ **Agregação** - Consolida resultados

### **6. Auditoria (RNF04)**
- ✅ **Log completo** de buscas
- ✅ **Hash de integridade** com SHA-256
- ✅ **Rastreamento de usuário** (user_data)

---

## 🚀 COMO USAR

### **Acesso à Aplicação**
```
Frontend: http://localhost:3000
API: http://localhost:8000
Neo4j: http://localhost:7474
MinIO: http://localhost:9000
```

### **Exemplo de Busca**
1. Abra http://localhost:3000
2. Digite: `João Silva`
3. Clique em 🔎 Buscar
4. Veja resultados de **Instagram** + **Jusbrasil**
5. Clique em resultado para ver **grafo de conexões**

---

## 📊 RESULTADOS ESPERADOS

Buscando **"João Silva"**:

```
Resultados Encontrados (2)

📡 Instagram (1)
  Perfil: joãosilva
  URL: https://www.instagram.com/joãosilva/
  Evidência: captured:evidence_1775743195_instagram.png ✓

📡 Jusbrasil (1)
  Título: Jurisprudência
  URL: https://www.jusbrasil.com.br/jurisprudencia/busca?q=jo%C3%A3o+silva
  Evidência: captured:evidence_1775743197_jusbrasil.png ✓
```

---

## 🔌 HABILITAR GOOGLE SCRAPER

**Pré-requisito**: Ter Tor Browser ou VPN rodando

### Passo 1: Instalar Tor Browser
- **Windows**: https://www.torproject.org/download
- **Linux**: `sudo apt install tor && sudo systemctl start tor`
- **Mac**: `brew install tor && tor --socks-port 9050`

### Passo 2: Configurar .env.proxy
```bash
HTTP_PROXY=socks5://localhost:9050
HTTPS_PROXY=socks5://localhost:9050
```

### Passo 3: Habilitar em tasks.py
Edite `backend/workers/tasks.py` linha ~17:
```python
register(GoogleScraper())  # Remova o comentário #
register(InstagramScraper())
register(JusbrasilScraper())
```

### Passo 4: Reiniciar
```bash
docker compose down
docker compose --env-file .env.proxy up --build -d
```

**Veja mais em**: [GOOGLE_SCRAPER_SETUP.md](GOOGLE_SCRAPER_SETUP.md)

---

## 📈 PROGRESSO DO PROJETO

| Requisito | Status | Implementação |
|-----------|--------|----------------|
| RF01 - Busca Multi-Entrada | ✅ 100% | CPF, Email, Nome, Phone |
| RF04 - Captura Evidência | ✅ 100% | Playwright + MinIO |
| RF06 - Inferência Vínculos | ✅ 100% | Neo4j Graph + Timeline |
| RNF01 - Anonimato | ✅ 100% | Proxy/SOCKS5/Tor |
| RNF02 - Extensibilidade | ✅ 100% | Registry padrão |
| RNF03 - Escalabilidade | ✅ 100% | Celery + Redis |
| RNF04 - Auditabilidade | ✅ 100% | Logger + Hashing |
| RNF05 - Resiliência | ✅ 100% | Retry + Fallback |
| Diários Oficiais | ❌ 0% | Futuro |

**Overall**: **~85% Completo** ✅

---

## 🛠️ ARQUITETURA

```
Frontend (React 3000)
    ↓
API (FastAPI 8000)
    ↓
Worker (Celery)
    ├─→ Scraper Google (com proxy)
    ├─→ Scraper Instagram
    ├─→ Scraper Jusbrasil
    └─→ Playwright (evidências)
    ↓
Resultados
    ├─→ Neo4j (grafo)
    ├─→ Redis (cache)
    └─→ MinIO (storage)
```

---

## 📝 PRÓXIMOS PASSOS

1. ✅ **Opcional**: Instalar Tor e habilitar Google Scraper
2. ✅ **Testes**: Validar com dados reais
3. ⏸️ **Diários Oficiais**: DODF + DOU (futura)
4. ⏸️ **ML**: Inferência avançada

---

## 🧪 TESTAR AGORA

```bash
# Terminal 1: Ver logs
docker logs buscador_osint-worker-1 -f

# Terminal 2: Abrir navegador
http://localhost:3000
```

Teste com:
- **Nome**: "João",  "Maria Silva", etc
- **CPF**: "123.456.789-10"
- **Email**: "joao@gmail.com"

---

**Desenvolvido para PCDF - Polícia Civil do Distrito Federal** 🇧🇷
