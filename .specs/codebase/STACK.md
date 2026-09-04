# STACK.md — Stack técnico do Argus

> Decisões marcadas "(autônoma)" foram tomadas sem confirmação humana (usuário indisponível). Ver justificativa completa e alternativas consideradas em `.specs/features/simulador-vibracao/context.md`.

## Back-end

- **Linguagem/runtime**: Python 3.12. _(autônoma)_
- **Framework web**: FastAPI (ASGI, validação nativa via Pydantic v2, geração automática de OpenAPI). _(autônoma)_
- **Processamento numérico**: NumPy + SciPy (`scipy.fft`) para geração de sinal sintético e cálculo de FFT.
- **ORM/driver de banco**: SQLAlchemy 2.x (engine assíncrono, `asyncpg`) + Alembic para migrações.
- **Servidor ASGI**: Uvicorn.
- **Gerenciador de pacotes**: Poetry (recomendado) ou `pip` + `requirements.txt` — escolha exata `A CONFIRMAR` na primeira tarefa de bootstrap (`T-001`).
- **Lint/format/type-check**: `ruff` (lint + format) e `mypy`.
- **Testes**: `pytest` + `pytest-asyncio`; `httpx.AsyncClient` para testes de contrato da API; `testcontainers-python` (PostgreSQL) para testes de integração.

## Front-end

- **Framework**: React 18 + Vite + TypeScript. _(autônoma)_
- **Gráficos**: Recharts (barras de FFT + linha de threshold; série temporal do sinal do acelerômetro).
- **Gerenciador de pacotes**: npm (ou pnpm — `A CONFIRMAR` na tarefa de bootstrap do front-end).
- **Lint/format**: ESLint + Prettier.
- **Testes**: Vitest + React Testing Library (unitário/componente); Playwright para E2E do fluxo de simulação (opcional, conforme risco — ver `TESTING.md`).

## Banco de dados

- **SGBD**: PostgreSQL 16. _(autônoma)_
- **Justificativa**: suporte nativo a tipos JSON/array para armazenar vetores de picos `R^3` sem normalizar cada pico em linha própria (alinhado a `NFR-003` — arquitetura não normalizada priorizando ingestão), além de robustez para consultas relacionais na hierarquia Planta/Área/Máquina/Ponto.
- **Alternativa considerada e não escolhida**: SQLite (mais simples, mas sem bom suporte a concorrência de escrita, relevante para `FR-008` sob carga simultânea) e TimescaleDB (otimizações de série temporal não necessárias no volume atual do MVP — reavaliar se `NFR-005` definir volume alto).

## Infraestrutura e execução

- **Ambiente local**: Docker + Docker Compose, com serviços `backend`, `frontend`, `db`.
- **CI**: não configurado (`A CONFIRMAR`).
- **Staging/produção**: não definido (`A CONFIRMAR`) — ver perguntas bloqueadoras em `SPECIFICATION.md`.
- **Variáveis de ambiente**: conexão com banco de dados, tolerâncias do Paralelepípedo de Descarte e desvio de rotação da regra de ouro (ver `design.md`), nunca versionadas (`.env` está no `.gitignore`; usar `.env.example` como referência de chaves esperadas).

## Versões mínimas

| Componente | Versão mínima |
|---|---|
| Python | 3.12 |
| Node.js | 20 |
| PostgreSQL | 16 |
| Docker | 24 |
| Docker Compose | v2 (plugin `docker compose`) |
