# STATUS.md — Estado atual do desenvolvimento

_Última atualização: 2026-09-04._

## Concluído

- `SPECIFICATION.md` — especificação funcional e técnica do sistema (18 `FR-###`, 7 `NFR-###`, 12 critérios de aceitação, matriz de rastreabilidade).
- `.specs/project/constitution.md` — princípios obrigatórios do projeto, com stack e decisões técnicas confirmadas.
- `.specs/project/ROADMAP.md` — fases de implementação do MVP.
- `.specs/codebase/STACK.md`, `ARCHITECTURE.md`, `CONVENTIONS.md`, `TESTING.md` — documentação de codebase.
- `.specs/features/simulador-vibracao/design.md` — design técnico do MVP (módulos, contratos, schema, concorrência, segurança, observabilidade).
- `.specs/features/simulador-vibracao/tasks.md` — quebra em tarefas `T-###` ordenadas por risco.
- `.specs/features/simulador-vibracao/context.md` — decisões técnicas tomadas autonomamente (usuário indisponível) e pendentes de revisão.
- `README.md`, `AGENTS.md`, `LICENSE` (Apache 2.0), `.gitignore`.

## Em andamento

- Nenhum código de aplicação foi implementado ainda. Este é o estado imediatamente anterior ao início da Fase 1 do roadmap (`T-001` em `tasks.md`).

## Pendente

- Implementação de todas as tarefas `T-001`–`T-0NN` listadas em `.specs/features/simulador-vibracao/tasks.md`.
- Criação dos diretórios `backend/` e `frontend/` e do `docker-compose.yml` referenciados no `README.md`.
- Configuração de CI (não definida — ver pergunta bloqueadora em `SPECIFICATION.md`).
- Confirmação humana das decisões técnicas tomadas autonomamente (ver `.specs/features/simulador-vibracao/context.md`): stack Python/FastAPI + React/Vite + PostgreSQL, persistência física do "trash", ausência de autenticação nesta fase, tolerâncias configuráveis, ambiente local via Docker Compose.

## Problemas e erros conhecidos

- Nenhum (não há código executável ainda).

## Testes realizados e pendentes

- Nenhum teste foi executado; nenhum ambiente `LOCAL`, `CI`, `STAGING` ou `PRODUÇÃO` foi validado.
- Gate mínimo a aplicar a partir de `T-001`: lint + type-check + testes unitários por tarefa (ver `.specs/codebase/TESTING.md`).

## Última alteração relevante

Criação do conjunto completo de artefatos de planejamento SDD (constituição, roadmap, stack, arquitetura, convenções, testes, design e tarefas) para viabilizar implementação por agentes de IA a partir de `SPECIFICATION.md`.

## Próximo passo recomendado

Iniciar `T-001` em `.specs/features/simulador-vibracao/tasks.md` (schema de banco de dados e migrações), respeitando a ordem de dependências das tarefas seguintes.
