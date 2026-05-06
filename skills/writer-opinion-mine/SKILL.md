---
name: writer-opinion-mine
description: Extract, refine or expand the author's opinion map - the structured record of what the author thinks about the topics they write about. Use when the user says "vamos mapear minhas opinies", "quero registrar o que penso sobre X", "atualizar opinion-map", "entrevista socrtica sobre minhas ideias", "map my opinions", "calibrate my positions", or runs `/writer-opinion-mine`. Runs a focused Socratic interview in batches of 3-5 short questions at a time (never cascade), targeting a single topic per session unless the user asks for breadth. Reads the existing `references/opinion-map.md` first to avoid re-asking settled positions and to surface tensions. Writes each confirmed position back to the file with confidence level (high / medium / neutral / refusal), evidence pointer if available, and known opposition. Never fabricates positions - if the author's answer is ambiguous, marks it as "em formao" with the condition that would firm it up.
argument-hint: "[optional topic to focus | --tensions | --refusals | --authorities]"
allowed-tools: Read, Write, Edit, Glob, AskUserQuestion, TodoWrite
---

# Writer Opinion Mine

Help the author build a reproducible opinion map — what they actually think about the themes they publish on. You are an interviewer first, a writer second. You do **not** invent positions. You extract, formalize, and file.

## Invariant rules

Inherit from `{workspace}/CLAUDE.md`. Critical for this skill:

- **Never fabricate a position.** If the author hedges, record the hedge as "em formação" with the revising-condition they actually stated.
- **Never ask more than 5 questions at once.** Batches of 3–5, then wait.
- **Never ask questions already settled** in the existing opinion-map (re-reading is mandatory before asking).
- **Language follows the user.**
- **Changes to the file are surgical.** `Edit` one section; do not rewrite the whole document.

## Step 1 — Load workspace

1. `Read` `.claude/eis-content-builder.local.md`. Missing → "Run `/writer-setup` first." Stop.
2. Extract `workspace_path`.
3. `Read` in parallel (one message, multiple Read calls):
   - `{workspace}/CLAUDE.md`
   - `{workspace}/references/author-profile.md`
   - `{workspace}/references/opinion-map.md` (if missing, create from the template at `workspace-template/references/opinion-map.md` — keep placeholders, just scaffold the sections)
   - `{workspace}/references/voice-fingerprint.md` (for tone hints — do not use to guess positions)

## Step 2 — Route the session

Parse `$ARGUMENTS`:

- Specific topic (e.g. "autonomia do PM") → **topic mode** (Step 3).
- `--tensions` → **tension-mapping mode** (Step 4).
- `--refusals` → **refusal-mapping mode** (Step 5).
- `--authorities` → **authority-reading mode** (Step 6).
- Nothing → ask once with `AskUserQuestion`: "What do you want to map today — a specific topic, tensions between topics you've already covered, your refusals, or how you read the authorities in your field?"

One mode per session. No auto-switching.

## Step 3 — Topic mode

Goal: move a topic from unstructured thought → recorded position with opposition and counter-argument.

**3a. Frame the topic.** Paste the topic back to the user in one sentence. Ask once: "Confirma que é isso, ou refina?" Wait.

**3b. Check the map first.** Before asking anything, scan the existing `opinion-map.md` for this topic:
- If it already exists with high confidence → summarize what's recorded, ask "O que mudou? Quer revisar, aprofundar sinergias, ou passar para outro tema?" Then either update the existing entry or close.
- If it exists with medium confidence → open asking what would firm up the position.
- If absent → proceed to 3c.

**3c. First batch (core position).** Ask these — pick **3**, not more:

- "Se um mentorado te perguntasse sua posição sobre {topic} numa frase, qual seria?"
- "Qual frase sobre {topic} que circula no seu meio profissional você **rejeita**? E por quê?"
- "Quem é a autoridade mais citada sobre {topic} — e o que você acha da leitura dela?"
- "Você já defendeu essa posição em público? Onde? (pode ser link, pode ser 'em conversa')"
- "Qual é a crítica mais forte que alguém inteligente faria contra você sobre isso — e como você responde?"

Wait for answers. Do not fill gaps.

**3d. Confidence sort.** Based on the answers:

- Posição clara + contra-argumento articulado + (evidência no corpus ou menção de já ter defendido publicamente) → **alta confiança** (núcleo duro).
- Posição clara, mas contra-argumento fraco ou "ainda penso sobre" → **média** (em formação). Pergunta: "O que te faria mudar de ideia?"
- Posição não formada, só inclinação → **neutra**. Não registra como convicção; registra como zona neutra com motivo.

**3e. Second batch (opposition + synergy), only if 3d concluded alta/média.** Ask **2 questions**:

- "Quem discorda publicamente de você nesse tema? (pode ser pessoa, linha de pensamento, corrente)"
- "Esse tema conversa ou atrita com outro tema do seu mapa? (ex: se o mapa já tem 'X', pergunta explicitamente se {topic} se relaciona com X)"

**3f. Write to the file.** Single `Edit` call. Target the correct section (`## Núcleo duro` for alta, `## Posições em formação` for média, `## Zonas neutras` for neutra). Format strictly following the template in `opinion-map.md`. If it's a tension or synergy, **also** add a line to `## Sinergias e tensões entre temas`.

**3g. Log the change.** Append one line to `## Changelog` at the bottom of `opinion-map.md`: `{YYYY-MM-DD}: {topic} — {nova posição registrada | posição revisada | movida de formação → núcleo} (gatilho: /writer-opinion-mine)`.

**3h. Close.** Show: "Registrado em {seção} com confiança {nível}. Próximo tema, ou paramos aqui?"

## Step 4 — Tension-mapping mode

Goal: surface contradictions or synergies between topics already in the map.

**4a.** `Read` the map. Extract all topics from Núcleo duro + Em formação.
**4b.** Propose up to 3 pairs that look tensionable. Example: "Você tem 'A é X' e 'B é Y'. Essas posições se tocam ou atritam?"
**4c.** Batch of 3 questions max per pair, but only the pair the user picks. Do **not** run all 3 pairs.
**4d.** Write findings to `## Sinergias e tensões entre temas`. Single `Edit`.

## Step 5 — Refusal-mapping mode

Goal: make the "não-posições" section granular and useful.

**5a.** Ask **3** questions:
- "Quais temas você se recusa a escrever, mesmo tendo opinião?"
- "Quais temas você se recusa a escrever porque **não** tem opinião que mereça tinta?"
- "Há temas que você **já** escreveu e se arrepende? (sinaliza refusal retroativo)"

**5b.** Separate in the file into:
- `## Não-posições (recusas explícitas)` → primeira pergunta.
- `## Zonas neutras` → segunda pergunta.
- Se houver arrependimento → pergunta de follow-up única: "Quer registrar o novo limite ou revisar o artigo antigo?"

## Step 6 — Authority-reading mode

Goal: populate the authorities table. Each row clarifies deference vs. filtering.

**6a.** Ask **3** at a time:
- "Cite 3 autoridades do seu campo. Para cada uma, em uma frase: como você lê?"
- (Depois do primeiro lote) "Há alguém que você **sempre cita** mesmo discordando? Por quê?"
- "Alguém que você **nunca cita** mesmo sendo influente? Por quê?"

**6b.** Write rows to the authorities table. One `Edit` call per authority added.

## Step 7 — Session limits

- **Máximo de tempo sugerido**: 15 minutos por sessão. Diga isso na abertura.
- **Máximo de tópicos por sessão (topic mode)**: 1. Breadth é feito em múltiplas sessões curtas.
- **Nunca peça ao usuário para "descrever seu pensamento completo sobre X"**. Perguntas específicas extraem mais que perguntas abertas.

## Failure handling

- Author gives a truly non-committal answer ("sei lá, depende") → registra em `## Zonas neutras` com o "depende" como nota. Não força.
- Author contradiz uma posição já registrada → para a entrevista. Mostra a contradição. Pergunta: "Registrar a nova posição e mover a antiga para o changelog, ou refinar a antiga?"
- Author pede para pular uma pergunta → pula e não insiste.
- Topic já coberto e sem mudança → fecha a sessão honestamente: "Não temos o que registrar hoje. Quer abrir outro tema?"

## TodoWrite usage

Para sessão com 3+ lotes de perguntas: uma todo por lote + uma para escrita final + uma para changelog. Mantém leve. Pula para sessões de 1 lote.
