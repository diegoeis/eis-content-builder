# Opinion Map — {{AUTHOR_NAME}}

Mapa de opiniões do autor. Carregado por `writer-ideate`, `writer-create` e `writer-calibrate`.

**Não é perfil de personalidade.** É registro operacional de:
- O que o autor pensa sobre os temas que escreve (convicções, posições em formação, zonas neutras)
- Onde as opiniões conversam ou atritam
- Como o autor lê as autoridades do campo
- O que o autor se recusa a opinar

Atualizado pela skill `/writer-opinion-mine` (entrevista socrática), por `/writer-calibrate` (quando uma correção sinaliza mudança de posição), ou manualmente pelo autor.

---

## Núcleo duro (convicções de alta confiança)

Temas onde a opinião é firme e já foi publicamente defendida. Alimentam tese direto.

Formato por item:
- **Posição**: uma frase afirmativa, voz ativa, sem hedging.
- **Evidência no corpus**: links para artigos/posts onde a posição aparece (quando conhecidos).
- **Quem discorda**: autoridades públicas que defendem o contrário.
- **Meu contra-argumento contra quem discorda**: uma frase que responde à crítica mais forte à sua posição.
- **Confiança**: alta.

### {{TOPIC_1}}

- **Posição**: {{POSITION_1}}
- **Evidência no corpus**: {{EVIDENCE_1}}
- **Quem discorda**: {{OPPOSITION_1}}
- **Contra-argumento**: {{COUNTER_1}}
- **Confiança**: alta

---

## Posições em formação (média confiança, sujeitas a revisão)

Temas onde há inclinação mas ainda calibra. O plugin deve sinalizar no outline que a posição é provisória.

Formato por item:
- **Posição atual**: frase afirmativa.
- **O que me faria mudar de ideia**: condição concreta (dado, observação, experiência).
- **Confiança**: média.

### {{FORMING_TOPIC_1}}

- **Posição atual**: {{FORMING_POSITION_1}}
- **O que me faria mudar de ideia**: {{FORMING_REVISE_1}}
- **Confiança**: média

---

## Zonas neutras (sem opinião firmada)

Temas que o autor escreve/pensa, mas sobre os quais ainda **não** quer soar opinativo. O plugin deve evitar inventar posição — prefere descrição, análise ou pergunta aberta quando esses temas aparecem.

- {{NEUTRAL_1}}
- {{NEUTRAL_2}}

---

## Não-posições (recusas explícitas)

Granular. Complementa `exclude_themes` do `CLAUDE.md`.

- {{REFUSAL_1}}
- {{REFUSAL_2}}

---

## Sinergias e tensões entre temas

Onde as opiniões conversam ou atritam entre si. Útil para propostas de artigo que articulam dois temas.

- **{{TOPIC_A}}** ↔ **{{TOPIC_B}}**: {{RELATION}}
  - Resolução (se houver): {{RESOLUTION}}

---

## Autoridades de referência (como o autor lê cada uma)

Como o autor cita cada figura pública do campo. Evita que o plugin trate toda autoridade com a mesma deferência.

| Autoridade | Como o autor lê | Onde concorda | Onde discorda |
|---|---|---|---|
| {{AUTHORITY_1}} | {{READ_1}} | {{AGREE_1}} | {{DISAGREE_1}} |

---

## Perfil operador (Graham-minimal, só o que ajuda a escrita)

Três campos — não um Graham completo.

- **Jogo infinito que o autor joga (e que guia o que escreve)**: {{GAME}}
- **Elefante da escrita (o que dispara um post, o que irrita a ponto de publicar)**: {{ELEPHANT}}
- **Strength → shadow na escrita (como a força vira fraqueza sob pressão)**: {{STRENGTH_SHADOW}}

---

## Changelog

Registra mudanças de posição ao longo do tempo. Cada entrada: data, tema, mudança em uma linha, gatilho.

- {{DATE}}: {{TOPIC}} — {{CHANGE}} (gatilho: {{TRIGGER}})
