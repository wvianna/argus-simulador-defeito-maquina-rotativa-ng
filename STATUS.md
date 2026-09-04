# STATUS.md — Estado atual do desenvolvimento

_Última atualização: 2026-09-04._

## Concluído

### Planejamento (SDD)

- `SPECIFICATION.md` — especificação funcional e técnica do sistema (18 `FR-###`, 7 `NFR-###`, 12 critérios de aceitação, matriz de rastreabilidade).
- `.specs/project/constitution.md` — princípios obrigatórios do projeto.
- `.specs/project/ROADMAP.md` — fases de implementação do MVP.
- `.specs/codebase/STACK.md`, `ARCHITECTURE.md`, `CONVENTIONS.md`, `TESTING.md` — documentação de codebase.
- `.specs/features/simulador-vibracao/design.md`, `tasks.md`, `context.md`.
- `README.md`, `AGENTS.md`, `LICENSE` (Apache 2.0), `.gitignore`, `.env.example`.

### Implementação do MVP (T-001 a T-011)

**Back-end (Python 3.12 + FastAPI, em `backend/`):**
- Módulos de domínio: `signal_generator.py`, `fft_processor.py`, `discard_engine.py` (regra de ouro + Paralelepípedo de Descarte `R^3`), `observability/logging.py`.
- Persistência: modelos SQLAlchemy (Planta/Área/Máquina/Ponto, `leituras_persistidas`, `leituras_trash`, `snapshots_defeito`), repositório com transação e lock de linha, Alembic com migração inicial.
- API: `POST /simulacoes` (validação Pydantic + Nyquist, orquestra geração → FFT → descarte → persistência), `POST /snapshots`, `GET /health`. CORS para o front de desenvolvimento (uso local, `NFR-006`).
- Resposta da simulação inclui `sinal_tempo` decimado (painel, `FR-014`), picos `R^3`, RMS, valor DC, decisão de descarte, tempo de processamento e taxa de descarte acumulada.

**Front-end (React 18 + Vite + TypeScript, em `frontend/`):**
- Componentes: `PainelSimulacao`, `PainelSinal`, `GraficoFFT` (Recharts), `IndicadoresSimulacao`, `ChecklistValidacao`, `SnapshotDefeito`.
- Client HTTP tipado com prefixo `/api` (proxy do Vite em dev; nginx em Docker).
- Validação no cliente espelhando Nyquist (`NFR-001`) e bloqueando submissão inválida (`FR-018`).

**Infraestrutura:**
- `docker-compose.yml` (serviços `db`, `backend`, `frontend`), `backend/Dockerfile` (roda `alembic upgrade head` no start), `frontend/Dockerfile` (build + nginx com proxy `/api`).

## Em andamento

- Teste de ponta a ponta em Docker Compose (validação final da sessão atual).

## Pendente

- Configuração de CI (`A CONFIRMAR`).
- Revisão humana das decisões técnicas tomadas autonomamente (stack, persistência do trash, ausência de autenticação, tolerâncias configuráveis) — ver `.specs/features/simulador-vibracao/context.md`.
- Decisão definitiva sobre autenticação (`NFR-006`) antes de qualquer exposição além do ambiente local.
- Calibração dos valores de tolerância do descarte e desvio de rotação (configuráveis via ambiente).

## Problemas e erros conhecidos

- Nenhum bug conhecido. O deprecation warning de `testcontainers.postgres` (migrar para `testcontainers.community`) é cosmético.

## Testes realizados

- Back-end: `ruff check` (limpo), `mypy app` (limpo), `pytest` → **48 passed** (unit + integração + contrato). Nível: `LOCAL`.
- Front-end: `tsc -b` (limpo), `oxlint` (limpo), `vitest run` → **9 passed**. Nível: `LOCAL`.
- Migração `alembic upgrade head` executada com sucesso em PostgreSQL 16 (8 tabelas).

## Última alteração relevante

Implementação completa do MVP do simulador (domínio, persistência, API, front-end e Docker Compose), com gate de lint/type-check/testes aprovado em ambas as camadas.

## Próximo passo recomendado

1. Concluir o teste de ponta a ponta via `docker compose up` (health + simulação real + snapshot).
2. Revisar com o responsável as decisões técnicas autônomas listadas em `context.md`.
3. Definir CI (`A CONFIRMAR`) para rodar os gates automaticamente.
