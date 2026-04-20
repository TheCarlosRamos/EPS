# Design System — Buscador OSINT Automatizado · PCDF

> **Disciplina:** Engenharia de Produto de Software (EPS) · UnB  
> **Projeto:** Buscador OSINT Automatizado — Polícia Civil do Distrito Federal  
> **Versão:** 1.0.0  

---

## Visão Geral

<img src="./assets/01-design-system-cover-pcdf-osint.png" alt="Design System Cover — PCDF OSINT" width="100%">

O design system do **Buscador OSINT Automatizado** garante consistência visual, acessibilidade e identidade institucional da PCDF em toda a interface. A identidade é construída sobre o azul institucional e o dourado da PCDF.

---

## 🎨 Design Tokens

### Paleta de Cores — Primary (Azul Institucional PCDF)

<img src="./assets/02-primary-color-scale.png" alt="Primary Color Scale" width="100%">

### Secondary — Dourado Institucional

<img src="./assets/03-secondary-color-scale.png" alt="Secondary Color Scale" width="100%">

### Status — Success

<img src="./assets/04-success-color-scale.png" alt="Success Color Scale" width="100%">

### Status — Warning

<img src="./assets/05-warning-color-scale.png" alt="Warning Color Scale" width="100%">

### Status — Error

<img src="./assets/06-error-color-scale.png" alt="Error Color Scale" width="100%">

### Neutral

<img src="./assets/07-neutral-color-scale.png" alt="Neutral Color Scale" width="100%">

### Spacing Scale (Base unit: 4px)

Escala: `4px · 8px · 12px · 16px · 24px · 32px · 48px · 64px`

<img src="./assets/08-spacing-scale.png" alt="Spacing Scale" width="100%">

### Border Radius

Tokens: `none (0) · sm (4px) · md (8px) · lg (12px) · xl (16px) · full (9999px)`

<img src="./assets/09-border-radius-tokens.png" alt="Border Radius Tokens" width="100%">

### Z-Index & Breakpoints

<img src="./assets/10-z-index-and-breakpoints.png" alt="Z-Index and Breakpoints" width="100%">

---

## 📝 Tipografia

### Headings — IBM Plex Mono (Display)

Escala: `H1 (48px) · H2 (36px) · H3 (28px) · H4 (22px) · H5 (18px) · H6 (14px)`

*(Veja frame `HEADINGS — IBM Plex Mono` no Figma — Página: 📝 Typography)*

### Body & Utility Types — Inter + IBM Plex Mono

Estilos: `Body LG · Body MD · Body SM · Caption · Overline · Code`

*(Veja frame `BODY & UTILITY TYPES` no Figma — Página: 📝 Typography)*

---

## 🧩 Componentes

### Botões

Variantes: `primary · secondary · gold (CTA) · danger · ghost` | Tamanhos: `LG (44px) · SM (32px)`

<img src="./assets/11-button-variants.png" alt="Button Variants" width="100%">

### Form Inputs

Campos: `CPF (mono) · Nome/Vulgo · E-mail · Telefone (mono) · Busca Federada`

<img src="./assets/12-form-inputs.png" alt="Form Inputs" width="100%">

### Data Table — Resultados da Busca OSINT

Status badges: `CONFIRMADO · ANALISANDO · PENDENTE · DESCARTADO`

<img src="./assets/13-data-table.png" alt="Data Table" width="100%">

### Alerts, Badges & Status Indicators

Alerts: `success · warning · error · info` | Badges: `ATIVO · INATIVO · PRIORIDADE · NOVO · OSINT · SIGILOSO`

<img src="./assets/14-alerts-and-badges.png" alt="Alerts and Badges" width="100%">

### Cards — Result & Stats

<img src="./assets/15-cards.png" alt="Cards" width="100%">

### Navigation — Sidebar + Tabs + Breadcrumbs

<img src="./assets/16-navigation-components.png" alt="Navigation Components" width="100%">

---

## 🌙 Dark Mode / Light Mode

### Dark Mode (Padrão operacional)

<img src="./assets/17-dark-mode-preview.png" alt="Dark Mode Preview" width="100%">

### Light Mode

<img src="./assets/18-light-mode-preview.png" alt="Light Mode Preview" width="100%">

---

## ♿ WCAG 2.1 AA — Auditoria de Contraste

**26 pares de cor testados · 3 cores corrigidas após auditoria · Mínimo 4.5:1 em todos os pares**

<img src="./assets/19-wcag-2-1-aa-contrast-audit.png" alt="WCAG 2.1 AA Contrast Audit" width="100%">

### Correções aplicadas após auditoria

| Par original | Contexto | Ratio antes | Correção | Ratio depois |
|---|---|---|---|---|
| `#8193A8` / `#FFFFFF` | Texto muted — light mode | 3.15:1 ❌ | `#5E6E85` | 5.19:1 ✅ |
| `#8193A8` / `#F5F7F9` | Texto muted — light surface | 2.93:1 ❌ | `#5E6E85` | 4.83:1 ✅ |
| `#5585D4` / `#1C2533` | Code text em surface-2 | 4.18:1 ❌ | `#91AEE4` | 6.89:1 ✅ |

---

## 🔧 Figma Variables

### Coleção: PCDF Design Tokens

| Token | Dark | Light |
|-------|------|-------|
| `color/bg/primary` | `#060A12` | `#F5F7F9` |
| `color/bg/surface-1` | `#0E1520` | `#FFFFFF` |
| `color/bg/surface-2` | `#1C2533` | `#E8ECF0` |
| `color/bg/surface-3` | `#2E3A4E` | `#CDD6DF` |
| `color/brand/primary` | `#2E64C0` | `#1A4A9E` |
| `color/brand/gold` | `#F5A623` | `#C87200` |
| `color/text/primary` | `#FFFFFF` | `#0E1520` |
| `color/text/secondary` | `#A9B7C6` | `#445165` |
| `color/text/muted` | `#8193A8` | `#5E6E85` ✦ |
| `color/border/default` | `#2E3A4E` | `#CDD6DF` |
| `color/border/focus` | `#2E64C0` | `#1A4A9E` |
| `color/status/success` | `#5CB87A` | `#18803F` |
| `color/status/warning` | `#F5A623` | `#C95E00` |
| `color/status/error` | `#EF5350` | `#C91C1C` |
| `color/status/info` | `#5585D4` | `#1A4A9E` |

> ✦ Valor corrigido para WCAG AA (era `#8193A8`, ratio 3.15:1 ❌)

### Coleção: Spacing

`spacing/4=4px · spacing/8=8px · spacing/12=12px · spacing/16=16px · spacing/24=24px · spacing/32=32px · spacing/48=48px · spacing/64=64px`

### Coleção: Border Radius

`radius/none=0px · radius/sm=4px · radius/md=8px · radius/lg=12px · radius/xl=16px · radius/full=9999px`

---

### Para acessar o design system completo, acesse a seguir:  
[Visualizar no Figma](https://www.figma.com/design/gAotIdNAKBThXKEZS1CyCb/EPS---PCDF?node-id=0-1&t=0wOZH1yc3o2loZtE-1)

*Design system criado para o projeto Buscador OSINT Automatizado — EPS/UnB · Grupo 13 · PCDF.*  
*Todas as cores validadas contra WCAG 2.1 AA. Todos os componentes construídos em Auto Layout no Figma.*

*Revisado por Alexandre Junior*