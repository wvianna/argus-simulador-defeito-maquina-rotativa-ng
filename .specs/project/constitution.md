# Constituição do Projeto — Argus (Simulador de Defeito de Máquina Rotativa)

> Copiado de `.agents/skills/sdd-software/references/constitution.md` e adaptado com as decisões técnicas do projeto. Decisões marcadas "(autônoma)" foram tomadas sem confirmação humana — ver `.specs/features/simulador-vibracao/context.md`.

## Identidade do sistema

- Produto/sistema: Argus — Simulador de Defeito de Máquina Rotativa.
- Linguagem/framework: Python 3.12 + FastAPI (back-end); React 18 + Vite + TypeScript (front-end). _(autônoma)_
- Banco de dados: PostgreSQL 16. _(autônoma)_
- Infraestrutura/deploy: Docker + Docker Compose, apenas ambiente local nesta fase; CI e staging/produção `A CONFIRMAR`. _(autônoma)_
- Ambientes de validação disponíveis: `LOCAL` apenas.

## Princípios obrigatórios

### 1. Segurança

- Autenticação e autorização: nenhuma nesta fase (uso local/interno). _(autônoma, `NFR-006`)_
- Dados sensíveis: o sistema não trata PII nem dados de pagamento; leituras vibracionais e metadados de máquina não são considerados sensíveis, mas segredos de conexão com banco de dados devem ficar em variáveis de ambiente (`.env`, nunca versionado).
- Entradas externas (parâmetros de simulação, payloads de API) devem ser validadas por schema (Pydantic no back-end) antes de qualquer processamento.
- Nenhuma alteração pode contornar validação de entrada sem decisão registrada em `SPECIFICATION.md`.

### 2. Concorrência e consistência

- Estado compartilhado: a última leitura efetivamente persistida por Ponto (`FR-008`) é o estado crítico para o algoritmo de descarte.
- Toda avaliação de descarte para um Ponto deve ler a última leitura persistida dentro de uma transação com isolamento suficiente para evitar leitura de estado obsoleto sob concorrência (ex.: `SELECT ... FOR UPDATE` ou controle de versão otimista por Ponto).
- Operações de simulação são idempotentes por execução (cada chamada gera uma nova leitura); não há deduplicação de simulações repetidas com os mesmos parâmetros.
- Transações de persistência (leitura definitiva ou trash) devem ser atômicas: nunca gravar parcialmente picos, RMS e metadados de uma mesma leitura.

### 3. Metas de qualidade e recursos

- Latência alvo: `A CONFIRMAR` (sem SLA definido; uso não produtivo nesta fase — `NFR-002`).
- Throughput alvo: uma simulação processada por requisição; processamento em lote fora de escopo do MVP.
- Disponibilidade alvo: não aplicável nesta fase (ambiente local).
- Limites de custo, rate limit e quota: não aplicável nesta fase.
- Persistência deve considerar falha parcial: se a gravação de uma leitura falhar, a leitura anterior persistida permanece como referência válida.

### 4. Contratos e compatibilidade

- Endpoints, eventos e schemas de dados devem ser documentados em `.specs/features/simulador-vibracao/design.md` antes da implementação.
- Mudanças incompatíveis nos contratos de API ou no schema de dados exigem atualização de `SPECIFICATION.md` e do `design.md` na mesma tarefa.
- Formatos de mensagem (JSON) devem declarar campos obrigatórios/opcionais e comportamento para dados inválidos (rejeição com erro `4xx`, nunca descarte silencioso).

### 5. Qualidade e rastreabilidade

- Todo requisito funcional tem `FR-###`; todo requisito não funcional tem `NFR-###` (ver `SPECIFICATION.md`).
- Cada requisito implementado possui teste ou evidência (`PASS`/`FAIL`/`PENDENTE`) registrado na tarefa correspondente em `tasks.md`.
- O build deve ser reproduzível via Docker; lint (`ruff`, `eslint`) e type-check (`mypy`, `tsc`) são obrigatórios em todo pull/commit.
- Código gerado por agente de IA não substitui revisão humana de contrato, segurança e comportamento antes de ser considerado definitivo.

### 6. Observabilidade e recuperação

- Logs estruturados (JSON) no back-end, incluindo tempo de processamento e resultado da avaliação de descarte por leitura.
- Métricas expostas: tempo de processamento por simulação e taxa de descarte agregada (`FR-017`, `NFR-002`, `NFR-004`).
- Falhas de configuração (ex.: violação de Nyquist) são rejeitadas antes do processamento (fail-fast), sem retry automático nesta fase.
- Falhas de persistência devem deixar evidência suficiente para diagnóstico (log com Ponto, timestamp e motivo da falha).

### 7. Processo de mudança

- `SPECIFICATION.md` é atualizada quando o comportamento aprovado muda; não se aceita corrigir apenas o código deixando o contrato obsoleto.
- Decisões que alteram risco, arquitetura, segurança, performance ou compatibilidade são registradas em `STATUS.md` ou em `context.md` da feature.
- Uma tarefa (`T-###`) deve ser pequena o bastante para revisão e verificação isoladas.
- Não se adicionam abstrações, dependências ou camadas sem benefício verificável (ex.: não introduzir fila de mensagens antes de haver necessidade real de processamento assíncrono).

## Gates padrão

- [x] Requisitos e critérios são observáveis e possuem IDs (`SPECIFICATION.md`).
- [x] Stack, versões e dependências foram confirmadas (autonomamente — ver `context.md`, pendente de revisão humana).
- [x] Caminhos de erro, retry e estado de falha foram considerados (`design.md`).
- [x] Segurança, concorrência e compatibilidade foram avaliadas quando aplicáveis (`design.md`).
- [ ] Testes foram executados no nível declarado: `LOCAL`, `CI`, `STAGING` ou `PRODUÇÃO` (pendente — implementação não iniciada).
- [ ] O resultado e as limitações estão registrados (pendente — implementação não iniciada).
