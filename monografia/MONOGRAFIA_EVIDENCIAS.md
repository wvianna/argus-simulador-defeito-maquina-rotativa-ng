# MONOGRAFIA — EVIDÊNCIAS

Matriz: `Afirmação | Evidência | Arquivo/Fonte | Seção na monografia`

| Afirmação | Evidência | Arquivo/Fonte | Seção |
|---|---|---|---|
| Critério R³ e regra de ouro definem a persistência seletiva | Texto-fonte descreve hierarquia de decisão (rotação → nº picos → R³) e "regra de ouro" | `docs/criterioArmazenamento.txt`, `docs/descricao.txt` | 2 e 5 |
| Unidades e convenções por zona (deslocamento/velocidade/aceleração) seguem ISO 10816 | Tabelas de convenções nos documentos de origem | `docs/descricao.txt`, `docs/criterioDetermincacaoAnamalia.txt` | 2 |
| Nyquist exige amostragem > 2× Fmax; janelas Hanning/FlatTop/Rectangular | Diretrizes metrológicas nos documentos de origem | `docs/descricao.txt`, `docs/criterioDetermincacaoAnamalia.txt` | 2 e 5 |
| Catálogo de defeitos com 13 tipos e assinaturas espectrais | Tabela em SPEC + `DEFECT_PROFILES` em `signal_generator.py` | `SPECIFICATION.md`, `backend/app/domain/signal_generator.py` | 2, 5, 6 |
| Frequências sempre derivadas de fr=RPM/60 (ordens) | Implementação e doc de assinaturas | `backend/app/domain/signal_generator.py`, `docs/assinaturas_fft_falhas_maquinas_rotativas_IA.md` | 2, 5 |
| Arquitetura em camadas (front/back/db) com fluxo simulação→FFT→descarte→persistência | Diagramas e tabelas de módulos | `.specs/codebase/ARCHITECTURE.md` | 5 |
| Back-end passa lint, mypy e 63 testes | Saída real de `ruff check`, `mypy`, `pytest` (63 passed) | `backend/tests/`; execução documentada em `STATUS.md` | 6 |
| Front-end passa tsc, oxlint e 12 testes | Saída real de `tsc -b`, `oxlint`, `vitest run` (12 passed) | `frontend/src/`, `frontend/src/**/*.test.*`; `STATUS.md` | 6 |
| Migração aplicada em PostgreSQL 16 (8 tabelas) | `alembic upgrade head` executado | `backend/alembic/`, `STATUS.md` | 5, 6 |
| Assinaturas observadas via API (1X, 2X/4X/6X, oil_whirl 0,42X, rolamento BPFI + sidebands) | Verificações via curl registradas na sessão E2E | `STATUS.md`, `HANDOFF.md`; execução via `POST /simulacoes` | 6 |
| Dashboard renderiza formulário, sinal, FFT com ordens N + rotação em Hz, telemetria e snapshot | Capturas de tela reais | `docs/image/*.png` (copiadas para `monografia/figures/`) | 6 |
| API expõe `POST /simulacoes`, `POST /snapshots`, `GET /health` | Implementação e testes de contrato | `backend/app/api/*`, `backend/tests/contract/` | 5 |
| Persistência usa JSONB (arquitetura não normalizada, NFR-003) | Schema e ADR-001 | `.specs/codebase/ARCHITECTURE.md`, `backend/alembic/` | 2, 5 |

## Evidências de execução (resultados reais capturados)

- Back-end: `pytest -q` → **63 passed** (unit + integração + contrato); `ruff check` limpo; `mypy` limpo.
- Front-end: `vitest run` → **12 passed** (5 arquivos); `tsc -b` limpo; `oxlint` limpo.
- Migração: 8 tabelas criadas em PostgreSQL 16.
- E2E (navegador `http://localhost:5173`): simulação de `rolamento_bpfi` apresentou picos em ordens compatíveis com BPFI + sidebands, RMS do sinal, telemetria e snapshot.

## Fontes não usadas como evidência direta (validação humana pendente)

- Normas ABNT e ISO citadas (verificar edição vigente).
- Referências bibliográficas externas (verificar metadados).
