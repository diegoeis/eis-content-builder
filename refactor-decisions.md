# Refactor Decisions — eis-content-builder v0.6.0

> Contexto: redesign do plugin iniciado por `/writer-setup` em maio 2026.
> Este arquivo registra decisões consolidadas E o débito técnico nas
> outras skills (writer-create, writer-calibrate, etc.) que ainda
> precisam ser atualizadas para a v0.6.0.

---

## Status

- **`/writer-setup` v0.6.0**: implementada, testada em sessão real, com
  vários ajustes incrementais (browser-tool, lazy channel-templates,
  no-narração de tools, output_language por agent, etc.). Score Gold
  (~82) no eval-orchestrator após correções.
- **`/writer-create` v0.6.0**: refatorada em maio 2026. Score Gold (80)
  no eval-orchestrator. Discovery pointer-first (Opção D), lazy channel
  materialization no Step 3 com fallback explícito de
  `${CLAUDE_PLUGIN_ROOT}`, Step 7 (archive) encolhido 80→25 linhas,
  Step 8 com browser-tool first, Step 9 lê style-rules inteiro como
  contrato. Tem 3 standbys conscientes (ver "Pendências writer-create"
  abaixo). **Está pronta no contrato dela mas depende de agents que
  ainda não foram refatorados** (draft-evaluator, opinion-extractor) —
  vai falhar em runtime até esses agents serem atualizados.
- **Outras skills (writer-calibrate, writer-save, writer-ideate,
  writer-index, writer-opinion-mine) + hook style-validator + agents
  (draft-evaluator, content-scout)**: ainda em v0.5 ou anterior.
  Várias referências mortas. Ver "Débito técnico restante" abaixo.

---

## Princípios operacionais (aplicam ao plugin todo)

1. **Inferir > perguntar.** Toda pergunta justifica sua existência.
2. **Pré-preencher > coletar do zero.** Usuário corrige, não digita.
3. **Mínimo viável agora, lapidação depois.** Cada skill termina rápido
   com o suficiente para a próxima skill funcionar.
4. **Skills orquestram; agents interpretam.** Skill não interpreta
   inputs — delega para agent e aplica o output.
5. **Degrade silencioso.** Falha de scraping/MCP/CLI nunca bloqueia —
   vira pergunta direta.
6. **Browser tool primeiro, WebFetch fallback, ask user se ambos
   falham.** Sem skip-list. Browser MCP (Claude in Chrome, Playwright)
   usa a sessão logada do usuário e funciona em LinkedIn/Twitter/etc.
   WebFetch é fallback. Se ambos falham, o agent registra
   `links_failed` e sugere PDF do perfil.
7. **Retry silencioso de agents.** 1 retry sem avisar. Segunda falha,
   surface o erro com motivo.
8. **JSON em vez de YAML para configs.** Mais fácil de parsear em
   Python nativo, melhor para agents. YAML só em frontmatter de
   markdown (convenção do ecossistema).
9. **Não narrar tool calls ou internals.** Usuário não precisa ler
   "Vou renderizar o formulário", "rendering elicitation", "agora vou
   rodar o voice-analyzer". Tool names e internal step numbers ficam
   fora da prosa user-facing.
10. **Headers em inglês sempre, conteúdo segue `output_language`.**
    Reference files têm headings/labels em inglês (fazem parte do
    contrato agent ↔ skill); a prosa substantiva (bio, princípios de
    voz, posições) segue o idioma do usuário.
11. **`cp` preferível a `Read+Write` para arquivos estáticos, com
    fallback Read+Write quando o sandbox bloqueia o source path.**

---

## Estado final acordado (workspace structure)

```
{workspace}/                              ← {primeiro-nome}-writer-profile
├── CLAUDE.md                             ← contrato operacional + hierarquia de voz
├── .claude/
│   └── eis-content-builder.local.json    ← config canônico (channels, archive, research, save_preferences, language, ideation)
├── references/                           ← 4 arquivos + baseline-forbidden por idioma
│   ├── voice-fingerprint.md              ← fingerprint + few-shot examples (CONSOLIDADO)
│   ├── style-rules.md                    ← rules prescritivas (gerado pelo voice-analyzer)
│   ├── author-profile.md                 ← identidade + mini_bio + expertise + audience + themes
│   ├── opinion-map.md                    ← posições do autor (populada por opinion-extractor no setup)
│   └── baseline-forbidden-<lang>.md      ← lista language-specific de frases proibidas
├── channel-templates/                    ← VAZIA no setup; materializada lazy por /writer-create
├── sample-sources/                       ← corpus original (input do voice-analyzer; não lido em runtime por outras skills)
├── drafts/                               ← peças escritas pelo plugin
└── eis-article-index.json                ← (opcional) índice do article archive

$HOME/.claude/
└── eis-content-builder.pointer.json      ← fallback de discovery quando skill roda fora do workspace
```

**Nome da pasta:** sempre `{primeiro-nome}-writer-profile`, slugificado e
minúsculo. Setup cria essa subpasta dentro da pasta-pai indicada pelo
usuário.

---

## Discovery do workspace (afeta TODAS as skills)

Cascata de 2 níveis:

1. **Local discovery.** Skill verifica se `cwd` está dentro de um
   workspace — busca local por `.claude/eis-content-builder.local.json`
   no `cwd` ou qualquer ancestral (walk-up até `/`). Primeiro hit ganha.
2. **Pointer fallback.** Se não achar local, lê
   `$HOME/.claude/eis-content-builder.pointer.json` → extrai
   `workspace_path` → carrega `.local.json` do workspace.
3. **Pergunta o path.** Se nenhum dos dois funciona (pointer ausente
   ou apontando pra path inexistente), prompt direto ao usuário.

**Regra de falha:** se pointer existe mas `workspace_path` não existe
no disco → orienta a rodar `/writer-setup`.

---

## Princípios de leitura para `/writer-create` (CRÍTICO)

Quando você for refatorar `/writer-create`, segue esta ordem de Tier:

### Tier 1 — autenticidade de voz (imexível)

1. `references/style-rules.md` — declarado, ganha em conflito.
2. `references/voice-fingerprint.md` — métricas + few-shot examples
   (consolidados nesse arquivo desde v0.6.0).
3. `channel-templates/<channel>.md` — só do canal solicitado.
   **MATERIALIZA SE NÃO EXISTIR** (ver "Lazy channel materialization"
   abaixo).

### Tier 2 — autenticidade de posição

4. `references/opinion-map.md` — early-exit quando vazio/scaffolded
   (populada no setup, mas pode estar vazia em runs de teste).

### Tier 3 — contexto situacional

5. `references/author-profile.md`
6. `.claude/eis-content-builder.local.json`
7. `eis-article-index.json` — **só matches relevantes ao tópico**, não
   JSON inteiro.

### Tier 4 — nunca ler em runtime

8. `sample-sources/` — input do `voice-analyzer` apenas. Fingerprint
   destila tudo que precisa estar acessível em runtime.

---

## Lazy channel materialization (CRÍTICO para `/writer-create`)

`/writer-create` é responsável por materializar o channel-template
**inline** (não delega para outra skill). Procedure quando
`/writer-create` é invocada com `--channel <name>`:

1. Checa se `{workspace}/channel-templates/<name>.md` existe. Se sim,
   usa.
2. Se não, lê source template em
   `${CLAUDE_PLUGIN_ROOT}/skills/writer-setup/assets/workspace-template/channel-templates/<name>.md`.
3. Aplica `template_customizations` recorded em `.local.json` sob
   `channels.<name>.template_customizations` (propostas pelo
   profile-inferencer no setup).
4. Escreve o template customizado em
   `{workspace}/channel-templates/<name>.md`.
5. Atualiza `channels.<name>.materialized: true` no `.local.json`.
6. Prossegue com o draft.

Para canais sem template built-in (`youtube`, `medium`, etc.,
`has_template: false`), `/writer-create` cai numa estrutura genérica
inferida em runtime e escreve um starter template no workspace para
runs subsequentes.

---

## Débito técnico restante (a corrigir junto com o refactor das skills)

A `/writer-setup` v0.6.0 está limpa. As **outras skills do plugin** têm
referências mortas. Lista por arquivo:

### `agents/draft-evaluator.md` — ALTO

- Description e Synopsis listam `style-examples.md`,
  `content-structures.md` como arquivos lidos. Esses arquivos não
  existem mais (consolidados no fingerprint + channel-templates).
- Linhas 32-33: lê de `style-examples.md` e `content-structures.md`.
- Linhas 56-57, 65, 74: lógica inteira referencia arquivos mortos.
- Linhas 78-80: headers em PT (`## Núcleo duro`, `## Posições em
  formação`, `## Não-posições`) — devem virar `## Hard core`,
  `## Forming positions`, `## Refusals`.

### `agents/content-scout.md` — ALTO

- Description, Synopsis e Procedure referenciam `.local.md` (YAML).
  Agora é `.local.json`.
- Linha 9: instrução de leitura aponta `.local.md`.

### `skills/writer-create/SKILL.md` — RESOLVIDO ✓

Refatorada em maio 2026. Score Gold 80 no eval-orchestrator.

Aplicado:
- Discovery em 2 níveis com **pointer-first** (Opção D): lê o
  `pointer.json` primeiro (1 file read no caso comum), walk-up só
  como fallback. Flag `--workspace <path>` adicionada para autores
  com múltiplos workspaces.
- **Lazy channel materialization** no Step 3 com fallback explícito
  de `${CLAUDE_PLUGIN_ROOT}`. STATUS distingue 3 casos: template
  built-in usado, starter por `has_template=false`, starter por
  plugin root indisponível (WARN — risco de voice regression).
- Tier 1-3 (sem proibição explícita de Tier 4 — overkill).
- Headers EN no opinion-map (`## Hard core`, `## Forming positions`,
  `## Neutral zones`, `## Refusals`, `## Tensions and synergies
  between topics`). Tolerância de PT preservada para workspaces
  antigos.
- `.local.json` em vez de `.local.md`.
- `${OUTPUT_LANGUAGE}` aplicado em toda prosa user-facing (errors,
  log descritivo, prompts interativos, body do draft). STATUS line
  permanece EN (contrato de automação).
- Browser-tool first → WebFetch fallback → ask user (Step 8).
- Step 9 lê `style-rules.md` inteiro como contrato vinculante (não
  só forbidden list).
- Step 7 (archive) encolhido de 80 → 25 linhas: sem scoring numérico
  (+3/+2/+1), sem buckets A/B/C, mantida regra "filtre antes de
  carregar com `jq`/`awk`/`python`, cap 50", mantidas as 4 hard
  rules. Decisões em 3 ações (link / flag repetition / reusable
  snippet).
- Frontmatter base agora vem do `## Frontmatter` block do
  channel-template materializado (não mais `content-structures.md`).
- Menções históricas removidas (sem `since v0.6.0`, `legacy configs`,
  `v0.4.x`).

**Bloqueio em runtime:** depende de `draft-evaluator` e
`opinion-extractor` que ainda referenciam arquivos mortos. Refatorar
esses agents antes de testar fim-a-fim.

### `skills/writer-opinion-mine/SKILL.md` — ALTO

- Linha 52: path antigo `workspace-template/references/opinion-map.md`
  (sem `skills/writer-setup/assets/`).
- Linhas 99, 109, 112, 124, 125: headers PT (`## Núcleo duro`,
  `## Posições em formação`, `## Zonas neutras`, `## Não-posições`,
  `## Sinergias e tensões entre temas`).
- Discovery em 4 níveis (precisa virar 2).

### `skills/writer-index/SKILL.md` — ALTO

- Discovery em 4 níveis (linhas 27-41). Precisa virar 2 níveis.
- Várias menções a `.local.md` (YAML). É `.local.json`.

### `skills/writer-calibrate/SKILL.md` — ALTO

- Não vi grep direto na auditoria, mas provavelmente:
  - Discovery antigo.
  - Atualiza `style-examples.md` (não existe mais — ajustes vão para
    a seção `## Few-shot examples` dentro do voice-fingerprint).
  - Headers PT do opinion-map.

### `skills/writer-save/SKILL.md` — MÉDIO

- Discovery antigo.
- Lê save-preferences de `references/save-preferences.md` (não existe
  mais — está em `.local.json` sob `save_preferences` array).
- `--remember` atualiza markdown (deve atualizar JSON).

### `skills/writer-ideate/SKILL.md` — MÉDIO

- Discovery antigo.
- Provavelmente referência `.local.md`.

### `hooks/style-validator.md` — MÉDIO

- Linha 46: header `## Posições em formação` (PT).
- Lê `style-rules.md + voice-fingerprint.md` — OK conceitualmente
  (esses arquivos existem na v0.6.0), mas confirmar o resto da lógica.
- Discovery — confirmar que respeita cascata de 2 níveis.

### `README.md` — RESOLVIDO ✓

Reescrito durante a auditoria. Estrutura nova do workspace, schema do
`.local.json` em JSON, discovery em 2 níveis, lazy channel
materialization, browser-tool, changelog v0.6.0.

### Limpeza física pendente (rm manual no host)

Sandbox bloqueou delete. Você precisa rodar no host:

```bash
cd /Users/diegoeis/obs-notes/prompts/skills-plugins/eis-content-builder/plugin
rm skills/writer-setup/assets/workspace-template/references/style-examples.md
rm skills/writer-setup/assets/workspace-template/references/content-structures.md
rm skills/writer-setup/assets/workspace-template/references/save-preferences.md
rm skills/writer-setup/assets/workspace-template/voice-fingerprint.md
rmdir skills/writer-setup/assets/docs
rm -rf skills/writer-setup/assets/scripts/__pycache__
rm .DS_Store
```

`prd-plugin.md` já foi movido para `docs/` na raiz do repo (fora da
pasta `plugin/` que vira zip).

---

## Pendências writer-create (standbys conscientes)

Três decisões deixadas em standby na refatoração de maio 2026, para
analisar com dados de uso real antes de implementar:

### 1. Step 6b — Voice sample antes do body (modo interactive)

Hoje em `--interactive` o usuário aprova um outline (bullets de
beats). Só vê a voz/tom quando o draft está pronto. Se o tom não
ficou certo, retrabalho via eval-loop ou `/writer-calibrate`.

Proposta: entre o outline (Step 6) e a escrita do body (Step 9),
escrever apenas **título + tese de 1 frase + primeiro parágrafo de
abertura** (~80-150 palavras), apresentar ao usuário e pedir
aprovação. Loop max 2x antes de seguir. Silent mode pula.

**Custo:** 1 LLM pass extra (~150 palavras) + 1 user decision.
**Ganho:** calibração precoce de voz/tese antes de escrever o body
inteiro.

**Status:** aprovado em princípio. Diego quer mensurar primeiro
o custo total dos passos anteriores (1-6) — preocupação de que o
fluxo já esteja longo.

### 2. Step 11 — Opinion extraction como hook?

Hoje Step 11 roda `opinion-extractor` em sequência, depois do draft
estar no disco e do eval ter rodado. Atrasa o STATUS final ao
usuário em alguns segundos.

Proposta avaliada e descartada: virar PostToolUse hook.
- Hooks só funcionam no Claude Code, não no Desktop. Usuários
  Desktop nunca rodariam opinion-extractor.
- Hook fire-and-forget — falha do extractor vira log de Claude Code
  que ninguém lê. Hoje, falha entra no STATUS.
- PostToolUse roda depois de cada Write/Edit; filtrar por path/skill
  é frágil.

Alternativa viável (não aplicada ainda): reordenar Step 12 para
emitir o STATUS line + path ANTES do extractor rodar, e o resultado
da extração entra como linha adicional do log. Usuário vê o draft
mais cedo.

**Status:** Diego vai analisar com uso real antes de decidir.

### 3. Description inflada (custo em triggering accuracy)

A description atual tem ~80 palavras de detalhe mecanístico
(`drafts/`, eval-loop, opinion-extractor, lazy materialization,
browser-tool first, output_language, Tier 1-3). Eval-judge da
rodada pós-tuning apontou que isso adiciona ruído sem melhorar
precisão de trigger. Custo: ~-0.07 em triggering_accuracy.

Proposta de enxugamento (não aplicada por decisão consciente):

```
Write a piece of content in the author's voice. Saves to drafts/,
never to chat. Use when the user says "write an article about",
"create a LinkedIn post", "draft a newsletter", "escreve um post
sobre", "escreve um artigo sobre", "quero um ensaio sobre", or
runs /writer-create. Silent by default — safe for automation.
--interactive for outline approval. Outputs STATUS: OK|WARN|BLOCKED.
```

Sozinho, deve recuperar ~+0.05-0.08 em triggering e voltar o score
pra ~82-83.

**Status:** Diego decidiu manter como está nesta rodada. Reavaliar
depois.

---

## Incoerências menores apontadas pelo eval (writer-create)

Achados do eval-orchestrator de maio 2026 que NÃO foram corrigidos
ainda (custo baixo, prioridade média):

1. **Step 8 "No skip-list" é referência órfã.** Skip-list foi
   removida com a transição para browser-tool-first, mas a frase
   ainda aparece. Trocar por uma afirmativa positiva ou remover.

2. **Step 11 "verify it did" é imperativo vago.** A instrução "the
   agent caps to medium in single mode (verify it did)" não diz o
   que fazer se o agent não capou. Falta else-branch explícito.

3. **Step 11 não realimenta Step 10.** Opinions extraídas podem
   alterar a tese implícita do draft, mas a skill termina sem
   revalidar. Incoerência semântica, não bug crítico.

4. **Step 12 "Automation contract" duplica conteúdo.** ~8 linhas no
   final do Step 12 repetem o que já está no synopsis e na format
   table. Marginal over-specification.

**Status:** todos lidos, todos deixados para próxima rodada.

---

## Pendências de design — decisões tomadas

1. **Adicionar canal novo após setup:** usuário edita manualmente em
   `channel-templates/` OU `/writer-create` materializa lazy quando
   solicitado pela primeira vez. Sem skill dedicada.
2. **`/writer-calibrate` e examples:** edita pontualmente o
   `voice-fingerprint.md` na seção `## Few-shot examples`. Regenera
   completo via voice-analyzer só quando o usuário pede explicitamente.
3. **Custo de regenerar voice-fingerprint:** pontual por default;
   regenera só quando pedido explícito.
4. **CONNECTORS.md do plugin:** adiado. Criar depois se houver demanda
   real.
5. **AGENTS.md:** adiado. Manter só CLAUDE.md por enquanto.
6. **Update e repair modes da `/writer-setup`:** adiados para v0.6.1+.
   v0.6.0 só faz first-time, short-circuit com mensagem clara nos
   outros casos.

---

## Roadmap v0.7+ — Hooks `PreToolUse` para enforcement determinístico

**Referência:** [aihero.dev — How To Use Claude Code Hooks To Enforce
The Right CLI](https://www.aihero.dev/how-to-use-claude-code-hooks-to-enforce-the-right-cli).

**Premissa:** regras hoje em prosa no SKILL.md são probabilísticas — o
LLM "lembra" 95% das vezes. Hooks `PreToolUse` bloqueiam tecnicamente
a chamada de ferramenta que viola a regra. Resultado: garantia técnica
+ menos texto repetido nas skills + score melhor em `token_efficiency`.

**Limitação importante:** hooks só funcionam no **Claude Code**, não no
**Claude Desktop**. Usuários Desktop continuam dependendo da prosa nas
skills como fallback.

### Hook 1 — `PreToolUse` no `Write`/`Edit` para workspace boundary (ALTO valor)

A invariant 3 da writer-setup diz "Never write outside the chosen
workspace path". Um hook que lê `tool_input.file_path` e valida contra
o `workspace_path` do `.local.json` impede tentativas acidentais
(especialmente quando o usuário invoca skills do plugin em pastas
diferentes).

**Implementação esperada:** ~40 linhas de bash em
`hooks/enforce-workspace-boundary.sh`. Hook config em `hooks/hooks.json`
com matcher `Write|Edit`.

### Hook 2 — `PreToolUse` para paths efêmeros em Bash/Write/Edit (MÉDIO valor)

A writer-setup já valida inline. Hook adiciona defesa em profundidade
global: qualquer skill do plugin que tente escrever em `/tmp/`,
`/sessions/`, `/var/folders/`, `/private/tmp/`, `/worktrees/*` é
bloqueada.

### Quando fazer

- **v0.7+**, depois de ter dados de uso real do v0.6.0. Quais regras o
  LLM está esquecendo na prática? Talvez o diagnóstico mude as
  prioridades acima.

### Hook 3 originalmente proposto (skip-list de scraping) — REMOVIDO

Decidimos que browser-tool é o caminho preferido para scraping social
(usa sessão logada). Não tem mais skip-list, então não tem hook de
skip-list. Substituído pela cascata browser → WebFetch → pergunta
descrita no princípio operacional 6.

---

## Schema do `eis-content-builder.local.json`

```json
{
  "workspace_path": "/Users/diego/.../diego-writer-profile",
  "initialized_at": "2026-05-17",
  "version": "0.6.0",

  "author": {
    "first_name": "diego",
    "full_name": "Diego Eis"
  },

  "language": {
    "default": "pt-BR",
    "technical_terms_in": "en"
  },

  "channels": {
    "blog": {
      "url": "https://tableless.com.br",
      "cms": "ghost",
      "publish_via": "manual",
      "has_template": true,
      "materialized": false,
      "template_customizations": {
        "target_length_words": [800, 1300],
        "formatting_notes_addition": null,
        "anti_pattern_additions": [],
        "rationale": "Median word count across blog samples: 1050"
      }
    },
    "newsletter": {
      "shares_url_with": "blog",
      "platform": "ghost",
      "has_template": true,
      "materialized": false,
      "template_customizations": null
    },
    "linkedin": {
      "profile_url": "https://linkedin.com/in/diegoeis",
      "posting_tool": "manual",
      "has_template": true,
      "materialized": false,
      "template_customizations": null
    },
    "youtube": {
      "active": true,
      "has_template": false,
      "materialized": false,
      "template_customizations": null
    }
  },

  "research_sources": {
    "trusted_blogs": [],
    "rss_feeds": [],
    "people_to_watch": [],
    "avoid_sources": []
  },

  "article_archive": {
    "enabled": true,
    "path": "/Users/diego/.../writings",
    "file_pattern": "**/*.md",
    "toolchain": "obsidian",
    "schema": {
      "title_property": "title",
      "tags_property": "tags",
      "status_property": "status",
      "published_values": ["published"],
      "date_property": "date",
      "url_property": "permalink",
      "excerpt_property": "excerpt"
    },
    "index_file": {
      "path": "/Users/diego/.../eis-article-index.json",
      "format": "json"
    }
  },

  "save_preferences": [],

  "ideation": {
    "exclude_themes": [],
    "preferred_angles": [],
    "default_channel": "blog"
  }
}
```

**Campos novos em v0.6.0 (relevantes para outras skills):**
- `channels.<name>.has_template` — se o plugin tem template built-in.
- `channels.<name>.materialized` — `/writer-create` setta `true` após
  primeira materialização.
- `channels.<name>.template_customizations` — propostas do
  profile-inferencer; aplicadas no momento da materialização.
- `save_preferences` agora é array de objetos JSON (era markdown).

---

## Schema do `eis-content-builder.pointer.json`

```json
{
  "workspace_path": "/Users/diego/.../diego-writer-profile",
  "initialized_at": "2026-05-17"
}
```

(Sem campo `version` — discutimos e decidimos que versão é audit
metadata, fica só no `.local.json`. Pointer é só apontador.)

---

## Contratos importantes (referenciar ao refatorar outras skills)

### `voice-analyzer` agent — output

Retorna dois blocos na resposta:

1. Summary curto (~300 palavras): metrics, samples processed,
   `language_detected` (quando `detect_language: true`), warnings.
2. `## Style-rules content blocks` — blocos pré-formatados nomeados
   após os placeholders do `style-rules.md` template:
   `VOICE_PRINCIPLES`, `SENTENCE_PATTERNS`, `ONE_LINE_PUNCHES`,
   `OPENING_PATTERNS`, `CLOSING_PATTERNS`, `PREFERRED_EXPRESSIONS`,
   `CONTRAST_FORBIDDEN`, `CHANNEL_OVERRIDES`. A skill consumidora
   copia verbatim.

Cada princípio em `VOICE_PRINCIPLES` tem **3 partes obrigatórias**:
regra acionável + métrica/observação que sustenta + exemplo verbatim
do corpus. Não é métrica formatada como prosa.

### `opinion-extractor` agent — output

Retorna markdown estruturado. Headers em inglês:
`## Hard core`, `## Forming positions`, `## Tensions and synergies
between topics`, `## Refusals`, `## Neutral zones`. Confidence levels:
`high`, `medium`, `discarded`.

Cada item tem `Apply patch` block com `target_section`, `insert_after`,
`block` — calling skill copia verbatim via `Edit`.

### `profile-inferencer` agent — output

JSON estruturado (≤1.5 KB) com `fields_inferred` (cada campo com
`value`, `confidence`, `source`), `fields_null`, `links_scraped` (com
`method`), `links_failed`, `channel_template_proposals`.

Browser-tool first (auto-detectado), WebFetch fallback, pede PDF do
perfil quando ambos falham.

### `detect-archive-schema.py` script — output

JSON na stdout. Exit 0 success / non-zero failure. Output inclui
`toolchain`, `file_pattern`, `schema` (cada role), `samples_analyzed`,
`field_frequency`, `warnings`.

Fallback automático: `archive-detector` agent (LLM) com mesmo schema
de output.

---

## Mudança de invariante crítica: language policy

Versões antigas: "Plugin UI is always in English."

v0.6.0: **"Skill prose (SKILL.md files) is in English; user-facing
prompts follow `${OUTPUT_LANGUAGE}`."** O texto que o usuário lê na UI
— perguntas, mensagens de erro, telas de confirmação — é no idioma
dele (detectado da conversa, refinado pelo analyzer). O inglês nos
SKILL.md é para o orquestrador, não para o usuário. Reference files
no workspace também seguem o idioma do usuário, com exceção dos
headings/labels que ficam EN por serem parte do contrato.

Skills sendo refatoradas: aplicar essa regra. Toda string que vai pro
usuário é traduzida pra `${OUTPUT_LANGUAGE}` no momento de uso.

---

## O que `/writer-create` precisa fazer (em ordem)

Esta seção é o briefing direto para a próxima refatoração.

1. **Discovery em 2 níveis** — local walk-up → pointer.json → ask.
2. **Estabelecer `${OUTPUT_LANGUAGE}`** — lê de `.local.json
   .language.default` (já foi resolvido no setup; aqui só carrega).
3. **Validar argumentos.** Topic obrigatório, `--channel` opcional
   (default vem de `ideation.default_channel`).
4. **Materializar channel-template se preciso.** Procedure documentado
   acima. Atualiza `materialized: true` no config após escrever.
5. **Carregar contexto (Tier 1-3 da seção "Princípios de leitura").**
   Não ler sample-sources.
6. **Outline (modo interactive) ou direto pro draft (modo silent).**
7. **Pesquisa de sources via browser-tool first, WebFetch fallback.**
   Aplicar princípio operacional 6.
8. **Consultar article index** se `article_archive.enabled` — só
   matches relevantes, não JSON inteiro.
9. **Cross-reference opinion-map** — se topic está em
   `## Hard core` (em EN), usa a posição como tese.
10. **Escrever draft em `drafts/`** com YAML frontmatter completo.
11. **Rodar draft-evaluator** em loop (max 3 iterations) — pendente
    refatorar o agent também.
12. **Rodar opinion-extractor (single mode)** após o draft pra
    capturar posições novas — agent já está atualizado.
13. **Output: STATUS line + path + 2-sentence preview**, nunca o
    body inteiro no chat.

---

## Atualizações por hops (resumo do que mudou nessa sessão e outros chats)

- **Channel-templates lazy.** Setup não materializa; `/writer-create`
  faz no primeiro uso. Customizations vivem no `.local.json`.
- **Browser-tool first.** Sem skip-list. Cascata: browser MCP →
  WebFetch → ask user.
- **Headers EN no opinion-map.** Conteúdo segue `output_language`.
- **Style-rules prescritivo, não descritivo.** Voice-analyzer agora
  gera blocos com rule + metric + example verbatim. Setup copia
  verbatim, não regenera.
- **Signature one-line punches.** Seção nova em style-rules.md que
  captura a marca de frase-parágrafo curta (3-8 palavras isoladas).
- **Versão do plugin não é mais lida em runtime.** Hardcoded como
  string em `plugin.json` e no `.local.json` (linha do Step 4.2 do
  setup). Audit metadata only.
- **`prd-plugin.md` movido pra `docs/` na raiz do repo**, fora do
  plugin que vira zip.
- **README atualizado** com toda a v0.6.0.
