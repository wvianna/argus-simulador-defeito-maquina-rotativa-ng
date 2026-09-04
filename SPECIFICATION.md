# SPECIFICATION.md — Argus: Simulador de Defeito de Máquina Rotativa

> Especificação funcional e técnica do sistema, independente de implementação. Elaborada a partir de `docs/descricao.txt` (síntese), `docs/criterioArmazenamento.txt` e `docs/criterioDetermincacaoAnamalia.txt`, seguindo a skill `sdd-software`. Itens de stack não confirmados na documentação de origem estão marcados `A CONFIRMAR`.

## Objetivo

Fornecer um simulador de sinais vibracionais sintéticos de máquinas rotativas, capaz de:

1. Gerar sinais de vibração no domínio do tempo a partir de parâmetros de máquina (RPM, tipo de defeito, severidade, ruído de fundo) e de aquisição (taxa de amostragem, número de amostras).
2. Processar o sinal via FFT, extrair picos como vetores `R^3` (frequência, amplitude, fase) e métricas de energia (RMS total, RMS do ruído, RMS dos picos).
3. Aplicar um algoritmo de persistência seletiva ("Paralelepípedo de Descarte") que decide, para cada leitura simulada, se ela deve ser armazenada em definitivo ou descartada ("trash"), reproduzindo o comportamento real de um sistema de monitoramento em campo.
4. Expor uma interface web para configurar simulações, visualizar sinal/FFT/RMS, registrar "snapshots de defeito" (par sensor + anomalia) para treinamento/pesquisa de RCA, e observar indicadores de performance (tempo de processamento, taxa de descarte).

## Fora de escopo

- Aquisição de dados de hardware real (sensores físicos, DAQ). O sistema gera sinais sintéticos.
- Diagnóstico automático de causa raiz (RCA) além da classificação do catálogo de defeitos usado como entrada da simulação.
- Balanceamento de rotor, alinhamento a laser ou qualquer ação corretiva física — o sistema é uma ferramenta de simulação/treinamento, não de manutenção.
- Integração com sistemas de controle industrial (SCADA/CLP) em tempo real.

## Atores

| Ator | Papel |
|---|---|
| Usuário/Analista | Configura parâmetros de simulação, observa painel visual e FFT, registra snapshots de defeito. |
| Sistema simulador (back-end) | Gera sinal sintético, calcula FFT/RMS/DC, executa o algoritmo de descarte, persiste ou descarta leituras. |
| Motor de descarte | Sub-componente do back-end responsável pela "regra de ouro" e pelo Paralelepípedo de Descarte. |
| SGBDR / armazenamento | Persiste leituras aprovadas (definitivo) e leituras descartadas (trash), organizadas por Planta > Área > Máquina > Ponto. |
| Pesquisador/treinamento | Consome snapshots de defeito persistidos para estudo e desenvolvimento de algoritmos de RCA. |

## Estados e eventos

Fluxo principal de uma simulação:

```text
Configuração → Validação (checklist) → Geração de sinal → FFT/Extração de picos e RMS
   → Avaliação de descarte (regra de ouro + Paralelepípedo) → Persistência (definitivo | trash)
   → Visualização (painel + gráfico FFT) → [opcional] Snapshot de defeito
```

Eventos: `simulação iniciada`, `sinal gerado`, `fft calculada`, `picos extraídos`, `leitura avaliada para descarte`, `leitura persistida`, `leitura descartada`, `snapshot de defeito registrado`.

## Catálogo de tipos de defeito (entrada válida para "Tipo de Defeito")

| Categoria | Defeitos suportados |
|---|---|
| Desbalanceamento | Estático, de acoplamento (couple), dinâmico |
| Desalinhamento | Angular, paralelo |
| Folga mecânica | Estrutural/Soft Foot (Tipo A), mancal/móvel (Tipo B/C) |
| Instabilidade fluodinâmica | Oil Whirl (0,40X–0,49X), Oil Whip (lock em frequência natural) |
| Contato/roçamento | Rotor Rub (roçamento de rotor) |
| Desgaste de rolamento | BPFO, BPFI, BSF, FTF (com sidebands) |
| Outros | Cavitação, erro de sensor/térmico ("ski-slope") |

## Requisitos funcionais

- **FR-001**: O sistema deve permitir configurar os parâmetros de máquina: RPM, tipo de defeito (catálogo acima), severidade e ruído de fundo.
- **FR-002**: O sistema deve permitir configurar os parâmetros de aquisição: taxa de amostragem (Hz) e número de amostras.
- **FR-003**: O sistema deve gerar um sinal de vibração sintético no domínio do tempo, compatível com os parâmetros configurados e com a assinatura espectral do tipo de defeito selecionado.
- **FR-004**: O sistema deve calcular a FFT do sinal gerado e extrair picos como vetores `R^3` (frequência, amplitude, fase).
- **FR-005**: O sistema deve calcular RMS total, RMS do ruído e RMS dos picos para cada leitura simulada.
- **FR-006**: O sistema deve calcular o valor DC (bias/gap) equivalente para sensores de proximidade/deslocamento.
- **FR-007**: O sistema deve aplicar a regra de ouro antes do Paralelepípedo de Descarte: SE `|rotação atual − rotação armazenada| > desvio configurado` E número de picos da leitura `> 0`, ENTÃO a leitura é persistida diretamente, sem passar pela verificação `R^3`.
- **FR-008**: Quando a regra de ouro não se aplicar, o sistema deve avaliar cada pico da leitura atual contra a última leitura **efetivamente persistida** (não a última leitura descartada) usando o Paralelepípedo de Descarte (janela de tolerância em frequência, amplitude e fase).
- **FR-009**: Se todos os picos da leitura estiverem dentro da zona de tolerância `R^3`, o sistema deve descartar a leitura, registrando-a no armazenamento "trash".
- **FR-010**: Se ao menos um pico estiver fora da zona de tolerância `R^3`, o sistema deve persistir a leitura completa no armazenamento definitivo, e essa leitura passa a ser a nova referência de comparação.
- **FR-011**: Para o primeiro ponto de um ativo (sem leitura anterior armazenada), o sistema deve persistir a leitura independentemente da verificação `R^3` (condição de inicialização).
- **FR-012**: O sistema deve persistir, para cada leitura aprovada: picos `R^3`, RMS total, RMS do ruído, RMS dos picos, valor DC, níveis de alerta/shutdown vigentes, rotação e timestamp original da leitura.
- **FR-013**: O sistema deve organizar os dados persistidos segundo a hierarquia Planta > Área > Máquina > Ponto.
- **FR-014**: O front-end deve exibir um painel visual com o sinal simulado do acelerômetro e o valor de RMS.
- **FR-015**: O front-end deve exibir um gráfico de FFT com barras verticais para as frequências identificadas e uma linha horizontal representando o threshold (limiar de alarme).
- **FR-016**: O front-end deve permitir registrar um "snapshot de defeito": gravação em banco de dados do par sensor + anomalia, para uso em treinamento e pesquisa de RCA.
- **FR-017**: O front-end deve exibir indicadores de tempo de processamento e de taxa de descarte da simulação executada.
- **FR-018**: O front-end deve exibir um checklist de validação dos parâmetros de entrada, impedindo o início da simulação enquanto houver parâmetro pendente ou inválido.

## Requisitos não funcionais

- **NFR-001 (correção de amostragem)**: A taxa de amostragem configurada deve ser superior a 2× a frequência máxima (`Fmax`) pretendida (critério de Nyquist); configurações que violem esse critério devem ser rejeitadas pelo checklist (FR-018).
- **NFR-002 (observabilidade de performance)**: O tempo de processamento de cada simulação deve ser medido e exibido (ligado a FR-017). Meta numérica de latência: `A CONFIRMAR`.
- **NFR-003 (arquitetura de persistência)**: O armazenamento definitivo deve priorizar velocidade de ingestão em alta frequência sobre simplicidade de consulta, usando representação por vetores/offsets (não normalizada), conforme justificativa de ROI da documentação de origem.
- **NFR-004 (observabilidade de descarte)**: A taxa de descarte (proporção de leituras descartadas versus avaliadas) deve ser calculável e exposta ao usuário (ligado a FR-017).
- **NFR-005 (escalabilidade)**: Volume esperado de pontos monitorados simultaneamente e de simulações concorrentes: `A CONFIRMAR`.
- **NFR-006 (segurança)**: Mecanismo de autenticação/autorização para acesso ao painel e ao SGBDR: `A CONFIRMAR` (não definido na documentação de origem).
- **NFR-007 (stack)**: Linguagem, framework, runtime e banco de dados: `A CONFIRMAR`.

## Critérios de aceitação

- [ ] **CA-001**: DADO que o usuário configurou RPM, tipo de defeito, severidade e ruído de fundo válidos, QUANDO o usuário inicia a simulação, ENTÃO o sistema gera o sinal sintético e calcula a FFT sem erros. _(FR-001, FR-002, FR-003, FR-004)_
- [ ] **CA-002**: DADO um sinal gerado, QUANDO a FFT é processada, ENTÃO o sistema identifica os picos como vetores `R^3` e calcula RMS total, RMS do ruído, RMS dos picos e valor DC. _(FR-004, FR-005, FR-006)_
- [ ] **CA-003**: DADO que não existe leitura anterior armazenada para o ponto, QUANDO a primeira leitura é processada, ENTÃO ela é persistida independentemente do Paralelepípedo de Descarte. _(FR-011)_
- [ ] **CA-004**: DADO que `|rotação atual − rotação armazenada| > desvio configurado` E número de picos `> 0`, QUANDO uma nova leitura é avaliada, ENTÃO o sistema a persiste sem aplicar o Paralelepípedo de Descarte. _(FR-007)_
- [ ] **CA-005**: DADO que a variação de rotação está dentro do desvio configurado, QUANDO uma nova leitura é avaliada, ENTÃO o sistema aplica o Paralelepípedo de Descarte comparando cada pico à última leitura efetivamente persistida. _(FR-008)_
- [ ] **CA-006**: DADO que todos os picos de uma leitura estão dentro da zona de tolerância `R^3`, QUANDO a verificação é concluída, ENTÃO a leitura é descartada e registrada no armazenamento trash. _(FR-009)_
- [ ] **CA-007**: DADO que ao menos um pico está fora da zona de tolerância `R^3`, QUANDO a verificação é concluída, ENTÃO a leitura completa é persistida no armazenamento definitivo e passa a ser a nova referência. _(FR-010)_
- [ ] **CA-008**: DADO uma simulação concluída, QUANDO o usuário visualiza o painel, ENTÃO o sistema exibe o sinal do acelerômetro, o RMS e o gráfico de FFT (barras + linha de threshold). _(FR-014, FR-015)_
- [ ] **CA-009**: DADO uma simulação concluída, QUANDO o usuário aciona "snapshot de defeito", ENTÃO o sistema grava o par sensor + anomalia no banco de dados. _(FR-016)_
- [ ] **CA-010 (erro)**: DADO parâmetros de entrada incompletos ou inválidos, QUANDO o usuário tenta iniciar a simulação, ENTÃO o checklist de validação impede o início e indica os campos pendentes/incorretos. _(FR-018)_
- [ ] **CA-011 (erro/borda)**: DADO uma taxa de amostragem configurada menor ou igual a 2× a `Fmax` pretendida, QUANDO o usuário tenta iniciar a simulação, ENTÃO o sistema rejeita a configuração por violação do critério de Nyquist. _(NFR-001)_
- [ ] **CA-012**: DADO uma simulação concluída, QUANDO o usuário observa os indicadores, ENTÃO o sistema exibe tempo de processamento e taxa de descarte da execução. _(FR-017, NFR-002, NFR-004)_

## Interface de operações (contrato preliminar)

> Protocolo/tecnologia de transporte `A CONFIRMAR` (REST, RPC, etc.). Tabela descreve a operação em nível funcional.

| Campo | Operação: Executar simulação | Operação: Registrar snapshot de defeito |
|---|---|---|
| Entrada | RPM, tipo de defeito, severidade, ruído de fundo, taxa de amostragem, número de amostras | Referência da simulação/leitura, identificação do sensor, classificação de anomalia |
| Saída | Sinal no tempo, FFT (picos `R^3`), RMS (total/ruído/picos), DC, decisão de descarte, indicadores de tempo/taxa de descarte | Confirmação de gravação, identificador do snapshot |
| Autenticação/autorização | `A CONFIRMAR` | `A CONFIRMAR` |
| Idempotência/concorrência | Cada simulação é independente; ordenação de leituras por ponto é relevante para a regra de descarte (depende da última leitura persistida) | `A CONFIRMAR` |
| Limites | `A CONFIRMAR` (tamanho máx. de amostras, taxa de requisições) | `A CONFIRMAR` |
| Falha/timeout | Configuração inválida deve ser rejeitada antes do processamento (ver CA-010, CA-011) | `A CONFIRMAR` |

## Matriz de rastreabilidade

| Requisito | Critério de aceitação | Tipo de teste sugerido | Evidência |
|---|---|---|---|
| FR-001, FR-002, FR-003, FR-004 | CA-001 | Unitário (geração de sinal) + integração (pipeline) | PENDENTE |
| FR-004, FR-005, FR-006 | CA-002 | Unitário (FFT/RMS/DC) | PENDENTE |
| FR-011 | CA-003 | Unitário (inicialização de ponto) | PENDENTE |
| FR-007 | CA-004 | Unitário (regra de ouro) | PENDENTE |
| FR-008 | CA-005 | Unitário (Paralelepípedo de Descarte) | PENDENTE |
| FR-009 | CA-006 | Unitário (descarte → trash) | PENDENTE |
| FR-010 | CA-007 | Unitário (persistência → nova referência) | PENDENTE |
| FR-014, FR-015 | CA-008 | E2E/manual (painel e gráfico) | PENDENTE |
| FR-016 | CA-009 | Integração (persistência de snapshot) | PENDENTE |
| FR-018 | CA-010 | Unitário/E2E (checklist) | PENDENTE |
| NFR-001 | CA-011 | Unitário (validação de Nyquist) | PENDENTE |
| FR-017, NFR-002, NFR-004 | CA-012 | Manual/integração (indicadores) | PENDENTE |

## Premissas

- `docs/descricao.txt` é tratado como a síntese consolidada de `docs/criterioArmazenamento.txt` e `docs/criterioDetermincacaoAnamalia.txt`; os três documentos foram usados como fonte, sem conflito de conteúdo identificado.
- O armazenamento "trash" é um destino lógico para leituras descartadas (para fins de auditoria/simulação do fluxo real de descarte), não necessariamente uma tabela física distinta — decisão de design fica para `design.md`.
- O projeto está em estágio inicial: não há código, `README.md`, `AGENTS.md`, `STATUS.md`, `LICENSE` ou `.gitignore` no repositório no momento desta especificação.

## Riscos

- Ausência de definição de stack (linguagem, framework, banco de dados) impede estimar viabilidade de performance para geração de sinal e FFT em tempo real.
- Ausência de requisito de segurança pode ser aceitável para uma ferramenta de simulação/treinamento offline, mas deve ser confirmada antes de qualquer exposição em rede compartilhada.
- Falta de definição numérica para desvios do Paralelepípedo de Descarte (tolerância de frequência/amplitude/fase) e para o desvio de rotação da regra de ouro pode gerar comportamento não determinístico entre implementações.

## Perguntas bloqueadoras

1. Qual stack tecnológico (linguagem, framework de back-end, framework de front-end, banco de dados) deve ser usado?
2. Quais são os valores padrão (ou configuráveis) de tolerância do Paralelepípedo de Descarte (Δfrequência, Δamplitude, Δfase) e do desvio de rotação da regra de ouro?
3. O armazenamento "trash" deve ser persistido fisicamente (para auditoria) ou é apenas um indicador/métrica de simulação (taxa de descarte)?
4. Há requisito de autenticação/autorização para o painel web e para o acesso ao SGBDR?
5. Qual o volume esperado de simulações concorrentes e de pontos monitorados, para dimensionar metas de performance (NFR-002, NFR-005)?
