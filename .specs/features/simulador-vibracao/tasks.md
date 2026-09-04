# tasks.md — Simulador de Vibração (MVP)

> Tarefas ordenadas por risco e dependência: contrato/schema → lógica pura → persistência → API → front-end → observabilidade. Cada tarefa deve ser pequena o bastante para revisão isolada (Princípio da constituição, seção 7). Estados: `[ ]` pendente, `[-]` em andamento, `[x]` concluída, `[!]` bloqueada.

- [x] T-001 Bootstrap do back-end e schema de banco de dados
- [x] T-002 Módulo `signal_generator`
- [x] T-003 Módulo `fft_processor`
- [x] T-004 Módulo `discard_engine` (regra de ouro + Paralelepípedo de Descarte)
- [x] T-005 Camada `persistence` (leituras, trash, hierarquia)
- [x] T-006 Endpoint `POST /simulacoes`
- [x] T-007 Endpoint `POST /snapshots`
- [x] T-008 Bootstrap do front-end e checklist de validação
- [x] T-009 Painel visual (sinal + RMS) e gráfico de FFT
- [x] T-010 Ação de snapshot de defeito + indicadores de tempo/taxa de descarte no front-end
- [x] T-011 Observabilidade (logs estruturados + métrica de taxa de descarte)

> **Status de implementação (2026-09-04):** todas as tarefas do MVP foram implementadas e o gate mínimo foi executado com sucesso (`PASS`). Evidência por camada abaixo.

| Tarefa | Gate executado | Resultado |
|---|---|---|
| T-001 | `alembic upgrade head` em Postgres 16 + `tests/integration/test_schema.py` | PASS (8 tabelas criadas) |
| T-002 | `pytest tests/unit/test_signal_generator.py` | PASS |
| T-003 | `pytest tests/unit/test_fft_processor.py` | PASS |
| T-004 | `pytest tests/unit/test_discard_engine.py` | PASS (casos obrigatórios de TESTING.md cobertos) |
| T-005 | `pytest tests/integration/test_persistence.py` | PASS |
| T-006 | `pytest tests/contract/test_simulacoes_api.py` | PASS |
| T-007 | `pytest tests/contract/test_snapshots_api.py` | PASS |
| T-008 | `npx tsc -b && npx oxlint && npx vitest run` (ChecklistValidacao) | PASS |
| T-009 | Vitest (PainelSinal, GraficoFFT) | PASS |
| T-010 | Vitest (SnapshotDefeito, IndicadoresSimulacao) | PASS |
| T-011 | `pytest tests/unit/test_observability.py` | PASS |

- Suíte completa de back-end: `ruff check` + `mypy` + `pytest` → **48 passed**.
- Suíte completa de front-end: `tsc -b` + `oxlint` + `vitest run` → **9 passed**.
- Nível de evidência: `LOCAL` (CI não configurado — `A CONFIRMAR`).

---

```text
Tarefa: T-001 Bootstrap do back-end e schema de banco de dados
Requisitos: FR-011, FR-013, NFR-007
Onde: backend/ (novo projeto), backend/alembic/
Depende de: nenhuma
Reutiliza: nenhum (projeto greenfield)
Feito quando: `docker compose up` sobe backend + PostgreSQL; migração cria plantas, areas, maquinas, pontos, leituras_persistidas, leituras_trash, snapshots_defeito com FKs corretas.
Testes: integração (testcontainers) validando criação do schema e inserção de um registro por tabela
Gate: lint + type-check + `pytest tests/integration/test_schema.py`
```

```text
Tarefa: T-002 Módulo signal_generator
Requisitos: FR-001, FR-002, FR-003
Onde: backend/app/domain/signal_generator.py
Depende de: T-001 (apenas para estrutura de projeto; lógica é pura, sem I/O)
Reutiliza: NumPy/SciPy
Feito quando: dado RPM, tipo de defeito (catálogo completo), severidade e ruído de fundo, gera sinal no domínio do tempo com assinatura espectral coerente com o defeito (ex.: 1X dominante para desbalanceamento, harmônicos 1X-10X para folga).
Testes: unitário — um caso por tipo de defeito do catálogo, verificando presença da frequência esperada no sinal gerado
Gate: lint + type-check + `pytest tests/unit/test_signal_generator.py`
```

```text
Tarefa: T-003 Módulo fft_processor
Requisitos: FR-004, FR-005, FR-006, NFR-001
Onde: backend/app/domain/fft_processor.py
Depende de: T-002 (usa sinais gerados nos testes)
Reutiliza: scipy.fft
Feito quando: calcula FFT, extrai picos como {frequencia, amplitude, fase}, calcula RMS total/ruído/picos e valor DC; rejeita configuração que viole Nyquist (taxa_amostragem <= 2 * fmax).
Testes: unitário — extração de picos de sinal sintético conhecido; caso de violação de Nyquist retorna erro (CA-011)
Gate: lint + type-check + `pytest tests/unit/test_fft_processor.py`
```

```text
Tarefa: T-004 Módulo discard_engine (regra de ouro + Paralelepípedo de Descarte)
Requisitos: FR-007, FR-008, FR-009, FR-010, FR-011
Onde: backend/app/domain/discard_engine.py
Depende de: T-003 (consome picos_r3 e rotacao produzidos pelo fft_processor)
Reutiliza: nenhum
Feito quando: função pura recebe (leitura_atual, ultima_leitura_persistida | None, tolerancias) e retorna decisão persistir|descartar com motivo; cobre os 4 casos obrigatórios de TESTING.md (primeira leitura, regra de ouro, dentro da tolerância, fora da tolerância).
Testes: unitário — um teste por caso obrigatório listado em .specs/codebase/TESTING.md
Gate: lint + type-check + `pytest tests/unit/test_discard_engine.py` (100% dos casos obrigatórios cobertos)
```

```text
Tarefa: T-005 Camada persistence (leituras, trash, hierarquia)
Requisitos: FR-012, FR-013
Onde: backend/app/persistence/
Depende de: T-001, T-004
Reutiliza: SQLAlchemy models de T-001
Feito quando: grava leitura aprovada em leituras_persistidas (e atualiza pontos.ultima_leitura_persistida_id) ou em leituras_trash, em transação atômica; falha de gravação não altera o ponteiro de última leitura.
Testes: integração (testcontainers) — leitura concorrente do mesmo Ponto não corrompe ultima_leitura_persistida_id; falha simulada não deixa estado parcial
Gate: lint + type-check + `pytest tests/integration/test_persistence.py`
```

```text
Tarefa: T-006 Endpoint POST /simulacoes
Requisitos: FR-014 (contrato), FR-018, NFR-001, NFR-006
Onde: backend/app/api/simulacoes.py
Depende de: T-002, T-003, T-004, T-005
Reutiliza: signal_generator, fft_processor, discard_engine, persistence
Feito quando: endpoint aceita payload de design.md, valida com Pydantic (incluindo Nyquist), orquestra geração → FFT → descarte → persistência, retorna resposta conforme contrato de design.md.
Testes: contrato — httpx.AsyncClient cobrindo CA-001, CA-002, CA-010, CA-011
Gate: lint + type-check + `pytest tests/contract/test_simulacoes_api.py`
```

```text
Tarefa: T-007 Endpoint POST /snapshots
Requisitos: FR-016
Onde: backend/app/api/snapshots.py
Depende de: T-005
Reutiliza: persistence
Feito quando: grava par sensor + anomalia vinculado a uma leitura existente; rejeita leitura_id inexistente (404) e tipo_defeito fora do catálogo (422).
Testes: contrato — httpx.AsyncClient cobrindo CA-009
Gate: lint + type-check + `pytest tests/contract/test_snapshots_api.py`
```

```text
Tarefa: T-008 Bootstrap do front-end e checklist de validação
Requisitos: FR-018
Onde: frontend/ (novo projeto)
Depende de: T-006 (contrato da API precisa existir para tipar o client)
Reutiliza: nenhum (projeto greenfield)
Feito quando: projeto Vite/React sobe via docker compose; componente ChecklistValidacao impede envio da simulação enquanto RPM, tipo de defeito, severidade, ruído de fundo, taxa de amostragem ou número de amostras estiverem ausentes/inválidos (incluindo violação de Nyquist no cliente, espelhando NFR-001).
Testes: unitário (Vitest + RTL) — checklist bloqueia submissão com campos inválidos (CA-010)
Gate: lint + type-check + `npm test -- ChecklistValidacao`
```

```text
Tarefa: T-009 Painel visual (sinal + RMS) e gráfico de FFT
Requisitos: FR-014 (painel), FR-015
Onde: frontend/src/components/PainelSimulacao.tsx, GraficoFFT.tsx
Depende de: T-008
Reutiliza: client de API tipado de T-008
Feito quando: exibe série temporal do sinal do acelerômetro simulado, valor de RMS, e gráfico de barras por frequência com linha horizontal de threshold.
Testes: unitário (Vitest + RTL) — renderização com dados mockados da API (CA-008)
Gate: lint + type-check + `npm test -- PainelSimulacao GraficoFFT`
```

```text
Tarefa: T-010 Ação de snapshot de defeito + indicadores de tempo/taxa de descarte
Requisitos: FR-016, FR-017
Onde: frontend/src/components/SnapshotDefeito.tsx, IndicadoresSimulacao.tsx
Depende de: T-007, T-009
Reutiliza: client de API tipado de T-008
Feito quando: botão de snapshot chama POST /snapshots e confirma sucesso; indicadores exibem tempo_processamento_ms e taxa_descarte_acumulada retornados pela API.
Testes: unitário (Vitest + RTL) — ação de snapshot dispara chamada correta (CA-009); indicadores renderizam valores da resposta (CA-012)
Gate: lint + type-check + `npm test -- SnapshotDefeito IndicadoresSimulacao`
```

```text
Tarefa: T-011 Observabilidade (logs estruturados + métrica de taxa de descarte)
Requisitos: NFR-002, NFR-004
Onde: backend/app/api/simulacoes.py (log por request), backend/app/observability/
Depende de: T-006
Reutiliza: infraestrutura de logging padrão do FastAPI/Uvicorn
Feito quando: cada simulação gera log estruturado (JSON) com ponto_id, parâmetros, decisão de descarte e tempo de processamento; taxa de descarte agregada é calculável (por Ponto e global).
Testes: unitário — formato do log é JSON válido com os campos esperados; cálculo de taxa de descarte testado com dados simulados
Gate: lint + type-check + `pytest tests/unit/test_observability.py`
```

## Entregáveis e aceite

- Arquivos de código: `backend/app/domain/*`, `backend/app/persistence/*`, `backend/app/api/*`, `backend/alembic/*`, `frontend/src/components/*`, `frontend/src/api/*`.
- Testes: `backend/tests/unit`, `backend/tests/integration`, `backend/tests/contract`, `frontend/tests` (ou colocados junto aos componentes, conforme convenção do Vitest).
- Comando(s) de build/execução: `docker compose up --build` (ver `README.md`).
- Comando(s) de teste: `docker compose exec backend pytest`, `docker compose exec frontend npm test`.
- Nível de evidência esperado nesta fase: `LOCAL` (CI ainda não configurado — `A CONFIRMAR` em `STACK.md`).
- Critérios de aceite rastreados: `CA-001` a `CA-012` (ver `SPECIFICATION.md`), todos com evidência `PASS`/`FAIL`/`PENDENTE` registrada na tarefa correspondente.
- Pendências e riscos residuais: tolerâncias do Paralelepípedo de Descarte e desvio de rotação não têm valor numérico padrão (ver `context.md`) — cada ambiente/instalação deve configurá-los antes de uso real; autenticação não implementada (`NFR-006`); CI não configurado.
- Responsável pela validação: agente de IA executor de cada tarefa, com revisão humana antes de merge (Princípio 5 da constituição — código gerado por IA não substitui revisão humana de contrato, segurança e comportamento).
