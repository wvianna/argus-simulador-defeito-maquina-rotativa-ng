# Argus — Simulador de Defeito de Máquina Rotativa

Simulador de sinais vibracionais sintéticos de máquinas rotativas, usado para testar algoritmos de persistência seletiva (FFT + descarte por similaridade) e para gerar dados de treinamento para análise de causa raiz (RCA) de defeitos mecânicos.

> Estado do projeto: especificação, design e implementação do MVP concluídos (validação `LOCAL` aprovada — ver [STATUS.md](STATUS.md)).

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

## Arquitetura

### Visão geral (componentes e fluxo de dados)

```mermaid
flowchart LR
    subgraph Front-end [Front-end - React/Vite]
        UI[Painel de simulação]
        FFTChart[Gráfico de FFT + threshold]
        Checklist[Checklist de validação]
    end

    subgraph Backend [Back-end - FastAPI]
        API[API REST]
        GEN[Módulo de geração de sinal]
        FFTMOD[Módulo de FFT e extração R^3]
        DISCARD[Motor de descarte<br/>regra de ouro + Paralelepípedo]
        PERSIST[Camada de persistência]
    end

    subgraph DB [PostgreSQL]
        HIER[(Planta/Área/Máquina/Ponto)]
        LEITURAS[(leituras_persistidas)]
        TRASH[(leituras_trash)]
        SNAP[(snapshots_defeito)]
    end

    UI -->|POST /simulacoes| API
    Checklist -->|valida antes de enviar| API
    API --> GEN --> FFTMOD --> DISCARD
    DISCARD -->|aprovada| PERSIST --> LEITURAS
    DISCARD -->|descartada| PERSIST --> TRASH
    PERSIST --> HIER
    API -->|POST /snapshots| SNAP
    API -->|resposta: sinal, FFT, RMS, decisão| FFTChart
```

### Ciclo de vida de uma leitura (máquina de estados)

```mermaid
stateDiagram-v2
    [*] --> Configurado
    Configurado --> SinalGerado: gerar sinal
    SinalGerado --> FFTCalculada: calcular FFT/RMS/DC
    FFTCalculada --> AvaliandoDescarte
    AvaliandoDescarte --> Persistida: regra de ouro satisfeita\nOU pico fora da tolerância R^3\nOU primeira leitura do ponto
    AvaliandoDescarte --> Descartada: todos os picos dentro da tolerância R^3
    Persistida --> [*]
    Descartada --> [*]
```

### Modelo de dados (entidades e relacionamentos)

```mermaid
erDiagram
    PLANTAS ||--o{ AREAS : possui
    AREAS ||--o{ MAQUINAS : contem
    MAQUINAS ||--o{ PONTOS : possui
    PONTOS ||--o{ LEITURAS_PERSISTIDAS : gera
    PONTOS ||--o{ LEITURAS_TRASH : descarta
    LEITURAS_PERSISTIDAS ||--o{ SNAPSHOTS_DEFEITO : referencia
    LEITURAS_TRASH ||--o{ SNAPSHOTS_DEFEITO : referencia

    PLANTAS {
        uuid id PK
        text nome
    }
    AREAS {
        uuid id PK
        uuid planta_id FK
        text nome
    }
    MAQUINAS {
        uuid id PK
        uuid area_id FK
        text nome
    }
    PONTOS {
        uuid id PK
        uuid maquina_id FK
        text nome
        uuid ultima_leitura_persistida_id FK
    }
    LEITURAS_PERSISTIDAS {
        uuid id PK
        uuid ponto_id FK
        timestamp timestamp_original
        float rotacao
        jsonb picos_r3
        float rms_total
        float rms_ruido
        float rms_picos
        float valor_dc
        float nivel_alerta
        float nivel_shutdown
    }
    LEITURAS_TRASH {
        uuid id PK
        uuid ponto_id FK
        timestamp timestamp_original
        float rotacao
        jsonb picos_r3
        float rms_total
        float rms_ruido
        float rms_picos
        float valor_dc
        text motivo_descarte
    }
    SNAPSHOTS_DEFEITO {
        uuid id PK
        uuid leitura_id FK
        text leitura_tipo
        text sensor_id
        text tipo_defeito
        timestamp criado_em
    }
```

> `snapshots_defeito.leitura_id` é polimórfico: aponta para `leituras_persistidas` ou `leituras_trash` (campo `leitura_tipo` indica qual). Detalhes em [.specs/codebase/ARCHITECTURE.md](.specs/codebase/ARCHITECTURE.md).

## Requisitos

- Docker e Docker Compose instalados.
- Para desenvolvimento sem contêiner: Python 3.12+ e Node.js 20+.

## Como executar (ambiente local via Docker Compose)

```bash
# Subir banco de dados, back-end e front-end (o back-end roda as migrações no start)
docker compose up --build

# Painel web: http://localhost:5173  |  API: http://localhost:8000  |  Docs OpenAPI: http://localhost:8000/docs
```

> Para usar o painel é necessário existir um Ponto na hierarquia Planta > Área > Máquina > Ponto (a API não expõe endpoint de cadastro no MVP). Crie um ponto de exemplo no banco:
>
> ```bash
> docker compose exec db psql -U argus -d argus -c \
>   "WITH p AS (INSERT INTO plantas(id,nome) VALUES (gen_random_uuid(),'Planta Demo') RETURNING id), \
>          a AS (INSERT INTO areas(id,planta_id,nome) SELECT gen_random_uuid(), id, 'Área Demo' FROM p RETURNING id), \
>          m AS (INSERT INTO maquinas(id,area_id,nome) SELECT gen_random_uuid(), id, 'Máquina Demo' FROM a RETURNING id) \
>   INSERT INTO pontos(id,maquina_id,nome) SELECT gen_random_uuid(), id, 'Ponto Demo' FROM m RETURNING id;"
> ```

### Desenvolvimento sem contêiner

```bash
# Back-end (na raiz de backend/)
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
alembic upgrade head              # aplica migrações
uvicorn app.main:app --reload     # http://localhost:8000

# Front-end (na raiz de frontend/, o Vite faz proxy de /api -> localhost:8000)
npm install
npm run dev                       # http://localhost:5173
```

### Testes

```bash
# Back-end (na raiz de backend/, com .venv ativo)
ruff check app tests && mypy app && python -m pytest        # 49 testes (unit + integração + contrato)

# Front-end (na raiz de frontend/)
npx tsc -b && npx oxlint && npx vitest run                 # 9 testes
```

### Parar o ambiente

```bash
docker compose down            # remove os contêineres (mantém o volume do banco)
docker compose down -v         # remove também o volume (apaga os dados)
```

## Estrutura de diretórios

```text
.
├── docs/                         # Documentos de origem + capturas do dashboard (docs/imagens/)
├── .specs/                       # Especificação técnica detalhada (SDD)
│   ├── project/                  # Constituição e roadmap do projeto
│   ├── codebase/                 # Stack, arquitetura, convenções e testes
│   └── features/simulador-vibracao/  # design.md, tasks.md e context.md do MVP
├── backend/                    # API FastAPI (domain, persistence, api, alembic, tests)
├── frontend/                   # SPA React + Vite + Recharts (componentes e testes)
├── docker-compose.yml          # serviços db (Postgres 16), backend, frontend (nginx)
├── .env.example                # referência de variáveis de ambiente
├── SPECIFICATION.md              # Especificação funcional e técnica do sistema
├── AGENTS.md                     # Regras permanentes para agentes que alterarem este repositório
├── STATUS.md                     # Estado atual do desenvolvimento
└── HANDOFF.md                    # Transferência de contexto entre agentes
```

## Capturas de tela (dashboard)

Painel web do simulador (imagens em `docs/imagens/`).

![Dashboard — formulário de simulação](docs/imagens/dashboard-formulario.png)

### Exemplos de assinaturas espectrais

![Desbalanceamento — 1X dominante](docs/imagens/dashboard_desbalanceamento.png)

![Desalinhamento angular](docs/imagens/dashboard_desalinhamento_angular.png)

![Desalinhamento paralelo — 2X dominante + harmônicos pares](docs/imagens/dashboard_desalinhamento_paralelo.png)

![Instabilidade do filme de óleo (oil whirl)](docs/imagens/dashboard_instabilidade_fime_oleo.png)

![Mancal frouxo — família de harmônicos](docs/imagens/dashboard_mancal_frouxo.png)

![Dashboard — resultado completo: sinal, espectro FFT (rolamento BPFI) e telemetria](docs/imagens/dashboard-simulacao.png)

## Documentação técnica

- Especificação: [SPECIFICATION.md](SPECIFICATION.md)
- Constituição do projeto: [.specs/project/constitution.md](.specs/project/constitution.md)
- Roadmap: [.specs/project/ROADMAP.md](.specs/project/ROADMAP.md)
- Design do MVP: [.specs/features/simulador-vibracao/design.md](.specs/features/simulador-vibracao/design.md)
- Tarefas do MVP: [.specs/features/simulador-vibracao/tasks.md](.specs/features/simulador-vibracao/tasks.md)
- Critérios técnicos de origem (domínio de vibração): [docs/descricao.txt](docs/descricao.txt), [docs/criterioArmazenamento.txt](docs/criterioArmazenamento.txt), [docs/criterioDetermincacaoAnamalia.txt](docs/criterioDetermincacaoAnamalia.txt)

## Licença

Este projeto é distribuído sob a [Apache License 2.0](LICENSE).
