# Projeto 02: Buscador OSINT Automatizado
## Analise sob PRINCE2 e PMBOK

---

## 1. Visao Geral do Projeto

O **Buscador OSINT Automatizado** e uma ferramenta de apoio a fase de Inteligencia Policial. O objetivo e reduzir drasticamente o tempo de "levantamento de dados em fontes abertas". Em vez de consultas manuais, o robo realiza uma Busca Federada, compilando vinculos, antecedentes em Diarios Oficiais e presenca em redes sociais para formar um dossie preliminar que servira de base para pedidos de quebra de sigilo ou mandados de busca e apreensao.

### Requisitos Funcionais
| ID | Requisito | Descricao |
|----|-----------|-----------|
| RF01 | Busca Multi-Entrada | Aceitar CPF, Nome Completo, E-mail, Telefone ou "Vulgo" |
| RF02 | Agregador de Fontes | Consultar Redes Sociais, Jusbrasil, Diarios Oficiais e buscadores |
| RF03 | Web Scraping / API | Extrair textos de postagens, fotos de perfil e vinculos |
| RF04 | Captura de Evidencia | Printscreens automaticos para preservacao da prova (Snapshot) |
| RF05 | Geracao de Dossie | PDF estruturado com sumario, links e cronologia |
| RF06 | Inferencia de Vinculos | Identificar pessoas que aparecem em multiplas fontes |

### Requisitos Nao Funcionais
| ID | Requisito | Criterio |
|----|-----------|----------|
| RNF01 | Anonimato Operacional | Rotacao de IP (Proxy/VPN), alteracao de User-Agents |
| RNF02 | Extensibilidade (Plugin) | Scrapers modulares; nova rede social sem mudanca no core |
| RNF03 | Escalabilidade | Buscas assincronas (filas) para multiplas equipes |
| RNF04 | Auditabilidade Interna | Log de quem realizou a busca, conformidade LGPD |
| RNF05 | Resiliencia | Tratar captchas e quedas sem interromper demais fontes |

### Arquitetura Proposta
1. Frontend: React/Vue (grafos de vinculos e timeline)
2. API Gateway: Python/FastAPI
3. Modulos Scrapers (Workers): Containers independentes por fonte
4. Task Queue: Redis/Celery
5. Data Storage: JSON (metadados) + MinIO/S3 (prints e fotos)

---

## 2. Analise sob PRINCE2

### 2.1 Verificacao dos 7 Principios

#### Principio 1: Justificativa de Negocio Continua
- **Business Case**: Investigadores gastam horas em consultas manuais a dezenas de fontes abertas. A automacao pode reduzir o tempo de levantamento de 8h para 15 minutos por alvo.
- **Beneficios**: Velocidade de investigacao; padronizacao de dossies; preservacao automatica de evidencias.
- **Custos**: Infraestrutura de proxy/VPN, desenvolvimento, servidores.
- **Riscos para o Business Case**: Mudancas de layout de redes sociais quebrando scrapers; questoes legais sobre scraping; bloqueio de IPs.
- **Sustentabilidade**: O Business Case deve considerar custo de manutencao continua dos scrapers.

#### Principio 2: Aprender com a Experiencia
- **Licoes a buscar**: Ferramentas OSINT existentes (Maltego, SpiderFoot, Recon-ng); experiencias de outras policias; limitacoes legais de scraping no Brasil.
- **Atencao especial**: Projetos anteriores que falharam por nao prever a volatilidade das fontes web.

#### Principio 3: Papeis e Responsabilidades Definidos
| Papel PRINCE2 | Sugestao para o Projeto |
|---------------|------------------------|
| **Executivo** | Chefe da Divisao de Inteligencia da PCDF |
| **Usuario Principal** | Agentes de inteligencia e analistas da PCDF |
| **Fornecedor Principal** | Coordenador do CyLab/UnB + Especialista em seguranca de redes |
| **Gerente de Projeto** | Pesquisador da UnB com experiencia em web scraping e seguranca |
| **Gerente de Equipe** | Lider tecnico do desenvolvimento |
| **Garantia do Projeto** | Assessor juridico da PCDF (legalidade das buscas) |

#### Principio 4: Gerenciamento por Estagios
| Estagio | Foco | Entrega Principal |
|---------|------|-------------------|
| Iniciacao | Planejamento + analise legal | PID com parecer juridico |
| Estagio 1 | Infra + Busca basica | API Gateway + 2-3 scrapers iniciais |
| Estagio 2 | Captura de evidencia + Dossie | Snapshot automatico + gerador de PDF |
| Estagio 3 | Inferencia de vinculos + Grafos | Visualizacao de relacionamentos |
| Estagio 4 | Anonimato + Escala + Deploy | Sistema em producao com VPN farm |

#### Principio 5: Gerenciamento por Excecao
| Dimensao | Tolerancia Sugerida |
|----------|-------------------|
| Tempo | +/- 3 semanas por estagio (volatilidade das fontes) |
| Custo | +/- 15% (necessidade potencial de proxies adicionais) |
| Qualidade | Minimo 3 fontes consultadas com sucesso por busca |
| Escopo | Novas fontes podem ser adicionadas; fontes quebradas nao contam como defeito |

#### Principio 6: Foco em Produtos
| Produto | Descricao | Criterio de Qualidade |
|---------|-----------|----------------------|
| API Gateway | Orquestrador de buscas | Tempo de resposta < 3s para distribuicao |
| Modulos Scrapers | Workers por fonte | Cobertura de 5+ fontes; taxa de sucesso > 80% |
| Motor de Snapshot | Captura de paginas | Screenshot legivel; metadados de data/hora/URL |
| Gerador de Dossie | PDF estruturado | Sumario completo; links ativos; cronologia |
| Dashboard de Vinculos | Grafo de relacionamentos | Visualizacao clara de conexoes entre pessoas |
| Farm de Anonimato | Infraestrutura de proxy/VPN | Zero vazamento de IPs PCDF |

#### Principio 7: Adequacao ao Ambiente
- **Legalidade**: Toda busca OSINT deve estar amparada em inquerito ou procedimento legal
- **Auditabilidade**: Cada busca registrada com identificacao do agente e numero do procedimento
- **Administracao publica**: Aquisicao de servicos de proxy pode exigir processo licitatorio
- **Volatilidade web**: Scrapers precisam de manutencao constante

### 2.2 Aplicacao dos 7 Temas

| Tema | Aplicacao ao Projeto |
|------|---------------------|
| **Business Case** | ROI: horas de analista poupadas x custo de infra + dev + manutencao de scrapers |
| **Organizacao** | Comite com Inteligencia PCDF + UnB + Assessoria Juridica |
| **Qualidade** | Taxa de sucesso de scrapers; completude do dossie; validade juridica dos snapshots |
| **Planos** | Plano do Projeto com dependencia explicita de parecer juridico |
| **Risco** | Riscos legais (scraping ilegal), tecnicos (bloqueio de IPs, captchas), operacionais (mau uso da ferramenta) |
| **Mudanca** | Orcamento de mudanca robusto (15-20%) dada a volatilidade das fontes |
| **Progresso** | Metricas de scrapers ativos vs quebrados; volume de buscas processadas |

### 2.3 Processo de Starting Up Detalhado

**Atividades Essenciais:**

1. **Nomear Executivo e Gerente**: Executivo da Divisao de Inteligencia + GP da UnB
2. **Preparar Project Brief**:
   - Mandato: Necessidade de acelerar levantamento OSINT
   - Business Case Esbocado: Economia de X horas/mes por investigador
   - Descricao do Produto: Ferramenta web de busca federada com geracao de dossie
   - Estrutura da equipe: Time misto UnB-PCDF
3. **Estrategia de Iniciacao**: Como obter parecer juridico; como mapear fontes prioritarias
4. **Plano do Estagio de Iniciacao**: 4-6 semanas para produzir o PID completo

**Elementos de Controle:**
- Registro de Licoes (desde o dia 1)
- Registro de Riscos Inicial (questoes legais, bloqueio de fontes)
- Abordagem de Qualidade (metricas de sucesso de scraping)

---

## 3. Analise sob PMBOK

### 3.1 Alinhamento com os 12 Principios (PMBOK 7)

| Principio PMBOK | Aplicacao |
|-----------------|-----------|
| Stewardship | Uso responsavel de dados obtidos em fontes abertas; compliance com LGPD |
| Equipe colaborativa | Integracao entre analistas de inteligencia e desenvolvedores |
| Engajar stakeholders | MP, juizes (destinatarios dos dossies), agentes (usuarios), TI (operadores) |
| Focar em valor | Valor = dossies completos em minutos, nao em dias |
| Interacoes do sistema | Integracao com fluxos de inquerito existentes, sistemas judiciais |
| Lideranca | Lideranca juridica tao importante quanto lideranca tecnica |
| Adaptar ao contexto | Legislacao brasileira sobre acesso a dados publicos e privados |
| Qualidade | Veracidade e completude das informacoes coletadas |
| Complexidade | Fontes volateis + requisitos legais + anonimato = complexidade muito alta |
| Riscos | Risco juridico e reputacional elevado; risco tecnico de fontes instáveis |
| Adaptabilidade | Arquitetura de plugins para lidar com mudancas constantes de fontes |
| Mudanca | Agentes precisam aprender a confiar na ferramenta e verificar resultados |

### 3.2 Processos PMBOK 6 Mais Relevantes

**Iniciacao:**
- Desenvolver o Termo de Abertura (4.1) - Incluir mandato legal e restricoes
- Identificar Partes Interessadas (13.1) - MP, juizes, agentes, compliance, LGPD

**Planejamento:**
- Planejar Gerenciamento de Riscos (11.1) - Riscos legais e operacionais
- Identificar Riscos (11.2) - Workshop multidisciplinar (juridico, tecnico, operacional)
- Planejar Gerenciamento de Aquisicoes (12.1) - Servicos de proxy/VPN, infra

**Execucao:**
- Conduzir Aquisicoes (12.2) - Contratar servicos de proxy/VPN
- Gerenciar Comunicacoes (10.2) - Alinhamento continuo com area juridica

**Monitoramento:**
- Monitorar Riscos (11.7) - Monitoramento constante de bloqueios e questoes legais
- Controlar Aquisicoes (12.3) - Avaliar performance dos servicos de proxy

### 3.3 Areas de Conhecimento Criticas

| Area | Relevancia |
|------|-----------|
| **Integracao** | Coordenacao entre scrapers, API gateway, armazenamento e frontend |
| **Riscos** | Area mais critica: riscos legais, eticos e tecnicos |
| **Aquisicoes** | Proxies, VPNs, servidores - tudo em ambiente publico |
| **Qualidade** | Completude e veracidade dos dados coletados |
| **Comunicacoes** | Ponte entre juridico, tecnico e operacional |
| **Partes Interessadas** | Stakeholders com interesses potencialmente conflitantes (celeridade vs legalidade) |

---

## 4. Riscos Principais

| ID | Risco | Probabilidade | Impacto | Resposta |
|----|-------|---------------|---------|----------|
| R01 | Uso ilegal da ferramenta (busca sem amparo) | Media | Muito Alto | Auditoria obrigatoria; vinculo a numero de procedimento legal |
| R02 | Bloqueio de IPs/contas | Alta | Alto | VPN farm com rotacao; fallback para APIs oficiais |
| R03 | Mudanca de layout quebrando scrapers | Alta | Alto | Arquitetura de plugins; monitoramento de saude dos scrapers |
| R04 | Captcha bloqueando coleta | Alta | Medio | Servicos anti-captcha; fallback manual; cache |
| R05 | Vazamento da identidade da PCDF | Baixa | Muito Alto | VPN dedicada; User-Agent rotation; zero uso de IPs oficiais |
| R06 | Contestacao juridica de evidencia digital | Media | Alto | Snapshot com timestamp e hash SHA-256; cadeia de custodia |
| R07 | Dados pessoais coletados indevidamente | Media | Alto | Filtros LGPD; retencao minima; anonimizacao |

---

## 5. Consideracoes Eticas e Legais

Este projeto exige atencao especial a:

1. **Marco Legal**: Toda busca deve estar vinculada a um procedimento investigativo formalizado
2. **LGPD (Art. 4)**: Tratamento de dados para fins de seguranca publica e investigacao criminal tem regime proprio, mas nao isenta de responsabilidade
3. **Proporcionalidade**: A coleta deve ser proporcional a necessidade investigativa
4. **Auditabilidade**: Logs completos de quem buscou o que, quando e por que
5. **SIEM Integration**: Monitorar uso da ferramenta para detectar abusos

---

## 6. Analise de Ciberseguranca

### 6.1 Pontos de Seguranca Presentes no Documento

| Area | Referencia | O que cobre |
|------|-----------|-------------|
| Anonimato Operacional | RNF01 | Rotacao de IP (Proxy/VPN) + alteracao de User-Agents para evitar deteccao |
| Auditabilidade Interna | RNF04 | Logs de quem realizou cada busca, para conformidade LGPD |
| DevSecOps | Secao 5 | SonarQube para impedir vazamento de tokens/credenciais no codigo |
| SIEM Integration | Secao 5 | Monitorar uso da ferramenta e garantir que buscas estao dentro do escopo legal |
| Proxy/VPN Farm | Secao 5 | IPs da PCDF nunca devem aparecer nos logs dos sites buscados |
| Resiliencia | RNF05 | Tratamento de CAPTCHAs e quedas de sites sem interromper demais fontes |

### 6.2 Lacunas Criticas Nao Abordadas

#### 6.2.1 Conformidade LGPD (Lei 13.709/2018)

O documento menciona LGPD apenas uma vez (RNF04) mas nao detalha os requisitos reais:

| Requisito | Fundamentacao | Descricao |
|-----------|---------------|-----------|
| Base Legal | Art. 7, Art. 4 | LGPD isenta atividades de seguranca publica (Art. 4, III), mas a isencao nao e absoluta — exige lei especifica futura para regulamentar. Ate la, principios de necessidade e proporcionalidade se aplicam. Toda busca deve estar vinculada a inquerito policial formal. |
| RIPD (Relatorio de Impacto a Protecao de Dados) | Art. 38 | ANPD pode exigir RIPD para tratamento de alto risco. Uma ferramenta que coleta dados pessoais em massa de fontes abertas e alto risco por definicao. Deve ser preparado **antes do deploy**. |
| DPO / Encarregado de Dados | Art. 41 | PCDF deve designar um Encarregado de Dados para supervisionar a operacao desta ferramenta. |
| Minimizacao de Dados | Art. 6, III | A ferramenta deve coletar apenas dados **relevantes a investigacao**, nao tudo disponivel. A geracao de dossie (RF05) deve filtrar dados pessoais irrelevantes. |
| Politica de Retencao e Eliminacao | Art. 16 | O documento menciona "Storage de Alta Capacidade" mas nao diz **quando dados sao eliminados**. Dados devem ser eliminados quando nao mais necessarios. |
| Direitos do Titular | Art. 18 | Mesmo para aplicacao da lei, deve haver processo para tratar solicitacoes de pessoas cujos dados foram coletados — especialmente se a investigacao for arquivada sem denúncia. |

#### 6.2.2 Marco Civil da Internet (Lei 12.965/2014)

| Requisito | Fundamentacao | Descricao |
|-----------|---------------|-----------|
| Inviolabilidade da intimidade | Art. 7, I | Scraping de perfis privados/restritos pode violar este direito. A ferramenta deve distinguir entre dados **verdadeiramente publicos** e dados protegidos por configuracoes de privacidade. |
| Acesso a registros | Art. 10, §2 | Acesso a logs de conexao e dados pessoais para investigacoes requer **ordem judicial**. A ferramenta pode coletar dados publicos, mas acessar conteudo restrito ou solicitar dados de plataformas exige autorizacao judicial. |
| Termos de Servico | — | Scraping automatizado viola os ToS da maioria das plataformas. Embora a aplicacao da lei possa ter fundamento legal, isso cria uma area cinzenta juridica que necessita de parecer juridico formal. |

#### 6.2.3 Cadeia de Custodia Digital (CPP Art. 158-A a 158-F)

A reforma de 2019 do Codigo de Processo Penal introduziu cadeia de custodia obrigatoria para evidencias. O documento menciona "Captura de Evidencia" (RF04) mas nao contempla:

| Requisito | Fundamentacao | Descricao |
|-----------|---------------|-----------|
| Hash de integridade | Art. 158-B | Todo screenshot e arquivo de dados coletados deve ter um **hash SHA-256** gerado no momento da captura e armazenado separadamente. Sem isso, a evidencia pode ser contestada em juizo como adulterada. |
| Carimbo de tempo com validade juridica | ICP-Brasil | Uso de autoridade certificadora de tempo (TSA) vinculada a ICP-Brasil para provar **quando** a evidencia foi coletada. O relogio do sistema nao tem validade juridica suficiente. |
| Trilha de auditoria completa | Art. 158-C | Toda pessoa/sistema que acessou a evidencia deve ser registrado. Vai alem do RNF04 — nao e apenas "quem buscou" mas "quem acessou, copiou, exportou ou modificou o dossie". |
| Isolamento da evidencia original | — | Dados originais coletados devem ser armazenados como **somente leitura** e nunca modificados. Qualquer analise deve ser feita em copias. |

#### 6.2.4 Controle de Acesso e Autenticacao

O documento nao menciona nada sobre:

| Requisito | Descricao |
|-----------|-----------|
| RBAC (Controle de Acesso por Papeis) | Nem todo agente deve acessar tudo. Papeis como: investigador (pode buscar), supervisor (pode auditar), administrador (pode configurar). |
| Autenticacao Multifator (MFA) | Obrigatorio para ferramenta que manipula dados pessoais sensiveis em contexto de aplicacao da lei. |
| Gerenciamento de sessao | Logout automatico, timeout de sessao, impedir sessoes concorrentes. |
| Segregacao por investigacao | Agente A nao deve ver as buscas do Agente B a menos que autorizado. Compartimentalizacao de dados por inquerito. |

#### 6.2.5 Criptografia

Nao mencionada em nenhum ponto do documento:

| Camada | Requisito |
|--------|-----------|
| Em transito | TLS 1.3 para toda comunicacao interna (API ↔ Redis ↔ Workers ↔ DB). |
| Em repouso | AES-256 para dados no PostgreSQL e objetos no MinIO (screenshots, dossies). |
| Gerenciamento de chaves | Politica de rotacao de chaves. Sem chaves hardcoded. Uso de cofre (HashiCorp Vault, gratuito). |

#### 6.2.6 Resposta a Incidentes

| Requisito | Fundamentacao | Descricao |
|-----------|---------------|-----------|
| Notificacao de incidentes | LGPD Art. 48 | Em caso de violacao de dados, ANPD e titulares afetados devem ser notificados em "prazo razoavel". PCDF precisa de plano formal de resposta a incidentes para esta ferramenta. |
| Prontidao forense | — | Ironico para uma ferramenta forense, mas a propria ferramenta deve ser auditavel forensicamente se comprometida. |

#### 6.2.7 Seguranca de Infraestrutura

| Area | Requisito |
|------|-----------|
| Segmentacao de rede | O Buscador OSINT deve rodar em segmento de rede isolado. Se um worker scraper for comprometido (ex: via pagina maliciosa), ele nao deve ter acesso a rede interna da PCDF. |
| Seguranca de containers | Scan de imagens (Trivy, gratuito), containers sem execucao como root, filesystems somente leitura onde possivel. |
| Gerenciamento de segredos | SonarQube (mencionado no doc) captura segredos no codigo, mas segredos em runtime (tokens de API, senhas de DB) precisam de cofre, nao variaveis de ambiente. |

### 6.3 Resumo de Prioridades

| Prioridade | Lacuna | Risco se ignorada |
|------------|--------|-------------------|
| **Critica** | Sem cadeia de custodia (hashing, timestamps ICP-Brasil) | Evidencia invalidada em juizo |
| **Critica** | Sem criptografia em repouso/transito | Responsabilidade por violacao de dados sob LGPD |
| **Critica** | Sem RBAC / MFA | Acesso nao autorizado a investigacoes sensiveis |
| **Alta** | Sem RIPD (Relatorio de Impacto) | ANPD pode bloquear a operacao da ferramenta |
| **Alta** | Sem politica de retencao/eliminacao de dados | Violacao da LGPD (Art. 16) |
| **Alta** | Sem segmentacao de rede | Worker comprometido = acesso a rede PCDF |
| **Media** | Sem plano de resposta a incidentes | Violacao da LGPD Art. 48 em caso de vazamento |
| **Media** | Sem parecer juridico sobre scraping vs ToS | Contestacao juridica dos metodos de investigacao |

---

## 7. Recomendacoes

1. **Parecer juridico obrigatorio antes de iniciar o desenvolvimento**: Validar legalidade de scraping para cada fonte
2. **Arquitetura de plugins desde o dia 1**: Fontes web sao volateis; facilidade de adicionar/remover scrapers e essencial
3. **Auditoria por design**: Cada busca registrada com ID do agente + numero do procedimento
4. **Estagios curtos com entregas incrementais**: Comecar com fontes publicas mais estaveis (Diarios Oficiais, Jusbrasil)
5. **Equipe de manutencao planejada**: Scrapers exigem manutencao continua pos-deploy
6. **Testes de anonimato rigorosos**: Validar que IPs da PCDF nunca vazam em nenhuma hipotese
7. **Implementar cadeia de custodia digital desde o Estagio 1**: Hash SHA-256 + carimbo de tempo ICP-Brasil em toda evidencia coletada
8. **RBAC e MFA obrigatorios**: Controle de acesso por papeis e autenticacao multifator antes de qualquer deploy em producao
9. **Criptografia em todas as camadas**: TLS 1.3 em transito, AES-256 em repouso, gerenciamento de chaves via cofre (Vault)
10. **Elaborar RIPD antes do deploy**: Relatorio de Impacto a Protecao de Dados exigido pela ANPD para tratamento de alto risco
11. **Segmentacao de rede**: Isolar a ferramenta da rede interna da PCDF para conter comprometimentos
12. **Plano de resposta a incidentes**: Procedimento formal para notificacao a ANPD e titulares em caso de violacao de dados
