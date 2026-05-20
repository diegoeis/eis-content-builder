# Baseline forbidden patterns — pt-BR

> Loaded by `/writer-create` and `/writer-calibrate` ONLY if the workspace
> `language.default` is `pt-BR`. These patterns read as generic LLM output,
> coach-speak, or empty corporate framing in Portuguese. Do not soften
> them, do not rephrase them — **go straight to the claim instead**.

> **Registro único de inversões panfletárias.** A seção "Inversões
> panfletárias" abaixo é o ÚNICO lugar onde esse padrão deve ser
> registrado neste workspace. Nem `style-rules.md` (Hard Rules ou
> CONTRAST_FORBIDDEN), nem `voice-fingerprint.md` devem repetir essas
> variantes. Se você é o `voice-analyzer` populando CONTRAST_FORBIDDEN,
> NÃO inclua inversões — elas já estão cobertas aqui.

## Phrases

- "O argumento central é simples"
- "Aqui vai uma verdade que poucos admitem abertamente."
- "A lição? Dados importam mais que opinião."
- "No final das contas, tudo se resume a..."
- "Vamos ser honestos aqui:"
- "Neste artigo, vamos explorar..." (introdução anunciada)
- "Como todos sabemos..." (paternalismo)
- "Transforme sua vida / carreira / empresa" (tom coach)
- "Entregando valor para o negócio" (vazio corporativo)
- "A verdade inconveniente"
- "Passei os últimos dias refletindo"
- "clareza brutal"
- "A lição?" (como início de parágrafo ou transição)
- "Mas o que perdemos no caminho?" (como início de parágrafo ou transição)
- "A verdade é que..."
- "Por que isso importa? Porque..."
- "Agora vem a pergunta que realmente importa:"
- "Os números chamam atenção:"
- "O padrão que se repete é simples."

## Inversões panfletárias (registro único — não duplicar em outro lugar)

Estrutura genérica: "Não é {X}. É {Y}." e variantes. Soa a manifesto de
LinkedIn, panfleto político ou copy motivacional. Vale para qualquer
combinação de negação seguida de reafirmação reforçada na mesma
microestrutura — independente do que está no lugar de X e Y.

Variantes proibidas (todas equivalentes para fins de detecção):

- "Não é X. É Y." (forma canônica)
- "Não é sobre X. É sobre Y."
- "Não é que X. É que Y."
- "O problema nunca foi X. Foi Y."
- "A pergunta não é X. É Y."
- "Isso não é X. É Y."
- "X não é o ponto. O ponto é Y."

**Detecção:** qualquer parágrafo que contenha negação curta de uma
opção seguida (na mesma frase ou na frase imediatamente posterior) por
afirmação curta de uma alternativa, com paralelismo sintático. Se
houver dúvida, conta como violação.

**Correção:** afirme Y diretamente, sem negar X primeiro. Se o
contraste com X for realmente importante, desenvolva o contraste em
prosa (2-3 frases) em vez de comprimir em paralelismo.

## Other constructions

- Qualquer frase "setup" antes do ponto (ex.: "Antes de entrar no tema,
  vale notar que..."). Corte o setup — comece com o ponto.
- Perguntas retóricas como transição ("Por que isso importa?", "E
  agora?") — diga a resposta direto.

**Rule of thumb:** se uma frase funciona como rampa para a afirmação
real, apague a rampa e comece pela afirmação.
