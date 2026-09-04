# AGENTS.md — Regras permanentes do projeto

Leia este arquivo antes de alterar qualquer código ou documento deste repositório. Ele complementa, sem substituir, a skill `sdd-software` (`.agents/skills/sdd-software/SKILL.md`) e a constituição do projeto (`.specs/project/constitution.md`).

## Ordem de leitura recomendada

1. `STATUS.md` — estado atual, pendências e próximo passo.
2. `HANDOFF.md` — contexto deixado pelo agente anterior, se houver.
3. `SPECIFICATION.md` — requisitos e critérios de aceitação (`FR-###` / `NFR-###`).
4. `.specs/project/constitution.md` — princípios obrigatórios do projeto.
5. `.specs/codebase/STACK.md`, `ARCHITECTURE.md`, `CONVENTIONS.md`, `TESTING.md`.
6. `.specs/features/simulador-vibracao/design.md` e `tasks.md` — design e tarefas do MVP em execução.

## Arquitetura e stack obrigatórios

- Back-end: Python 3.12 + FastAPI. Geração de sinal e FFT com NumPy/SciPy. Persistência via SQLAlchemy + Alembic.
- Front-end: React 18 + Vite + TypeScript. Gráficos com Recharts.
- Banco de dados: PostgreSQL 16.
- Execução local: Docker Compose. Não introduza outra stack sem atualizar `.specs/codebase/STACK.md` e `context.md` com a justificativa.

> Estas escolhas foram feitas de forma autônoma (usuário indisponível para decidir) e estão registradas com justificativa em `.specs/features/simulador-vibracao/context.md`. Revise-as com o responsável pelo projeto antes de considerá-las definitivas.

## Convenções de código

Ver `.specs/codebase/CONVENTIONS.md` para o detalhamento completo (estilo, lint, nomenclatura, commits). Resumo:

- Back-end: `ruff` + `black` + `mypy`; nomes de módulos em `snake_case`.
- Front-end: `eslint` + `prettier`; componentes em `PascalCase`.
- Toda função pública relevante deve referenciar o(s) ID(s) de requisito (`FR-###`/`NFR-###`) que implementa, em teste ou comentário curto, para rastreabilidade.

## Comandos importantes

Ver `.specs/codebase/STACK.md` e `.specs/codebase/TESTING.md` para os comandos completos de build, lint, migração e teste. Nenhum comando foi validado em execução real ainda — confirme antes de reportar sucesso.

## Restrições

- Não introduza autenticação, criptografia ou qualquer novo requisito de segurança sem atualizar `SPECIFICATION.md` (`NFR-006`) e `.specs/project/constitution.md`.
- Não altere o algoritmo de descarte (regra de ouro + Paralelepípedo de Descarte) sem atualizar `FR-007`–`FR-010` em `SPECIFICATION.md` e o `design.md` correspondente.
- Não faça commit automaticamente. Se o usuário pedir commits, mantenha commits atômicos por tarefa (`T-###`).
- Não crie uma segunda fonte de documentação concorrente ao `README.md`; atualize-o em vez de duplicar conteúdo.

## Procedimento de teste

- Gate mínimo por tarefa: lint + type-check + testes unitários do módulo afetado.
- Antes de declarar uma funcionalidade concluída, execute o nível de teste definido na tarefa correspondente em `tasks.md` e registre `PASS`/`FAIL`/`PENDENTE` com a evidência (comando executado e resultado).
- Nunca declare validação de produção a partir de teste apenas local — não há ambiente de produção definido neste projeto (`NFR-005` em aberto).

## Critério para alteração de arquivos

- Qualquer mudança de comportamento observável exige atualização de `SPECIFICATION.md` e, se aplicável, de `design.md`/`tasks.md`.
- Toda tarefa concluída deve atualizar `STATUS.md` e, se houver continuidade pendente, `HANDOFF.md`.
