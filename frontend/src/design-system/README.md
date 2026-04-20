# Design System â€” Buscador OSINT Automatizado Â· PCDF

> **Disciplina:** Engenharia de Produto de Software (EPS) Â· UnB  
> **Projeto:** Buscador OSINT Automatizado â€” PolÃ­cia Civil do Distrito Federal  
> **VersÃ£o:** 1.0.0  

---

## VisÃ£o Geral

<img src="./assets/01-design-system-cover-pcdf-osint.png" alt="Design System Cover â€” PCDF OSINT" width="100%">

O design system do **Buscador OSINT Automatizado** garante consistÃªncia visual, acessibilidade e identidade institucional da PCDF em toda a interface. A identidade Ã© construÃ­da sobre o azul institucional e o dourado da PCDF.

---

## ðŸŽ¨ Design Tokens

### Paleta de Cores â€” Primary (Azul Institucional PCDF)

<img src="./assets/02-primary-color-scale.png" alt="Primary Color Scale" width="100%">

### Secondary â€” Dourado Institucional

<img src="./assets/03-secondary-color-scale.png" alt="Secondary Color Scale" width="100%">

### Status â€” Success

<img src="./assets/04-success-color-scale.png" alt="Success Color Scale" width="100%">

### Status â€” Warning

<img src="./assets/05-warning-color-scale.png" alt="Warning Color Scale" width="100%">

### Status â€” Error

<img src="./assets/06-error-color-scale.png" alt="Error Color Scale" width="100%">

### Neutral

<img src="./assets/07-neutral-color-scale.png" alt="Neutral Color Scale" width="100%">

### Spacing Scale (Base unit: 4px)

Escala: `4px Â· 8px Â· 12px Â· 16px Â· 24px Â· 32px Â· 48px Â· 64px`

<img src="./assets/08-spacing-scale.png" alt="Spacing Scale" width="100%">

### Border Radius

Tokens: `none (0) Â· sm (4px) Â· md (8px) Â· lg (12px) Â· xl (16px) Â· full (9999px)`

<img src="./assets/09-border-radius-tokens.png" alt="Border Radius Tokens" width="100%">

### Z-Index & Breakpoints

<img src="./assets/10-z-index-and-breakpoints.png" alt="Z-Index and Breakpoints" width="100%">

---

## ðŸ“ Tipografia

### Headings â€” IBM Plex Mono (Display)

Escala: `H1 (48px) Â· H2 (36px) Â· H3 (28px) Â· H4 (22px) Â· H5 (18px) Â· H6 (14px)`

*(Veja frame `HEADINGS â€” IBM Plex Mono` no Figma â€” PÃ¡gina: ðŸ“ Typography)*

### Body & Utility Types â€” Inter + IBM Plex Mono

Estilos: `Body LG Â· Body MD Â· Body SM Â· Caption Â· Overline Â· Code`

*(Veja frame `BODY & UTILITY TYPES` no Figma â€” PÃ¡gina: ðŸ“ Typography)*

---

## ðŸ§© Componentes

### BotÃµes

Variantes: `primary Â· secondary Â· gold (CTA) Â· danger Â· ghost` | Tamanhos: `LG (44px) Â· SM (32px)`

<img src="./assets/11-button-variants.png" alt="Button Variants" width="100%">

### Form Inputs

Campos: `CPF (mono) Â· Nome/Vulgo Â· E-mail Â· Telefone (mono) Â· Busca Federada`

<img src="./assets/12-form-inputs.png" alt="Form Inputs" width="100%">

### Data Table â€” Resultados da Busca OSINT

Status badges: `CONFIRMADO Â· ANALISANDO Â· PENDENTE Â· DESCARTADO`

<img src="./assets/13-data-table.png" alt="Data Table" width="100%">

### Alerts, Badges & Status Indicators

Alerts: `success Â· warning Â· error Â· info` | Badges: `ATIVO Â· INATIVO Â· PRIORIDADE Â· NOVO Â· OSINT Â· SIGILOSO`

<img src="./assets/14-alerts-and-badges.png" alt="Alerts and Badges" width="100%">

### Cards â€” Result & Stats

<img src="./assets/15-cards.png" alt="Cards" width="100%">

### Navigation â€” Sidebar + Tabs + Breadcrumbs

<img src="./assets/16-navigation-components.png" alt="Navigation Components" width="100%">

---

## ðŸŒ™ Dark Mode / Light Mode

### Dark Mode (PadrÃ£o operacional)

<img src="./assets/17-dark-mode-preview.png" alt="Dark Mode Preview" width="100%">

### Light Mode

<img src="./assets/18-light-mode-preview.png" alt="Light Mode Preview" width="100%">

---

## â™¿ WCAG 2.1 AA â€” Auditoria de Contraste

**26 pares de cor testados Â· 3 cores corrigidas apÃ³s auditoria Â· MÃ­nimo 4.5:1 em todos os pares**

<img src="./assets/19-wcag-2-1-aa-contrast-audit.png" alt="WCAG 2.1 AA Contrast Audit" width="100%">

### CorreÃ§Ãµes aplicadas apÃ³s auditoria

| Par original | Contexto | Ratio antes | CorreÃ§Ã£o | Ratio depois |
|---|---|---|---|---|
| `#8193A8` / `#FFFFFF` | Texto muted â€” light mode | 3.15:1 âŒ | `#5E6E85` | 5.19:1 âœ… |
| `#8193A8` / `#F5F7F9` | Texto muted â€” light surface | 2.93:1 âŒ | `#5E6E85` | 4.83:1 âœ… |
| `#5585D4` / `#1C2533` | Code text em surface-2 | 4.18:1 âŒ | `#91AEE4` | 6.89:1 âœ… |

---

## ðŸ”§ Figma Variables

### ColeÃ§Ã£o: PCDF Design Tokens

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
| `color/text/muted` | `#8193A8` | `#5E6E85` âœ¦ |
| `color/border/default` | `#2E3A4E` | `#CDD6DF` |
| `color/border/focus` | `#2E64C0` | `#1A4A9E` |
| `color/status/success` | `#5CB87A` | `#18803F` |
| `color/status/warning` | `#F5A623` | `#C95E00` |
| `color/status/error` | `#EF5350` | `#C91C1C` |
| `color/status/info` | `#5585D4` | `#1A4A9E` |

> âœ¦ Valor corrigido para WCAG AA (era `#8193A8`, ratio 3.15:1 âŒ)

### ColeÃ§Ã£o: Spacing

`spacing/4=4px Â· spacing/8=8px Â· spacing/12=12px Â· spacing/16=16px Â· spacing/24=24px Â· spacing/32=32px Â· spacing/48=48px Â· spacing/64=64px`

### ColeÃ§Ã£o: Border Radius

`radius/none=0px Â· radius/sm=4px Â· radius/md=8px Â· radius/lg=12px Â· radius/xl=16px Â· radius/full=9999px`

---


### Para acessar o design system completo, acesse a seguir:  
[Visualizar no Figma](https://www.figma.com/design/gAotIdNAKBThXKEZS1CyCb/EPS---PCDF?node-id=0-1&t=0wOZH1yc3o2loZtE-1)

*Design system criado para o projeto Buscador OSINT Automatizado â€” EPS/UnB Â· Grupo 13 Â· PCDF.*  
*Todas as cores validadas contra WCAG 2.1 AA. Todos os componentes construÃ­dos em Auto Layout no Figma.*

*Revisado por Alexandre Junior*
