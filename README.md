# Buscador OSINT Automatizado – PCDF

Sistema completo de inteligência em fontes abertas desenvolvido para a Polícia Civil do Distrito Federal.

## Arquitetura Implementada

### Backend (FastAPI + Python)
- **API Gateway**: FastAPI com autenticação JWT
- **Task Queue**: Redis + Celery para processamento assíncrono
- **Scrapers Modulares**: Google, Instagram, Jusbrasil
- **Captura de Evidências**: Playwright para screenshots automáticos
- **Auditoria**: Logs detalhados com hash de integridade
- **Análise de Inteligência**: Inferência de vínculos e timeline
- **Storage**: MinIO para evidências digitais

### Frontend (React)
- Interface moderna com React 18
- Visualização de grafos de vínculos (react-force-graph-2d)
- Busca multi-entrada em tempo real
- Exibição de resultados estruturados

### Infraestrutura
- **Docker**: Contêineres para todos os serviços
- **Redis**: Fila de tarefas e cache
- **MinIO**: Storage compatível com S3
- **Neo4j**: Banco de grafos para análise de vínculos

## Requisitos Funcionais Implementados

✅ **RF01** - Busca Multi-Entrada (CPF, Nome, E-mail, Telefone, Vulgo)  
✅ **RF02** - Agregador de Fontes (Google, Instagram, Jusbrasil)  
✅ **RF03** - Web Scraping/API com extração estruturada  
✅ **RF04** - Captura de Evidência com screenshots automáticos  
✅ **RF05** - Geração de Dossiê PDF  
✅ **RF06** - Inferência de Vínculos com análise de grafos  

## Requisitos Não Funcionais Implementados

✅ **RNF01** - Estrutura para anonimato operacional  
✅ **RNF02** - Arquitetura extensível por plugins  
✅ **RNF03** - Escalabilidade com processamento assíncrono  
✅ **RNF04** - Auditoria interna completa  
✅ **RNF05** - Resiliência com tratamento de erros  

## Execução

```bash
# Iniciar todos os serviços
docker-compose up --build

# Acessar serviços
# API: http://localhost:8000
# Frontend: http://localhost:3000
# MinIO Console: http://localhost:9001
# Neo4j Browser: http://localhost:7474
```

## Endpoints da API

- `POST /search` - Iniciar busca OSINT
- `GET /task/{task_id}` - Verificar status da busca
- `POST /investigacoes` - Gerar dossiê PDF

## Estrutura de Dados

```json
{
  "results": [...],
  "graph": {
    "nodes": [...],
    "edges": [...]
  },
  "timeline": [...]
}
```

## Segurança e Auditoria

- Logs de auditoria com hash SHA-256
- Autenticação JWT para controle de acesso
- Captura de evidências com integridade verificável
- Rastreabilidade completa das operações

## Próximos Passos

1. Configurar proxy/VPN para anonimato real
2. Adicionar mais fontes (DOU/DODF)
3. Implementar rotação de User-Agents
4. Integrar com SIEM da PCDF
