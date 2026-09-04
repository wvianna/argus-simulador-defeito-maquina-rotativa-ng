# HANDOFF.md — Transferência de contexto entre agentes

_Registrado em: 2026-09-04 (atualizado ao final da sessão de UI/UX, testes E2E e documentação)._

## Contexto

Sessões conduzidas de forma autônoma sob a skill `sdd-software`: especificação (`SPECIFICATION.md`) → design/tasks → implementação completa do MVP → iterações de UI/UX (tema industrial dark, layout de página única, tooltips de ajuda) → refatoração do catálogo de defeitos segundo `docs/assinaturas_fft_falhas_maquinas_rotativas_IA.md` → scripts `start.sh`/`stop.sh` → README com diagramas Mermaid e capturas de tela. O usuário esteve indisponível para as perguntas bloqueadoras e autorizou o agente a "trabalhar de forma autônoma e tomar boas decisões".

## Estado atual

- Planejamento SDD completo (`SPECIFICATION.md` com 19 FR/7 NFR/14 CA e catálogo de 13 defeitos, constituição, roadmap, codebase docs, `design.md`, `tasks.md` T-001 a T-013, `context.md`) e artefatos obrigatórios (`README.md`, `AGENTS.md`, `STATUS.md`, `LICENSE`, `.gitignore`, `.env.example`).
- **Implementação do MVP concluída e validada de ponta a ponta**: back-end (FastAPI + domínio + persistência + API), front-end (React/Vite/TS + Recharts, tema industrial dark em página única), Docker Compose com 3 serviços (`db`, `backend`, `frontend`).
- Catálogo de defeitos com 13 tipos e assinaturas espectrais por ordem/rotação (harmônicos, sub-harmônicos, `oil_whirl` 0,39–0,48X, BPFO/BPFI/BSF/FTF com sidebands).
- Front-end com tooltips `Help` em todos os controles/painéis, limiar de ruído configurável (`limiar_picos`, `FR-019`), FFT com ordens `N` + rotação em Hz (`FR-015`), barras de 5 px e default de UUID de ponto.
- Gates aprovados: back-end 63 testes `PASS` (ruff/mypy limpos); front-end 12 testes `PASS` (tsc/oxlint limpos); migração aplicada em Postgres 16 (8 tabelas).
- E2E concluído no navegador (`http://localhost:5173`): formulário, sinal, FFT, telemetria e snapshot; assinaturas verificadas via API (1X, 2X/4X/6X, 0,42X, BPFI+sidebands).
- `start.sh`/`stop.sh` operacionais (setup + health-check + seed do Ponto demo).
- `README.md` com arquitetura Mermaid e seção "Capturas de tela (dashboard)" referenciando `docs/imagens/` (7 imagens).

## Alterações realizadas nesta(s) sessão(ões)

- Planejamento: `SPECIFICATION.md` (evoluída para 19 FR/14 CA/catálogo de 13 defeitos), `LICENSE`, `.gitignore`, `README.md`, `AGENTS.md`, `STATUS.md`, `HANDOFF.md`, `.specs/**` (project, codebase, feature).
- Back-end: catálogo de defeitos refatorado em `signal_generator.py`; suporte a `limiar_picos`/`limiar_amplitude` na FFT, schemas e `POST /simulacoes`; testes expandidos (48 → 63).
- Front-end: redesign industrial dark + layout de página única (~844 px); novo `Help.tsx`; `GraficoFFT` com barras de 5 px, rótulos Hz + ordem `N`, linha de limiar e rotação em Hz; slider de limiar; default de UUID; endurecimento de mensagens de erro; testes (9 → 12).
- Infra/docs: `start.sh`, `stop.sh`; README com diagramas Mermaid + seção de capturas; capturas de tela em `docs/imagens/`.
- E2E no navegador com validação visual e de assinaturas via API.

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

- Sem bugs conhecidos. Riscos residuais:
  - Decisões acima pendentes de revisão humana (impactam `SPECIFICATION.md`, `STACK.md`, `constitution.md` se mudarem).
  - Deprecation warning de `testcontainers.postgres` (cosmético; migrar para `testcontainers.community` quando conveniente).
  - Sem CI configurado — o gate é executado manualmente (`LOCAL`).
  - Artefato menor de a11y: `Help` dentro de `<label>` adiciona o sufixo "Ajuda" ao nome acessível dos campos (testes seguem passando).
  - Frequências de rolamento usam geometria padrão do rolamento; geometria real ainda não exposta na UI.

## Testes

- Back-end: `ruff check` (limpo), `mypy app` (limpo), `python -m pytest` → 63 passed.
- Front-end: `npx tsc -b`, `npx oxlint` (limpos), `npx vitest run` → 12 passed.
- Migração `alembic upgrade head` → sucesso (8 tabelas).
- E2E navegador: OK (formulário + resultado completo; assinaturas 1X/2X/4X/6X, 0,42X, BPFI+sidebands).
- Evidências detalhadas por tarefa na tabela do topo de `.specs/features/simulador-vibracao/tasks.md`.

## Pendências

- Revisão humana das decisões técnicas de `context.md` (stack, trash físico, ausência de autenticação, tolerâncias configuráveis).
- Configurar CI (`A CONFIRMAR`) para rodar os gates (ruff/mypy/pytest + tsc/oxlint/vitest) automaticamente.
- Decidir autenticação (`NFR-006`) e volume/meta de performance (`NFR-005`) antes de exposição fora do ambiente local.
- Calibrar tolerâncias de descarte e desvio de rotação.
- Sugestões futuras (não solicitadas): teste Playwright E2E versionado; geometria de rolamento configurável na UI; workflow de CI.

## Próximo passo

1. Revisar com o responsável as decisões técnicas autônomas de `context.md`.
2. Configurar CI para os gates.
3. Avançar a Fase 5 do roadmap (observabilidade/hardening) quando o ambiente-alvo for definido.

## Cuidados

- Não alterar o algoritmo de descarte (regra de ouro + Paralelepípedo `R^3`) sem atualizar `SPECIFICATION.md` (`FR-007`–`FR-010`) e `design.md` na mesma tarefa.
- Não alterar o catálogo de defeitos/assinaturas espectrais sem atualizar `SPECIFICATION.md` (seção "Catálogo de tipos de defeito") e os testes correspondentes.
- Não fazer commit automaticamente.
- Manter a documentação atualizada a cada mudança (Princípio 11 da skill `sdd-software`).
- Comandos de teste usam o venv local (`backend/.venv`) — não confundir com o ambiente do contêiner.
- O repositório efetivo está em `/home/william/git/argus-simulador-defeito-maquina-rotativa-ng`.

## Critério de conclusão

Este handoff é considerado resolvido quando as decisões técnicas autônomas forem confirmadas (ou revisadas) pelo responsável pelo projeto e a CI for definida (`A CONFIRMAR`).
