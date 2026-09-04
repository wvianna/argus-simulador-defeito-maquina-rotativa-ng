# HANDOFF.md — Transferência de contexto entre agentes

_Registrado em: 2026-09-04 (atualizado após implementação do MVP)._

## Contexto

O usuário pediu a criação da especificação (`SPECIFICATION.md`) a partir de `docs/descricao.txt`, depois os documentos de design/tasks para implementação por agentes de IA e, por fim, a implementação completa ("implemente"). O usuário não estava disponível para responder às perguntas bloqueadoras e autorizou explicitamente o agente a "trabalhar de forma autônoma e tomar boas decisões".

## Estado atual

- Planejamento SDD completo (`SPECIFICATION.md`, constituição, roadmap, codebase docs, `design.md`, `tasks.md`, `context.md`) e artefatos obrigatórios (`README.md`, `AGENTS.md`, `STATUS.md`, `LICENSE`, `.gitignore`).
- **Implementação do MVP concluída**: back-end (FastAPI + domínio + persistência + API), front-end (React/Vite/TS + Recharts), Docker Compose com 3 serviços.
- Gates aprovados: back-end 48 testes `PASS` (lint/mypy limpos); front-end 9 testes `PASS` (tsc/oxlint limpos); migração aplicada em Postgres 16.
- Pendência de validação em andamento: teste de ponta a ponta via `docker compose up`.

## Alterações realizadas nesta sessão

- Fase de planejamento: `SPECIFICATION.md`, `LICENSE`, `.gitignore`, `README.md`, `AGENTS.md`, `STATUS.md`, `HANDOFF.md`, `.specs/**` (project, codebase, feature).
- Fase de implementação: `backend/` (Dockerfile, alembic, `app/` — domain, persistence, api, observability, config, main; `tests/` unit/integration/contract), `frontend/` (Dockerfile, nginx.conf, Vite, componentes e testes), `docker-compose.yml`, `.env.example`.

## Decisões tomadas (sem confirmação humana ainda)

Todas registradas com justificativa em `.specs/features/simulador-vibracao/context.md`:

1. Back-end: Python 3.12 + FastAPI.
2. Front-end: React 18 + Vite + TypeScript + Recharts.
3. Banco de dados: PostgreSQL 16.
4. Persistência do "trash": física, em tabela separada.
5. Autenticação: nenhuma nesta fase (uso local/interno); CORS restrito a `localhost:5173`.
6. Tolerâncias do Paralelepípedo de Descarte e desvio de rotação: configuráveis via variáveis de ambiente, sem valor fixo no código.
7. Ambiente-alvo inicial: local via Docker Compose, sem CI nem staging/produção definidos.

## Problemas

- Nenhum bug conhecido. Riscos residuais:
  - Decisões acima pendentes de revisão humana (impactam `SPECIFICATION.md`, `STACK.md`, `constitution.md` se mudarem).
  - Deprecation warning de `testcontainers.postgres` (cosmético; migrar para `testcontainers.community` quando conveniente).
  - Sem CI configurado — o gate é executado manualmente (`LOCAL`).

## Testes

- Back-end: `ruff check` (limpo), `mypy app` (limpo), `python -m pytest` → 48 passed.
- Front-end: `npx tsc -b`, `npx oxlint` (limpos), `npx vitest run` → 9 passed.
- Migração `alembic upgrade head` → sucesso (8 tabelas).
- Evidências detalhadas por tarefa na tabela do topo de `.specs/features/simulador-vibracao/tasks.md`.

## Pendências

- Concluir teste de ponta a ponta via `docker compose up` (health + criar Planta/Área/Máquina/Ponto + simulação + snapshot) — o schema não possui endpoint para criar a hierarquia, então no teste E2E a criação deve ser feita via SQL/psql no contêiner do banco ou script de seed.
- Confirmar (ou revisar) as decisões técnicas com o responsável pelo projeto.
- Configurar CI (`A CONFIRMAR`).
- Decidir autenticação (`NFR-006`) antes de exposição fora do ambiente local.

## Próximo passo

Rodar `docker compose up --build`, aguardar health, popular a hierarquia mínima via psql e validar uma chamada real a `POST /simulacoes` e `POST /snapshots` pelo proxy do nginx (`http://localhost:5173/api/...`).

## Cuidados

- Não alterar o algoritmo de descarte (regra de ouro + Paralelepípedo `R^3`) sem atualizar `SPECIFICATION.md` (`FR-007`–`FR-010`) e `design.md` na mesma tarefa.
- Não fazer commit automaticamente.
- Manter a documentação atualizada a cada mudança (Princípio 11 da skill `sdd-software`).
- Comandos de teste usam o venv local (`backend/.venv`) — não confundir com o ambiente do contêiner.

## Critério de conclusão

Este handoff é considerado resolvido quando o teste de ponta a ponta em Docker Compose for concluído com sucesso e as decisões técnicas autônomas forem confirmadas (ou revisadas) pelo responsável pelo projeto.
