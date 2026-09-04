# design.md — Simulador de Vibração (MVP)

> Design técnico do MVP completo descrito em `SPECIFICATION.md`. Decisões de stack em `.specs/codebase/STACK.md`; arquitetura de alto nível em `.specs/codebase/ARCHITECTURE.md`. Este documento detalha os módulos, contratos e o comportamento necessário para implementação por agentes de IA.

## Módulos reutilizados e novos pontos de integração

Projeto greenfield: não há módulos reutilizados. Novos pontos de integração:

- Banco de dados PostgreSQL (único sistema externo).
- Nenhuma integração com serviços de terceiros no MVP.

## Costuras de teste

- `signal_generator`, `fft_processor` e `discard_engine` são funções/classes puras (entrada → saída), sem acesso direto a banco de dados ou rede, permitindo teste unitário sem qualquer infraestrutura.
- `discard_engine` recebe a "última leitura persistida" como parâmetro de entrada (injetado pelo chamador), em vez de consultar o banco diretamente — isso permite testar todas as combinações de regra de ouro e Paralelepípedo sem banco real.
- A camada `persistence` é a única com I/O; é testada separadamente via `testcontainers-python`.

## Fluxo de dados e máquina de estados

Ver diagrama de estados em `.specs/codebase/ARCHITECTURE.md`. Resumo textual:

1. API recebe parâmetros de simulação e valida (schema + regra de Nyquist).
2. `signal_generator` gera o sinal sintético no domínio do tempo.
3. `fft_processor` calcula FFT, extrai picos `R^3`, RMS (total/ruído/picos) e valor DC.
4. `discard_engine` recebe a leitura atual + última leitura persistida do Ponto (ou `None` se for a primeira) e decide: persistir direto (regra de ouro ou primeira leitura), persistir por pico fora da tolerância, ou descartar.
5. `persistence` grava a leitura em `leituras_persistidas` ou `leituras_trash`, atualizando `pontos.ultima_leitura_persistida_id` quando aplicável, em uma única transação.
6. API retorna sinal, picos, RMS, DC, decisão de descarte e indicadores (tempo de processamento) ao front-end.

## Contratos de API (nível de operação)

### `POST /simulacoes`

**Requisição**:

```json
{
  "ponto_id": "uuid",
  "rpm": 1780,
  "tipo_defeito": "desbalanceamento",
  "severidade": 0.6,
  "ruido_fundo": 0.05,
  "taxa_amostragem_hz": 25600,
  "numero_amostras": 4096,
  "limiar_picos": 0.05
}
```

`tipo_defeito` deve ser um dos valores do catálogo em `SPECIFICATION.md` (ex.: `sem_defeito`, `desbalanceamento`, `desalinhamento_angular`, `desalinhamento_paralelo`, `rocamento`, `mancal_frouxo`, `acoplamento_defeituoso`, `oil_whirl`, `whirl_atrito`, `rolamento_bpfo`, `rolamento_bpfi`, `rolamento_bsf`, `rolamento_ftf`).

**Resposta `200`**:

```json
{
  "leitura_id": "uuid",
  "sinal_tempo": [/* amostras, opcional/paginado se grande */],
  "limiar_picos": 0.05,
  "limiar_amplitude": 0.0266,
  "picos_r3": [{"frequencia_hz": 29.7, "amplitude": 4.2, "fase_graus": 12.0}],
  "rms_total": 5.1,
  "rms_ruido": 0.4,
  "rms_picos": 4.9,
  "valor_dc": 0.02,
  "rotacao": 1780,
  "descartada": false,
  "motivo_descarte": null,
  "tempo_processamento_ms": 42,
  "taxa_descarte_acumulada": 0.73
}
```

**Erros**:

- `422`: parâmetro obrigatório ausente ou inválido (schema Pydantic).
- `422`: `taxa_amostragem_hz <= 2 * fmax_estimado` → violação de Nyquist (`CA-011`).
- `404`: `ponto_id` inexistente.
- `500`: falha de persistência (log com contexto; leitura anterior permanece como referência válida).

**Autenticação/autorização**: nenhuma nesta fase (`NFR-006`).

**Idempotência/concorrência**: cada chamada gera uma nova leitura; concorrência tratada via transação sobre `pontos.ultima_leitura_persistida_id` (ver `ARCHITECTURE.md`).

**Limites**: `numero_amostras` deve ter teto configurável (evitar payload de resposta excessivo); valor exato `A CONFIRMAR`.

### `POST /snapshots`

**Requisição**:

```json
{
  "leitura_id": "uuid",
  "sensor_id": "string",
  "tipo_defeito": "desbalanceamento"
}
```

**Resposta `201`**: `{"snapshot_id": "uuid", "criado_em": "2026-09-04T12:00:00Z"}`.

**Erros**: `404` se `leitura_id` não existir; `422` se `tipo_defeito` não pertencer ao catálogo.

**Autenticação/autorização**: nenhuma nesta fase.

## Schema de dados e migrações

Ver schema lógico completo em `.specs/codebase/ARCHITECTURE.md`. Primeira migração (`T-001`) deve criar, nesta ordem: `plantas`, `areas`, `maquinas`, `pontos`, `leituras_persistidas`, `leituras_trash`, `snapshots_defeito`, com chaves estrangeiras respeitando a hierarquia.

## Ownership de transações, estado compartilhado e cache

- Ownership de `pontos.ultima_leitura_persistida_id`: exclusivamente o módulo `persistence`, dentro da transação de gravação da leitura.
- Nenhum cache no MVP (ver ADR-002 em `ARCHITECTURE.md`).

## Modelo de concorrência

- Sem processamento assíncrono/filas no MVP; cada requisição HTTP é tratada de forma independente pelo FastAPI (concorrência via event loop assíncrono do ASGI).
- Concorrência de escrita no mesmo Ponto é tratada via transação de banco de dados (lock de linha em `pontos` durante a decisão de descarte), não em memória da aplicação — necessário para suportar múltiplas instâncias do back-end no futuro.

## Tratamento de erro e resiliência

- Validação de entrada (schema + Nyquist) ocorre antes de qualquer processamento (fail-fast).
- Falha de persistência não deve deixar `ultima_leitura_persistida_id` em estado inconsistente (transação atômica com rollback).
- Sem retry automático nesta fase; erros são reportados ao chamador com código HTTP apropriado.

## Segurança

- Validação de entrada via Pydantic é a única barreira de segurança no MVP (sem autenticação — `NFR-006`, decisão autônoma em `context.md`).
- Superfícies de ataque relevantes mesmo sem autenticação: injeção via parâmetros de simulação (mitigada por schema estrito e uso de ORM parametrizado, nunca SQL concatenado).

## Observabilidade

- Log estruturado por simulação: `ponto_id`, parâmetros de entrada, decisão de descarte, tempo de processamento.
- Métrica agregada de taxa de descarte: `leituras_descartadas / leituras_avaliadas`, por Ponto e global.

## Impacto em performance, custo e compatibilidade

- Operação síncrona por requisição; performance depende do custo de FFT sobre `numero_amostras` — sem meta numérica definida (`NFR-002` em aberto).
- Sem custo de infraestrutura além do ambiente local.
- Contrato de API é a primeira versão; sem consumidores externos a proteger ainda.

## ADRs

Ver `ADR-001` e `ADR-002` em `.specs/codebase/ARCHITECTURE.md` (aplicam-se integralmente a este design).

## Alternativas rejeitadas

- Expor `sinal_tempo` completo sempre na resposta: rejeitado como padrão único — considerar paginação ou omissão opcional se `numero_amostras` for grande, para não violar limites de payload (`A CONFIRMAR` valor exato do limite).
- Persistir `sinal_tempo` bruto no banco: rejeitado; apenas os picos `R^3` e métricas agregadas são persistidos (`FR-012`), reduzindo volume de armazenamento, alinhado ao objetivo original dos documentos de origem.
