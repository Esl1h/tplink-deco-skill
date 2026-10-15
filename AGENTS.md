# Guia para agentes

Este arquivo explica como alterar esta skill sem quebrá-la.

## O que este repositório contém

Uma skill de agente que controla um mesh TP-Link Deco pela API web local do roteador, via pacote Python `tplink-deco-api`, com um CLI fino que imprime JSON.

- `SKILL.md` é a fonte da verdade da skill.
- `scripts/deco.py` é o CLI (Python 3.14+, `pip install tplink-deco-api`).
- `tests/test_deco.py` cobre o plumbing do CLI, sem roteador.
- `README.md` documenta instalação, configuração e desenvolvimento.

Não há etapa de build.

## Regras para mudanças

- Mantenha a skill em inglês e portável entre agentes. Não escreva instruções que limitem a uma ou duas ferramentas de agente específicas.
- Credenciais só por variáveis de ambiente (`DECO_HOST`, `DECO_USER`, `DECO_PASSWORD`). Nunca coloque senhas em código, exemplos ou logs.
- A skill lê por padrão. Ações que mudam estado (`block`, `unblock`, `rename`, `forget`, `reserve`, `unreserve`) exigem confirmação do usuário; mantenha essa regra no `SKILL.md`.
- Mantenha o import do `tplink_deco_api` tardio, dentro de `load_sdk`: os testes de plumbing rodam sem o pacote instalado e o `--help` não pode exigir instalação.
- Não faça polling em loop no CLI; a API do roteador é sensível a excesso de chamadas.

## Verificações

Antes de publicar, rode os testes:

```sh
python3 -m unittest discover -s tests
```

Sem o `tplink-deco-api` instalado, o teste que precisa dele pula sozinho. Nenhum roteador é necessário.

## Estilo de escrita

Linguagem simples e direta: voz ativa, frases curtas, um único termo para a mesma coisa. Identificadores, comandos, saídas de API e mensagens de erro ficam exatamente como são. Em português, acentuação e crase corretas.
