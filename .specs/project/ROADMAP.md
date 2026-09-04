# ROADMAP.md — Argus (Simulador de Defeito de Máquina Rotativa)

> Fases de implementação do MVP definido em `SPECIFICATION.md`. Cada fase corresponde a um grupo de tarefas em `.specs/features/simulador-vibracao/tasks.md`.

## Fase 1 — Núcleo de geração e processamento de sinal

- Schema de banco de dados e migrações (hierarquia Planta > Área > Máquina > Ponto).
- Módulo de geração de sinal sintético a partir de RPM, tipo de defeito, severidade e ruído de fundo.
- Módulo de FFT: extração de picos `R^3` (frequência, amplitude, fase) e cálculo de RMS total/ruído/picos e valor DC.

Cobre: `FR-001`–`FR-006`, `NFR-001`, `NFR-007`.

## Fase 2 — Motor de descarte e persistência seletiva

- Implementação da regra de ouro (variação de rotação + número de picos).
- Implementação do Paralelepípedo de Descarte (janela de tolerância `R^3` configurável).
- Persistência de leituras definitivas e de leituras descartadas (trash).

Cobre: `FR-007`–`FR-013`, `NFR-003`.

## Fase 3 — API e contrato

- Endpoint para executar simulação (parâmetros → sinal, FFT, decisão de descarte, indicadores).
- Endpoint para registrar snapshot de defeito (sensor + anomalia).
- Validação de entrada e rejeição fail-fast de configurações inválidas (ex.: violação de Nyquist).

Cobre: `FR-014` (contrato), `FR-016`, `FR-018`, `NFR-001`.

## Fase 4 — Front-end

- Painel visual: sinal do acelerômetro simulado e RMS.
- Gráfico de FFT: barras por frequência + linha de threshold.
- Checklist de validação de parâmetros antes de iniciar simulação.
- Ação de snapshot de defeito e exibição de indicadores de tempo de processamento/taxa de descarte.

Cobre: `FR-014`, `FR-015`, `FR-016`, `FR-017`, `FR-018`.

## Fase 5 — Observabilidade e hardening

- Logs estruturados e métricas de tempo/taxa de descarte.
- Testes de integração com banco de dados real (ou em contêiner).
- Revisão de segurança e decisão definitiva sobre autenticação (`NFR-006`) antes de qualquer exposição além do ambiente local.

Cobre: `NFR-002`, `NFR-004`, `NFR-005`, `NFR-006`.

## Fora do roadmap do MVP

- Diagnóstico automático de causa raiz (RCA).
- Integração com hardware real de aquisição.
- Deploy em nuvem / staging / produção (sem decisão registrada — ver perguntas bloqueadoras em `SPECIFICATION.md`).
