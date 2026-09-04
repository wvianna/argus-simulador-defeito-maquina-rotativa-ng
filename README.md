# Argus — Simulador de Defeito de Máquina Rotativa

Simulador de sinais vibracionais sintéticos de máquinas rotativas, usado para testar algoritmos de persistência seletiva (FFT + descarte por similaridade) e para gerar dados de treinamento para análise de causa raiz (RCA) de defeitos mecânicos.

> Estado do projeto: especificação e design concluídos, implementação ainda não iniciada. Veja [STATUS.md](STATUS.md) para o estado atual e [HANDOFF.md](HANDOFF.md) para continuidade entre agentes.

## Objetivo

- Gerar sinais de vibração no domínio do tempo a partir de parâmetros de máquina (RPM, tipo de defeito, severidade, ruído de fundo) e de aquisição (taxa de amostragem, número de amostras).
- Processar o sinal via FFT, extrair picos como vetores `R^3` (frequência, amplitude, fase) e métricas de energia (RMS total, RMS do ruído, RMS dos picos).
- Aplicar persistência seletiva ("Paralelepípedo de Descarte") que decide se cada leitura deve ser armazenada em definitivo ou descartada, reproduzindo o comportamento de um sistema de monitoramento em campo.
- Expor um painel web para configurar simulações, visualizar sinal/FFT/RMS e registrar snapshots de defeito para treinamento/pesquisa.

Detalhes completos de requisitos e critérios de aceitação: [SPECIFICATION.md](SPECIFICATION.md).

## Tecnologias

| Camada | Tecnologia |
|---|---|
| Back-end | Python 3.12, FastAPI, NumPy/SciPy, SQLAlchemy, Alembic |
| Front-end | React 18 + Vite + TypeScript, Recharts |
| Banco de dados | PostgreSQL 16 |
| Execução local | Docker + Docker Compose |

Justificativa e alternativas consideradas: [.specs/codebase/STACK.md](.specs/codebase/STACK.md).

## Requisitos

- Docker e Docker Compose instalados.
- Para desenvolvimento sem contêiner: Python 3.12+ e Node.js 20+.

## Como executar (ambiente local)

> O código de aplicação ainda não foi implementado (ver [STATUS.md](STATUS.md)). Os comandos abaixo refletem o fluxo alvo definido em [.specs/features/simulador-vibracao/design.md](.specs/features/simulador-vibracao/design.md) e devem ser confirmados assim que o `docker-compose.yml` e os projetos de back-end/front-end existirem.

```bash
# Subir back-end, front-end e banco de dados
docker compose up --build

# Rodar migrações do banco de dados (dentro do contêiner do back-end)
docker compose exec backend alembic upgrade head

# Rodar testes de back-end
docker compose exec backend pytest

# Rodar testes de front-end
docker compose exec frontend npm test
```

## Estrutura de diretórios

```text
.
├── docs/                         # Documentos de origem (critérios de armazenamento e de determinação de anomalia)
├── .specs/                       # Especificação técnica detalhada (SDD)
│   ├── project/                  # Constituição e roadmap do projeto
│   ├── codebase/                 # Stack, arquitetura, convenções e testes
│   └── features/simulador-vibracao/  # design.md, tasks.md e context.md do MVP
├── backend/                      # A CONFIRMAR — API FastAPI (ainda não criado)
├── frontend/                     # A CONFIRMAR — SPA React (ainda não criado)
├── SPECIFICATION.md              # Especificação funcional e técnica do sistema
├── AGENTS.md                     # Regras permanentes para agentes que alterarem este repositório
├── STATUS.md                     # Estado atual do desenvolvimento
└── HANDOFF.md                    # Transferência de contexto entre agentes
```

## Documentação técnica

- Especificação: [SPECIFICATION.md](SPECIFICATION.md)
- Constituição do projeto: [.specs/project/constitution.md](.specs/project/constitution.md)
- Roadmap: [.specs/project/ROADMAP.md](.specs/project/ROADMAP.md)
- Design do MVP: [.specs/features/simulador-vibracao/design.md](.specs/features/simulador-vibracao/design.md)
- Tarefas do MVP: [.specs/features/simulador-vibracao/tasks.md](.specs/features/simulador-vibracao/tasks.md)
- Critérios técnicos de origem (domínio de vibração): [docs/descricao.txt](docs/descricao.txt), [docs/criterioArmazenamento.txt](docs/criterioArmazenamento.txt), [docs/criterioDetermincacaoAnamalia.txt](docs/criterioDetermincacaoAnamalia.txt)

## Licença

Este projeto é distribuído sob a [Apache License 2.0](LICENSE).
