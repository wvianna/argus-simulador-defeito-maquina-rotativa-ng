# TESTING.md — Estratégia de testes do Argus

## Níveis de teste

| Nível | Ferramenta | Escopo |
|---|---|---|
| Estático | `ruff`, `mypy` (back-end); `eslint`, `tsc` (front-end) | Lint, formatação e checagem de tipos em todo commit |
| Unitário | `pytest` (back-end); `vitest` + React Testing Library (front-end) | `signal_generator`, `fft_processor`, `discard_engine` (regra de ouro + Paralelepípedo), componentes de UI isolados |
| Integração | `pytest` + `testcontainers-python` (PostgreSQL) | Persistência de leituras/trash/snapshots, hierarquia Planta/Área/Máquina/Ponto, transação de descarte sob concorrência |
| Contrato/E2E | `httpx.AsyncClient` (API); Playwright (fluxo completo via UI, opcional conforme risco) | Endpoints de simulação e snapshot; fluxo configurar → simular → visualizar → snapshot |
| Manual/exploratório | Checklist registrado em `SUMMARY.md` da tarefa | Casos sem automação viável (ex.: inspeção visual do gráfico de FFT) |

## Gate mínimo por tarefa

1. Lint e type-check sem erros nos arquivos alterados.
2. Testes unitários do módulo afetado executados e aprovados.
3. Critérios de aceitação (`CA-###`) relacionados à tarefa verificados e registrados como `PASS`, `FAIL` ou `PENDENTE`.

## Casos obrigatórios para o motor de descarte (`discard_engine`)

Estes casos cobrem `FR-007`–`FR-011` e devem ter teste unitário dedicado antes de qualquer integração com banco de dados real:

- Primeira leitura de um Ponto (sem referência anterior) → sempre persistida (`CA-003`).
- Variação de rotação acima do desvio configurado + número de picos > 0 → persistida sem checar `R^3` (`CA-004`).
- Variação de rotação dentro do desvio + todos os picos dentro da tolerância `R^3` → descartada (`CA-006`).
- Variação de rotação dentro do desvio + ao menos um pico fora da tolerância `R^3` → persistida e vira nova referência (`CA-007`).
- Comparação deve sempre usar a última leitura **persistida**, nunca a última leitura avaliada/descartada.

## Casos obrigatórios para validação de entrada

- Taxa de amostragem ≤ 2× `Fmax` pretendida → rejeitada antes do processamento (`CA-011`, `NFR-001`).
- Parâmetros obrigatórios ausentes/inválidos → checklist impede início da simulação (`CA-010`).

## Ambientes de validação

- `LOCAL`: Docker Compose, banco de dados real ou `testcontainers`.
- `CI`: não configurado ainda (`A CONFIRMAR`).
- `STAGING` / `PRODUÇÃO`: não definidos (`A CONFIRMAR`).

Nenhuma tarefa pode declarar validação em `PRODUÇÃO` sem esse ambiente existir. Enquanto `CI` não estiver configurado, todo teste é `LOCAL` e deve registrar comando, versão de runtime e resultado.
