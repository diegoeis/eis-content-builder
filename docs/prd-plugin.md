# Plugin Requirements Document

Esse arquivo descreve o objetivo, e os principais pontos e responsabilidades das skills e instruções que formam esse plugin.

## Objetivo

Muitos usuários têm dificuldade em criar conteúdo consistente e de qualidade utilizando IA. Este plugin visa ajudar qualquer pessoa a criar conteúdo consistente e de qualidade, com o seu tom, estilo e estrutura, através de um conjunto de skills que permitem a criação de conteúdo de forma automática e personalizada.

Logo, esse plugin é um assistente pessoal de escrita que aprende a sua voz e produz conteúdo "indistinguível do seu" em múltiplos canais (blog, redes sociais, newsletter, etc.).

A arquitetura central é um workspace para escritores: uma pasta no disco do usuário (pasta dedicada, vault do Obsidian, pasta de artigos e escritos, qualquer lugar) que contém:

- CLAUDE.md (contrato operacional + hierarquia de voz)
- references/ (7 arquivos: voice-fingerprint, author-profile, style-rules, style-examples, content-structures, save-preferences, opinion-map)
- sample-sources/ (amostras originais do autor)
- drafts/ (peças escritas pelo plugin para validação e manipulação do usuário)

Toda skill lê e escreve nesse workspace. A configuração mutável (canais, fontes de pesquisa, arquivo histórico, idioma preferido, ideação) vive separadamente em `$HOME/.claude/eis-content-builder.local.md`.

O arquivo `eis-content-builder.local.md` é o arquivo de configuração utilizado pelo plugin e deve ser encontrável caso o usuário não estiver indicado o workspace explicitamente. Ele é criado pelo skill `writer-setup`.

## writer-setup

O `/writer-setup` é uma skill que permite ao usuário configurar o seu workspace, com todas as informações necessárias para agentes entenderem qual o estilo, tom e estrutura preferenciais definidas pelo usuário. É o único ponto de entrada que cria ou reestrutura o workspace. Nenhuma outra skill faz isso. 

Responsabilidades concretas:

**Coleta identidade do autor**: faz um profile do usuário, em rounds curtos, usado `AskUserQueston` quando escolhas forem necessárias; e texto livre para outras informações.

Informações importantes para inferir informações com mais precisão:

- Pergunta URL do Linkedin: consegue pegar nome, cargo, empresas, indústrias, especialidades e outros links de redes sociais, público, blogs/newsletters. Aqui é importante utilizar o browser tool para acessar e extrair as informações, evitando o bloqueio que esses sites podem ter;
- Pergunta URL do blog e Newsletter: se não conseguiu pegar do Linkedin, perguntar diretamente. E daí, tenta descobrir informações faltantes como links das redes sociais;
- Pergunta links de Redes Sociais: se não conseguiu pegar dos passos anteriores, pergunta diretamente e tenta descobrir informações faltantes e já consegue pegar uma lista das últimas 10 publicações;
- Pergunta se tem livros publicados e os links dos livros: se não conseguiu pegar nos passos anteriores, perguntar diretamente;

**Referências e exemplos do usuário**: aqui, o usuário deve trazer exemplos de escrita, para que posteriormente o agente possa entender o estilo e o tom do usuário.

Aqui, devemos reunir a partir dos inputs dos usuários (e os dados coletados nos passos anteriores):

- Artigos e conteúdos online a partir dos blogs, newsletters, livros, artigos, etc.
- Pasta onde são guardados os artigos, conteúdos escritos salvos localmente: pode ser uma pasta local. E aqui, o plugin deve ler alguns dos arquivos para entender a estrutura de organização e relacionamento. O plugin deve identificar se a pasta é do Obsidian. E se for, utilizar o Obsidian CLI para facilitar o acesso e conteudo dos arquivos. Se não for obsidian, utilizar comandos bash/grep etc para entender os padrões. Não leia todos os arquivos, veja o que pode ser inferido a partir das extrações de conteúdo de poucos arquivos.
  - O usuário entregar um link de pasta de serviços como o Drive, Dropbox, nesse caso, o Plugin deve tentar ver se há algum MCP ou integração instalada no LLM dele, e usá-lo para facilitar sem gastar muitos tokens.

Como o plugin também faz criação de conteúdo, devemos perguntar para o usuários, quais autores, sites e fontes de referência que ele gostaria que fossem utilizadas para fazer pesquisas e inspirações.

**Tom, estilo e estruturas de linguagem**: com as informações adquiridas com o passo anterior, tenta inferir o estilo de escrita, tom e linguagem preferida pelo autor.

Importante não fazer pesquisas muito superficiais ou muito profundas. Não queremos que o agente fique perdido em uma busca infinita e que gaste tokens sem necessidade. Lembre-se que o usuário pode enriquecer o contexto posteriormente fazendo calibração.



- **Descobrir contexto** — localiza o config file numa busca em cascata ($ENV → cwd → walk-up → $HOME), decide entre três branches: primeira vez, update, ou repair.
- **Guard contra paths efêmeros** — recusa explicitamente /sessions/, /tmp/, /var/folders/, worktrees etc. O workspace tem que viver em storage durável.
- **Coletar identidade do autor** em rounds curtos: identity → channels → language/preferences → article archive (opcional) → samples.
- **Auto-detectar Obsidian** no archive (sem perguntar) via walk-up procurando .obsidian/.
- **Inferir schema do archive** — amostra 3–5 arquivos, mapeia roles conhecidos (title, tags, status, date, url, excerpt), deixa null o que não existe (nunca inventa).
- **Escrever o config canônico** em $HOME/.claude/ + symlink dentro do workspace.
- **Materializar o workspace** — copia CLAUDE.md do template, cria diretórios, escreve os 7 reference files a partir dos templates.
- **Orquestrar dois agents** — voice-analyzer (gera voice-fingerprint + style-examples) e opinion-extractor em modo bulk (popula opinion-map).
- **Suportar três modos** — 2A first-time, 2B update (intent-routed, sem menu se não for ambíguo), 2C repair.
- **Versionamento** — bumpa version: no .local.md no fim.

É aqui que garantimos que o conteúdo será consistente, respeitando as preferências de padrões de escrita de cada pessoa.
O `/writer-setup` deve ser a primeira coisa a ser executada pelo usuário, antes de qualquer outra skill do plugin. 

Logo, quando o workspace tiver sido construído, a LLM poderá utilizar as informações coletadas.
