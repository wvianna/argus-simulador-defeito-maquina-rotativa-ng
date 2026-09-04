# MONOGRAFIA — RASTREABILIDADE

## Objetivos específicos → método → evidência → resultado → status

| # | Objetivo específico | Método | Evidência | Resultado | Status |
|---|---|---|---|---|---|
| 1 | Modelar geração sintética com catálogo de defeitos | Domínio `signal_generator.py` (perfis por ordem/rotação) | Testes unitários do gerador; assinaturas via API | 13 tipos; frequências derivadas de fr=RPM/60 | OK |
| 2 | Processamento espectral FFT com picos R³, RMS, DC e limiar | Domínio `fft_processor.py` | Testes unitários; resposta da API (`limiar_picos`, `limiar_amplitude`) | Picos R³, RMS, DC, Nyquist, limiar | OK |
| 3 | Motor de descarte (regra de ouro + Paralelepípedo R³) + persistência seletiva | Domínio `discard_engine.py` + camada `persistence` | Testes unitários do descarte + integração com Postgres | Decisão persistir/descartar; `leituras_trash` | OK |
| 4 | API REST + interface web (sinal, FFT com ordens N, indicadores, snapshot) | FastAPI + React/Recharts | Testes de contrato; E2E no navegador; capturas | Dashboard funcional | OK |
| 5 | Validar por testes automatizados e E2E | pytest/vitest/testcontainers + navegador | 63 + 12 testes PASS; verificação de assinaturas | Gates aprovados | OK |

## Problema → objetivo geral → método → resultado

| Problema | Objetivo geral | Método | Resultado |
|---|---|---|---|
| Volume massivo de dados brutos; necessidade de sinais de defeito para treinamento sem risco | Simulador com geração sintética parametrizável e persistência seletiva R³ | SDD + FastAPI/React/Postgres; testes em camadas | MVP validado com catálogo de 13 defeitos, descarte seletivo e painel web |

## Pendências de rastreabilidade

- Associar cada afirmação da fundamentação a uma referência bibliográfica verificada (ver `MONOGRAFIA_PENDENCIAS.md`).
- Confirmar objetivos com o orientador.
