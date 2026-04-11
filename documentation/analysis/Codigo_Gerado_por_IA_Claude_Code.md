# Código Gerado por IA: Claude Code

---

## 1. O que é Claude Code

Claude Code é um assistente de codificação agêntico da Anthropic. Ele lê seu codebase, edita arquivos, executa comandos no terminal e se integra ao fluxo de desenvolvimento. Funciona via linguagem natural — você descreve o que quer e ele implementa.

Disponível em múltiplas superfícies:

| Superfície | Descrição |
|-----------|-----------|
| **Terminal CLI** | Modo interativo e não-interativo completo |
| **VS Code** | Extensão com diffs inline e chat integrado |
| **JetBrains** | Plugin para IntelliJ, PyCharm, WebStorm, etc. |
| **Desktop App** | Aplicativo para Mac/Windows com revisão visual de diffs |
| **Web** | Acesso via navegador em claude.ai/code |

O que ele faz na prática:
- Constrói features e corrige bugs a partir de descrição em linguagem natural
- Cria commits, branches e pull requests
- Executa testes, lint, e atualizações de dependências
- Delega tarefas para subagentes em paralelo
- Se integra com ferramentas externas via MCP

Documentação oficial: https://code.claude.com/docs/en/overview.md

---

## 2. Ações Paralelas

Claude Code pode executar múltiplas ações simultaneamente, evitando gargalos sequenciais.

### Mecanismos de paralelismo

**Chamadas de ferramentas em paralelo**: Quando múltiplas operações são independentes (ex: ler 3 arquivos ao mesmo tempo), Claude dispara todas na mesma mensagem em vez de esperar uma por uma.

**Subagentes**: Claude pode delegar tarefas para agentes especializados que rodam em paralelo. Cada subagente tem seu próprio contexto e conjunto de ferramentas. Tipos disponíveis:
- `general-purpose` — tarefas complexas de múltiplas etapas
- `Explore` — exploração rápida de codebase
- `Plan` — planejamento de arquitetura
- Agentes customizados definidos em settings

**Git Worktrees**: Agentes podem trabalhar em cópias isoladas do repositório (worktrees), permitindo mudanças paralelas sem conflitos.

**Agent Teams (experimental)**: Uma sessão líder coordena múltiplas sessões "teammate" que trabalham independentemente com lista de tarefas compartilhada e troca de mensagens entre agentes. Habilitar com: `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`

Documentação oficial: https://code.claude.com/docs/en/agent-teams.md

---

## 3. Teams

Agent Teams é o recurso experimental que permite coordenar múltiplas instâncias de Claude Code trabalhando juntas no mesmo projeto.

### Como funciona

- Uma **sessão líder** distribui trabalho para **sessões teammate**
- Cada teammate opera com sua própria janela de contexto
- Compartilham uma **lista de tarefas** e podem trocar mensagens
- Teammates trabalham em worktrees isolados para evitar conflitos de arquivo

### Colaboração em equipe humana

Não existe um recurso "Teams" para colaboração entre humanos dentro do Claude Code. A colaboração acontece via:
- **Git** (commits, branches, PRs)
- **CLAUDE.md** compartilhado no repositório (convenções, regras do projeto)
- **Contas Team/Enterprise** com SSO, permissões gerenciadas e analytics

Documentação oficial: https://code.claude.com/docs/en/agent-teams.md

---

## 4. Skills

Skills são comandos customizados e workflows reutilizáveis que estendem as capacidades do Claude Code. Seguem o padrão aberto **Agent Skills**.

### Estrutura

Skills são definidas em arquivos `SKILL.md` dentro de `.claude/skills/<nome-da-skill>/`:

```markdown
---
name: minha-skill
description: O que essa skill faz
allowed-tools: [Read, Edit, Bash]
user-invocable: true
---

Instruções para o Claude executar quando a skill for invocada.
```

### Invocação

Skills podem ser disparadas de **duas formas**:

| Forma | Como funciona | Exemplo |
|-------|---------------|---------|
| **Manual (comando)** | Usuário digita `/nome-da-skill` no prompt | `/simplify` |
| **Automática (contexto)** | Claude detecta que a skill é relevante ao que o usuário está pedindo e a invoca sozinho | Usuário pede para construir algo com a API da Anthropic → Claude dispara a skill `claude-api` automaticamente |

Esse comportamento é controlado por flags no frontmatter da skill:

| Flag | Efeito |
|------|--------|
| `user-invocable: true` | Usuário pode disparar com `/nome-da-skill` |
| `user-invocable: false` | Apenas Claude pode invocar (invisível para o usuário) |
| `disable-model-invocation: true` | Impede Claude de disparar automaticamente — somente manual |

Por padrão, uma skill é **ambas as coisas**: um comando que o usuário pode chamar E algo que Claude pode invocar quando o contexto da conversa indica relevância.

### Skills embutidas

| Skill | Função |
|-------|--------|
| `/simplify` | Revisa código alterado para qualidade e eficiência |
| `/batch` | Orquestra mudanças em larga escala com 5-30 agentes em worktrees paralelos |
| `/loop` | Executa um prompt ou skill em intervalo recorrente |
| `/claude-api` | Auxilia na construção de apps usando a API da Anthropic |
| `/schedule` | Cria agentes remotos agendados via cron |

### Contexto dinâmico

Skills podem injetar saída de comandos usando a sintaxe `` !`comando` `` no corpo do SKILL.md, permitindo contexto atualizado a cada invocação.

Documentação oficial: https://code.claude.com/docs/en/skills.md

---

## 5. Comandos

Claude Code possui dois tipos de comandos:

### Comandos embutidos (built-in)

Comandos fixos do sistema, invocados com `/`:

| Comando | Função |
|---------|--------|
| `/help` | Mostra comandos disponíveis |
| `/config` | Abre interface de configurações |
| `/model` | Altera o modelo de IA |
| `/effort` | Ajusta nível de processamento/raciocínio |
| `/resume` | Continua uma sessão anterior |
| `/memory` | Gerencia CLAUDE.md e memória automática |
| `/mcp` | Configura servidores MCP |
| `/permissions` | Gerencia regras de acesso a ferramentas |
| `/fast` | Alterna modo rápido (mesmo modelo, saída mais veloz) |

### Comandos customizados

Definidos via Skills (seção anterior) ou arquivos `.claude/commands/<nome>.md`. Aparecem no autocomplete com `/` e podem receber argumentos.

Documentação oficial: https://code.claude.com/docs/en/commands.md

---

## 6. Settings JSON

O arquivo `settings.json` controla o comportamento do Claude Code. Existem múltiplos escopos com ordem de precedência:

### Hierarquia de configuração

| Prioridade | Escopo | Local | Uso |
|-----------|--------|-------|-----|
| 1 (maior) | Managed | Servidor | Políticas organizacionais (IT/Enterprise) |
| 2 | User | `~/.claude/settings.json` | Preferências pessoais, todos os projetos |
| 3 | Project | `.claude/settings.json` | Compartilhado via git com a equipe |
| 4 (menor) | Local | `.claude/settings.local.json` | Pessoal, não versionado |

### Principais configurações

**Modelo e comportamento:**
```json
{
  "model": "opus",
  "alwaysThinkingEnabled": true,
  "effortLevel": "high"
}
```

**Permissões (allow/deny/ask por ferramenta):**
```json
{
  "permissions": {
    "allow": ["Read", "Glob", "Grep"],
    "deny": ["Bash(rm *)"],
    "ask": ["Edit", "Write"]
  }
}
```

**Hooks (automações pré/pós execução):**
```json
{
  "hooks": {
    "preToolCall": [
      {
        "matcher": "Bash",
        "command": "echo 'Executando comando bash...'"
      }
    ]
  }
}
```

**Variáveis de ambiente:**
```json
{
  "env": {
    "NODE_ENV": "development",
    "API_KEY": "..."
  }
}
```

**Servidores MCP, subagentes customizados, plugins e sandboxing** também são configurados aqui.

Documentação oficial: https://code.claude.com/docs/en/settings.md

---

## 7. Integração MCP (Model Context Protocol)

MCP é um **protocolo aberto** que permite ao Claude Code se conectar a ferramentas externas, fontes de dados e serviços de forma padronizada.

### Como funciona

Servidores MCP expõe **ferramentas**, **recursos** e **prompts** que Claude Code pode usar. A comunicação acontece via:

| Tipo | Descrição |
|------|-----------|
| **stdio (local)** | Servidor roda como processo local |
| **HTTP/SSE (remoto)** | Servidor hospedado na nuvem |
| **Plugins** | Servidores MCP empacotados como plugins |

### Configuração

Arquivo `.mcp.json` na raiz do projeto (compartilhado) ou em `~/.claude/.mcp.json` (global):

```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_TOKEN": "ghp_..."
      }
    }
  }
}
```

### Integrações populares

| Servidor MCP | Função |
|-------------|--------|
| GitHub | Issues, PRs, repositórios |
| Slack | Mensagens e canais |
| PostgreSQL | Consultas ao banco de dados |
| Jira | Tickets e sprints |
| Google Drive | Documentos e planilhas |
| Sentry | Monitoramento de erros |

### Descoberta de ferramentas

Quando muitos servidores MCP estão configurados, Claude Code usa **Tool Search** para descobrir ferramentas relevantes sob demanda, sem carregar todas na memória.

Prompts MCP aparecem como comandos customizados no formato `/mcp__<servidor>__<prompt>`.

Documentação oficial: https://code.claude.com/docs/en/mcp.md

---

## Referências

| Recurso | Link |
|---------|------|
| Documentação Claude Code | https://code.claude.com/docs/en/overview.md |
| Skills | https://code.claude.com/docs/en/skills.md |
| Comandos | https://code.claude.com/docs/en/commands.md |
| Settings | https://code.claude.com/docs/en/settings.md |
| MCP | https://code.claude.com/docs/en/mcp.md |
| Agent Teams | https://code.claude.com/docs/en/agent-teams.md |
| CLI Reference | https://code.claude.com/docs/en/cli-reference.md |
| Anthropic Blog | https://www.anthropic.com/blog |
