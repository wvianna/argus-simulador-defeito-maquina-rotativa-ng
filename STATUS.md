# STATUS.md — Estado atual do desenvolvimento

_Última atualização: 2026-09-04 (finalização da sessão de UI/UX, testes E2E e documentação)._

## Concluído

### Planejamento (SDD)

- `SPECIFICATION.md` — especificação funcional e técnica (19 `FR-###`, 7 `NFR-###`, 14 critérios de aceitação `CA-001`–`CA-014`, catálogo com 13 tipos de defeito alinhado a `docs/assinaturas_fft_falhas_maquinas_rotativas_IA.md`, matriz de rastreabilidade).
- `.specs/project/constitution.md` — princípios obrigatórios do projeto.
- `.specs/project/ROADMAP.md` — fases 1–5 de implementação do MVP.
- `.specs/codebase/STACK.md`, `ARCHITECTURE.md`, `CONVENTIONS.md`, `TESTING.md` — documentação de codebase.
- `.specs/features/simulador-vibracao/design.md`, `tasks.md` (T-001 a T-013), `context.md`.
- `README.md`, `AGENTS.md`, `LICENSE` (Apache 2.0), `.gitignore`, `.env.example`, `start.sh`, `stop.sh`.

### Implementação do MVP (T-001 a T-013)

**Back-end (Python 3.12 + FastAPI, em `backend/`):**
- Domínio: `signal_generator.py` com catálogo de 13 defeitos (`DEFECT_PROFILES`) e assinaturas espectrais por ordem/rotação (inclui sub-harmônicos de roçamento, `oil_whirl` 0,39–0,48X e frequências de rolamento BPFO/BPFI/BSF/FTF com sidebands); `fft_processor.py` (picos `R^3`, RMS, DC, Nyquist, `limiar_picos`/`limiar_amplitude`); `discard_engine.py` (regra de ouro + Paralelepípedo de Descarte `R^3`); `observability/logging.py`.
- Persistência: modelos SQLAlchemy (Planta/Área/Máquina/Ponto, `leituras_persistidas`, `leituras_trash`, `snapshots_defeito`), repositório transacional com lock de linha, Alembic com migração inicial (8 tabelas).
- API: `POST /simulacoes` (validação Pydantic + Nyquist, `limiar_picos`; resposta com `sinal_tempo` decimado, picos, RMS, DC, decisão de descarte, tempo, taxa de descarte e `limiar_picos`/`limiar_amplitude`), `POST /snapshots`, `GET /health`.

**Front-end (React 18 + Vite + TypeScript, em `frontend/`):**
- Layout industrial dark (redesenhado por sessão de UI); painel cabe em uma página (~844 px) sem rolagem.
- Componentes: `PainelSimulacao`, `PainelSinal`, `GraficoFFT` (Recharts), `IndicadoresSimulacao`, `ChecklistValidacao`, `SnapshotDefeito`, `Help` (tooltips de ajuda em todos os controles e painéis).
- FFT com barras finas (5 px), rótulos Hz + ordem `N` por barra, linha de limiar e rotação em Hz abaixo do gráfico (`FR-015`/`CA-014`).
- Slider de limiar de ruído (`limiar_picos`, `FR-019`/`CA-013`); UUID de ponto com default `69c0eb95-…a99`; validação Nyquist no cliente.
- Client HTTP tipado com mensagens de erro tratadas (rede/API).

**Infraestrutura:**
- `docker-compose.yml` (serviços `db`, `backend`, `frontend`), `backend/Dockerfile` (roda `alembic upgrade head` no start), `frontend/Dockerfile` (build + nginx com proxy `/api`).
- `start.sh` (setup + health-check + seed do Ponto demo) e `stop.sh`.

**Documentação:**
- `README.md` com arquitetura (diagramas Mermaid: fluxo, estados, ER) e seção de capturas de tela do dashboard (`docs/imagens/`, 7 imagens).

## Em andamento

- Nenhuma. MVP funcional e validado de ponta a ponta no navegador (`http://localhost:5173`).

## Pendente

- Configuração de CI (`A CONFIRMAR`).
- Revisão humana das decisões técnicas tomadas autonomamente (stack, persistência do trash, ausência de autenticação, tolerâncias configuráveis) — ver `.specs/features/simulador-vibracao/context.md`.
- Decisão definitiva sobre autenticação (`NFR-006`) antes de exposição fora do ambiente local.
- Calibração dos valores de tolerância do descarte e desvio de rotação (configuráveis via ambiente).
- Expor a geometria real do rolamento na UI (as frequências BPFO/BPFI/BSF/FTF usam geometria padrão em `signal_generator.py`).

## Problemas e erros conhecidos

- Sem bugs conhecidos. Deprecation warning de `testcontainers.postgres` (migrar para `testcontainers.community`) é cosmético.
- Artefato menor de a11y: o componente `Help` dentro de `<label>` faz o nome acessível incluir o sufixo "Ajuda" (os testes seguem passando).

## Testes realizados

- Back-end: `ruff check` (limpo), `mypy app` (limpo), `pytest` → **63 passed** (unit + integração + contrato). Nível: `LOCAL`.
- Front-end: `tsc -b` (limpo), `oxlint` (limpo), `vitest run` → **12 passed**. Nível: `LOCAL`.
- Migração `alembic upgrade head` aplicada em PostgreSQL 16 (8 tabelas).
- E2E no navegador: formulário e resultado completos (sinal, FFT, telemetria, snapshot); assinaturas verificadas via API (`desbalanceamento` 1X, `desalinhamento_paralelo` 2X/4X/6X, `oil_whirl` 0,42X, `rolamento_bpfi` BPFI + sidebands).

## Última alteração relevante

Finalização de documentação: seção "Capturas de tela (dashboard)" no `README.md` com as imagens de `docs/imagens/` (7 capturas).

## Próximo passo recomendado

1. Revisar com o responsável as decisões técnicas autônomas listadas em `context.md`.
2. Definir CI (`A CONFIRMAR`) para rodar os gates automaticamente.
3. Avançar a Fase 5 do roadmap (observabilidade/hardening) assim que o ambiente-alvo for definido (`NFR-005`/`NFR-006`).
