# Assinaturas Espectrais de Falhas em Máquinas Rotativas — Especificação para Geração de FFT por IA

**Versão:** 1.0  
**Objetivo:** fornecer a um modelo de IA uma especificação parametrizada para gerar uma lista de picos espectrais esperados de uma FFT a partir de **rotação (RPM)**, **tipo de defeito** e, quando necessário, parâmetros construtivos da máquina.

> **Importante:** as frequências características são baseadas na literatura de diagnóstico de vibrações. As amplitudes relativas propostas neste documento são **parâmetros de síntese para geração de sinais/datasets**, não valores universais de severidade. A amplitude real depende de massa, rigidez, amortecimento, posição do sensor, carga, ressonâncias, tipo de acoplamento, montagem e instrumentação.

---

## 1. Princípio geral

A frequência de rotação é:

\[
f_r = \frac{RPM}{60}
\]

onde:

- `RPM` = velocidade de rotação em rpm;
- `f_r` = frequência de rotação em Hz.

A ordem `kX` corresponde a:

\[
f_{kX}=k f_r
\]

Exemplos para `RPM = 1800`:

| Ordem | Frequência |
|---:|---:|
| 0,5X | 15 Hz |
| 1X | 30 Hz |
| 1,5X | 45 Hz |
| 2X | 60 Hz |
| 3X | 90 Hz |
| 4X | 120 Hz |
| 10X | 300 Hz |

O modelo deve sempre calcular as frequências a partir da RPM, e **não armazenar frequências absolutas fixas**.

---

# 2. Representação recomendada da assinatura FFT

Para geração sintética, representar cada pico como:

```yaml
peak:
  frequency_hz: <valor>
  order_x: <valor>
  amplitude_norm: <0..1>
  bandwidth_hz: <valor>
  peak_type: synchronous | sub_synchronous | super_synchronous | bearing | sideband | broadband
  direction: radial | axial | tangential | unknown
  confidence: <0..1>
```

A amplitude deve ser normalizada em relação ao maior pico da janela:

\[
A_{norm}=\frac{A_i}{A_{max}}
\]

Também é possível utilizar amplitude em RMS, mm/s RMS, g RMS ou aceleração, mas a unidade precisa ser mantida consistente em todo o dataset.

---

# 3. Regras gerais para um gerador de FFT

O gerador deve:

1. calcular `f_r = RPM / 60`;
2. selecionar a família espectral associada ao defeito;
3. calcular cada frequência a partir de `f_r`;
4. adicionar variação aleatória pequena na amplitude;
5. adicionar ruído de fundo;
6. aplicar uma largura de pico compatível com a resolução da FFT;
7. permitir harmônicos e bandas laterais;
8. permitir variação de severidade;
9. evitar que a assinatura de um defeito seja perfeitamente determinística;
10. manter as frequências fisicamente coerentes com a RPM.

### Modelo de amplitude sintética

Para cada componente:

\[
A_i=A_{base}\,S_i\,R_i
\]

onde:

- `A_base` = escala geral do sinal;
- `S_i` = peso da componente associado ao defeito;
- `R_i` = fator aleatório, por exemplo `0,85–1,15`.

Para um dataset de treinamento, recomenda-se variar:

```text
RPM
carga
severidade
amplitude
ruído
fase
posição do sensor
largura dos picos
frequência natural
tipo de acoplamento
```

---

# 4. Sem defeito

## Assinatura esperada

Uma máquina saudável ainda pode apresentar um pico em `1X`, pois existe alguma componente residual de desbalanceamento, excentricidade e outras excitações síncronas.

### Picos

| Componente | Frequência | Peso sintético sugerido |
|---|---:|---:|
| 1X | `f_r` | 0,10–0,30 |
| 2X | `2 f_r` | 0,00–0,05 |
| 3X | `3 f_r` | 0,00–0,03 |
| Ruído | banda larga | baixo |

### Regra IA

```text
SEM_DEFEITO:
  pico principal permitido em 1X
  2X e 3X devem permanecer baixos
  não criar sequência forte de harmônicos
  não criar frequências características de rolamento
  não criar sub-síncronas fortes
```

Um espectro saudável não significa necessariamente `FFT = 0`.

Um experimento publicado com rotor saudável a 1200 rpm mostrou um pico em 1X e praticamente ausência de 2X, ilustrando esse comportamento. [1]

---

# 5. Desbalanceamento

## Mecanismo

O centro de massa do rotor não coincide com o eixo geométrico de rotação.

## Assinatura espectral

A característica clássica é um **pico dominante em 1X**.

| Componente | Frequência | Peso relativo |
|---|---:|---:|
| 1X | `f_r` | **1,00** |
| 2X | `2 f_r` | 0,00–0,15 |
| 3X | `3 f_r` | 0,00–0,08 |
| demais | `k f_r` | baixo |

### Característica direcional

- predominantemente radial;
- normalmente mais forte em direção horizontal/vertical dependendo da máquina;
- componente axial tende a ser menor que a radial.

### Regra IA

```text
DESBALANCEAMENTO:
  gerar pico forte em 1X
  gerar poucos harmônicos
  evitar 2X dominante
  evitar famílias BPFO/BPFI/BSF/FTF
  evitar sub-harmônicos fortes
```

A literatura de análise de máquinas rotativas identifica o desbalanceamento principalmente por `1X` da velocidade de rotação. [2]

---

# 6. Desalinhamento

O desalinhamento pode ser:

- angular;
- paralelo;
- combinado.

Em geral aparecem componentes `1X`, `2X` e harmônicos superiores, com grande importância da direção axial e da configuração do acoplamento.

A literatura também alerta que a assinatura exata depende do acoplamento, velocidade e magnitude do desalinhamento; portanto `2X` é um forte indicador, mas não deve ser tratado isoladamente como diagnóstico definitivo. [3][4]

---

# 7. Desalinhamento angular

## Característica

O desalinhamento angular produz momentos e esforços axiais.

### Assinatura sintética

| Componente | Frequência | Peso relativo |
|---|---:|---:|
| 1X | `f_r` | 0,30–0,70 |
| 2X | `2 f_r` | **0,60–1,00** |
| 3X | `3 f_r` | 0,10–0,40 |
| 1,5X | `1,5 f_r` | 0,05–0,25 |
| 2,5X | `2,5 f_r` | 0,05–0,20 |
| 4X | `4 f_r` | 0,05–0,20 |

A direção axial deve receber maior peso.

Um estudo experimental recente encontrou, para desalinhamento angular, componentes 1X, 2X, 3X e componentes fracionários como 1,5X e 2,5X, além de aumento do piso de ruído. [4]

### Regra IA

```text
DESALINHAMENTO_ANGULAR:
  2X elevado
  1X também presente
  permitir 3X
  permitir 1,5X e 2,5X
  permitir bandas laterais
  aumentar componente axial
  aumentar noise floor moderadamente
```

---

# 8. Desalinhamento paralelo

## Característica

É comum observar forte componente `2X`, frequentemente acompanhada de `1X` e harmônicos pares.

### Assinatura

| Componente | Frequência | Peso relativo |
|---|---:|---:|
| 1X | `f_r` | 0,20–0,60 |
| 2X | `2 f_r` | **0,80–1,00** |
| 4X | `4 f_r` | 0,20–0,60 |
| 6X | `6 f_r` | 0,05–0,35 |
| 8X | `8 f_r` | 0,02–0,20 |

O `2X` deve ser o principal indicador sintético.

Um experimento a 1200 rpm observou 1X em 20 Hz e forte 2X em 40 Hz sob desalinhamento paralelo, seguido de harmônicos pares 4X, 6X e 8X. [4]

### Regra IA

```text
DESALINHAMENTO_PARALELO:
  2X dominante
  1X moderado
  gerar principalmente harmônicos pares
  4X > 6X > 8X
  componente radial elevada
```

---

# 9. Roçamento rotor-estator

O roçamento é um fenômeno não linear. A assinatura depende da intensidade do contato.

## Roçamento leve

| Componente | Frequência |
|---|---:|
| 1X | `f_r` |
| 2X | `2 f_r` |
| 3X | `3 f_r` |
| 4X+ | `k f_r` |

Pode aparecer uma série rica de harmônicos.

## Roçamento severo

Adicionar sub-harmônicos:

| Componente | Frequência |
|---|---:|
| 1/2X | `0,5 f_r` |
| 1/3X | `0,333 f_r` |
| 2/3X | `0,667 f_r` |
| 1X | `f_r` |
| 2X | `2 f_r` |
| 3X | `3 f_r` |
| 4X+ | `k f_r` |

Estudos experimentais mostram que roçamento leve pode produzir 1X, 2X e 3X, enquanto roçamento severo pode apresentar sub-harmônicos como 1/3X e 2/3X. Espectros ricos em linhas também são característicos de rub. [5][6]

### Regra IA

```text
ROÇAMENTO:
  gerar 1X + harmônicos
  aumentar quantidade de linhas espectrais
  severidade baixa:
      1X, 2X, 3X
  severidade alta:
      adicionar 0,5X, 1/3X, 2/3X
  aumentar noise floor
  permitir assimetria entre componentes
```

---

# 10. Problemas de mancal

## 10.1 Mancal defeituoso — rolamento de elementos rolantes

**Não é correto definir a frequência do defeito apenas pela RPM.**

É necessário conhecer a geometria do rolamento.

Parâmetros:

```text
n   = número de elementos rolantes
Bd  = diâmetro do elemento rolante
Pd  = diâmetro de passo
φ   = ângulo de contato
fr  = frequência de rotação
```

### BPFO — defeito na pista externa

\[
BPFO =
\frac{n}{2}f_r
\left[
1-\frac{Bd}{Pd}\cos(\phi)
\right]
\]

### BPFI — defeito na pista interna

\[
BPFI =
\frac{n}{2}f_r
\left[
1+\frac{Bd}{Pd}\cos(\phi)
\right]
\]

### BSF — frequência de rotação do elemento

\[
BSF =
\frac{Pd}{2Bd}f_r
\left[
1-\left(\frac{Bd}{Pd}\cos(\phi)\right)^2
\right]
\]

### FTF — frequência fundamental da gaiola

\[
FTF =
\frac{1}{2}f_r
\left[
1-\frac{Bd}{Pd}\cos(\phi)
\right]
\]

Essas expressões são apresentadas pela SKF para diagnóstico espectral de rolamentos. [7]

---

## 10.2 Defeito de pista externa — BPFO

### Assinatura

```text
BPFO
2×BPFO
3×BPFO
4×BPFO
...
```

Componente de `1X` pode aparecer como modulação, mas não deve ser confundida com a frequência fundamental do defeito.

### Modelo

\[
f_i=k\cdot BPFO
\]

para:

```text
k = 1,2,3,4,...,N
```

### Regra IA

```text
MANCAL_BPFO:
  gerar BPFO dominante
  gerar harmônicos de BPFO
  opcionalmente gerar bandas laterais ±1X
  adicionar ressonância de alta frequência
  aumentar amplitude conforme severidade
```

---

# 11. Defeito de pista interna — BPFI

### Assinatura

\[
f_i=k\cdot BPFI
\]

Além dos harmônicos de BPFI, são comuns **bandas laterais espaçadas por 1X**.

Exemplo:

```text
BPFI - 1X
BPFI
BPFI + 1X

2×BPFI - 1X
2×BPFI
2×BPFI + 1X
```

Defeitos na pista interna apresentam frequentemente bandas laterais associadas à rotação porque a posição do defeito em relação ao sensor varia durante a rotação. [8][9]

### Regra IA

```text
MANCAL_BPFI:
  gerar BPFI
  gerar 2×BPFI, 3×BPFI...
  adicionar sidebands em ±1X
  aumentar conteúdo de alta frequência
```

---

# 12. Defeito no elemento rolante — BSF

### Assinatura

\[
f_i=k\cdot BSF
\]

Podem aparecer:

```text
BSF
2×BSF
3×BSF
...
```

com bandas laterais dependendo da carga e da posição do elemento.

### Regra IA

```text
MANCAL_BSF:
  gerar BSF
  gerar harmônicos de BSF
  permitir sidebands em ±FTF ou ±1X
  gerar conteúdo de alta frequência
```

---

# 13. Defeito de gaiola — FTF

### Assinatura

\[
f_i=k\cdot FTF
\]

Como `FTF` é normalmente subsíncrona em relação à rotação, o modelo deve procurar:

```text
FTF
2×FTF
3×FTF
...
```

### Regra IA

```text
MANCAL_FTF:
  gerar pico em FTF
  gerar harmônicos
  permitir bandas laterais
  combinar com componentes 1X
```

---

# 14. Observação importante sobre FFT de rolamentos

Para rolamentos, a frequência característica pode ser pouco evidente na FFT bruta.

A literatura recomenda frequentemente:

```text
aceleração
→ filtragem/banda ressonante
→ demodulação/envelope
→ FFT do envelope
```

Os impactos do defeito excitam ressonâncias estruturais de alta frequência. A análise do envelope normalmente fornece uma assinatura mais clara do que a FFT direta do sinal bruto. [8][9][10]

Portanto, para um dataset de IA, é recomendável manter dois tipos de espectro:

```text
FFT_RAW
FFT_ENVELOPE
```

---

# 15. Mancal ou suporte frouxos

Aqui o defeito não é uma frequência geométrica de rolamento. É uma não linearidade mecânica associada à folga/afrouxamento.

### Assinatura típica

```text
1X
2X
3X
4X
5X
...
```

podendo existir uma família extensa de harmônicos.

Também podem aparecer sub-harmônicos, especialmente quando há folga e impactos.

### Modelo

\[
f_i=kf_r
\]

com:

```text
k = 1,2,3,...,10
```

e opcionalmente:

```text
0,5X
1,5X
2,5X
...
```

A literatura descreve energia de banda larga aproximadamente entre 1X e 10X, com harmônicos da rotação sobrepostos; folgas entre mancal e suporte podem produzir 1X proeminente e, em alguns casos, 2X e 3X. [11][12]

### Regra IA

```text
MANCAL_SUPORTE_FROUXO:
  1X moderado/alto
  2X e 3X elevados
  4X..10X possíveis
  permitir 0,5X e harmônicos fracionários
  aumentar noise floor
  amplitude instável
```

A característica importante para classificação é a **família de harmônicos**, e não apenas um pico isolado.

---

# 16. Acoplamento defeituoso

"Acoplamento defeituoso" é uma categoria ampla e não possui uma única frequência universal.

Pode incluir:

```text
desalinhamento
desgaste
folga
elemento elástico deteriorado
problema de fixação
excentricidade
falha de elemento do acoplamento
```

## Assinatura genérica

```text
1X
2X
3X
```

com possibilidade de:

```text
4X+
sidebands
aumento axial
aumento radial
```

### Modelo sintético

| Componente | Peso |
|---|---:|
| 1X | 0,30–0,80 |
| 2X | 0,50–1,00 |
| 3X | 0,10–0,50 |
| 4X | 0,05–0,30 |
| sidebands | 0,05–0,30 |

A literatura mostra que desalinhamento através de acoplamentos pode aumentar os harmônicos, especialmente 1X e 2X, e que o tipo de acoplamento influencia fortemente o espectro. [3][13]

### Regra IA

```text
ACOPLAMENTO_DEFEITUOSO:
  gerar 1X e 2X
  permitir 3X e 4X
  permitir sidebands
  aumentar componente axial quando apropriado
  não utilizar somente 2X como critério definitivo
```

---

# 17. Instabilidades de whirl

Whirl é diferente de uma falha puramente síncrona.

O modelo deve distinguir:

```text
f_rotor = RPM / 60
f_whirl ≠ necessariamente f_rotor
```

As componentes podem ser:

- subsíncronas;
- síncronas;
- supersíncronas;
- travadas em uma frequência natural.

---

# 18. Whirl por óleo — instabilidade do filme de óleo

Também chamado de **oil whirl**.

Uma assinatura clássica ocorre em uma frequência aproximadamente:

\[
f_{oil}=0,39\ldots0,48\,f_r
\]

ou, em algumas referências práticas:

\[
f_{oil}\approx0,40\ldots0,48\,f_r
\]

Uma referência de rotodinâmica reporta tipicamente `0,39X–0,48X`; outras referências usam aproximadamente `0,40X–0,48X`. [14][15]

### Exemplo

Para:

```text
RPM = 3600
fr = 60 Hz
```

o oil whirl esperado pode estar aproximadamente entre:

```text
23,4 Hz
e
28,8 Hz
```

### Assinatura

| Componente | Frequência |
|---|---:|
| Oil Whirl | `0,39–0,48X` |
| 1X | `1X` |
| harmônicos | podem aparecer |
| ressonância | depende do rotor |

### Regra IA

```text
OIL_WHIRL:
  gerar pico forte entre 0,39X e 0,48X
  permitir deslocamento dentro desse intervalo
  gerar 1X simultaneamente
  aumentar amplitude subsíncrona com a instabilidade
  permitir bandas/modulação
```

**Importante:** o valor exato não deve ser fixado em 0,45X para todos os casos. O modelo deve amostrar a razão dentro do intervalo fisicamente plausível.

---

# 19. Whirl por atrito — dry-friction whirl

O whirl por atrito associado a contato rotor-estator é um fenômeno de **precessão autoexcitada**.

Uma diferença fundamental em relação ao oil whirl é que **não existe uma razão universal simples como 0,45X que possa ser calculada apenas a partir da RPM**.

A literatura sobre dry-friction backward whirl descreve regimes de whirl com frequência não síncrona e, em determinadas condições, transição para **dry whip**, no qual a frequência pode ficar limitada por uma frequência natural do sistema rotor-estator. [16][17][18]

### Regra de geração

Para um modelo puramente baseado em RPM:

```text
NÃO FIXAR:
  f_whirl = 0,45X
```

Em vez disso:

```text
f_whirl = função(RPM, clearance, friction, stiffness, damping, critical_speed)
```

Quando esses parâmetros não estiverem disponíveis, o modelo deve gerar uma assinatura **hipotética** e marcar a frequência como `model_assumed`.

### Dry whirl

Pode apresentar:

```text
f_whirl ≠ 1X
harmônicos
componentes backward
```

### Dry whip

Quando ocorre travamento em uma frequência natural:

```text
f_whirl ≈ f_n
```

mesmo quando a velocidade de rotação continua aumentando.

### Regra IA

```text
WHIRL_ATRITO:
  se critical_speed conhecida:
      permitir componente próxima da frequência crítica
  se parâmetros de rotor-estator conhecidos:
      calcular/estimar frequência de whirl
  se não:
      gerar faixa paramétrica e marcar como hipótese
  adicionar componentes de rub/harmônicos
  permitir comportamento não síncrono
```

---

# 20. Tabela mestre de classificação

| Defeito | Frequência dominante esperada | Harmônicos | Sub-harmônicos | Sidebands | Direção típica |
|---|---|---|---|---|---|
| Sem defeito | 1X baixo | baixos | não | não | radial |
| Desbalanceamento | **1X** | baixos | não | não | radial |
| Desalinhamento angular | **2X + 1X** | 3X+ | possível | possível | axial |
| Desalinhamento paralelo | **2X + 1X** | 4X, 6X, 8X | possível | possível | radial |
| Roçamento | 1X | **muitos** | **possíveis** | possível | radial |
| Mancal defeituoso | BPFO/BPFI/BSF/FTF | muitos | não necessariamente | **frequentes** | radial |
| Mancal/suporte frouxo | 1X | **2X...10X** | possíveis | possível | radial |
| Acoplamento defeituoso | 1X/2X | 3X+ | possível | possível | radial/axial |
| Oil whirl | **0,39–0,48X** | possíveis | subsíncrono | possível | radial |
| Whirl por atrito | não universal | possíveis | não universal | possível | radial |

---

# 21. Prioridade dos indicadores para classificação por IA

O classificador não deve utilizar apenas o maior pico.

Uma estratégia melhor:

```text
score(defeito) =
    peso_frequência
  + peso_harmônicos
  + peso_sidebands
  + peso_subharmônicos
  + peso_direção
  + peso_evolução_com_RPM
  + peso_evolução_com_severidade
```

### Exemplos

#### Desbalanceamento

```text
score alto se:
  1X dominante
  radial dominante
  poucos harmônicos
```

#### Desalinhamento

```text
score alto se:
  2X elevado
  1X presente
  axial elevado
  harmônicos superiores
```

#### Rolamento BPFI

```text
score alto se:
  BPFI presente
  2×BPFI presente
  3×BPFI presente
  sidebands ±1X
  energia de alta frequência elevada
```

#### Oil whirl

```text
score alto se:
  pico subsíncrono
  razão f_whirl/fr entre 0,39 e 0,48
```

---

# 22. Geração parametrizada por RPM

## Entrada mínima

```yaml
machine:
  rpm: 1800

fault:
  type: "desbalanceamento"

signal:
  fs: 5000
  duration_s: 10
  fft_size: 8192
```

## Saída esperada

```yaml
rotation:
  rpm: 1800
  rotational_frequency_hz: 30.0

fault:
  type: "desbalanceamento"

peaks:
  - order_x: 1.0
    frequency_hz: 30.0
    amplitude_norm: 1.0
    peak_type: synchronous
    direction: radial

  - order_x: 2.0
    frequency_hz: 60.0
    amplitude_norm: 0.06
    peak_type: synchronous
    direction: radial

  - order_x: 3.0
    frequency_hz: 90.0
    amplitude_norm: 0.02
    peak_type: synchronous
    direction: radial
```

---

# 23. Exemplo — desalinhamento paralelo a 1800 rpm

```yaml
rotation:
  rpm: 1800
  fr_hz: 30

fault:
  type: desalinhamento_paralelo

peaks:
  - order_x: 1
    frequency_hz: 30
    amplitude_norm: 0.40

  - order_x: 2
    frequency_hz: 60
    amplitude_norm: 1.00

  - order_x: 4
    frequency_hz: 120
    amplitude_norm: 0.40

  - order_x: 6
    frequency_hz: 180
    amplitude_norm: 0.18

  - order_x: 8
    frequency_hz: 240
    amplitude_norm: 0.08
```

Os valores de amplitude acima são **exemplo de síntese**, não valores universais.

---

# 24. Exemplo — oil whirl a 3600 rpm

```yaml
rotation:
  rpm: 3600
  fr_hz: 60

fault:
  type: oil_whirl

parameters:
  whirl_ratio: 0.44

peaks:
  - order_x: 0.44
    frequency_hz: 26.4
    amplitude_norm: 1.00
    peak_type: sub_synchronous

  - order_x: 1.0
    frequency_hz: 60.0
    amplitude_norm: 0.25
    peak_type: synchronous
```

O valor `0,44X` deve variar entre amostras, por exemplo:

```text
0,40X
0,42X
0,44X
0,46X
0,48X
```

---

# 25. Exemplo — rolamento

Para calcular BPFO/BPFI/BSF/FTF é obrigatório informar a geometria.

```yaml
machine:
  rpm: 1800

bearing:
  number_of_elements: 9
  ball_diameter_mm: <valor>
  pitch_diameter_mm: <valor>
  contact_angle_deg: <valor>

fault:
  type: BPFI
```

O gerador deve calcular:

```text
fr
BPFI
2×BPFI
3×BPFI
...
```

e adicionar:

```text
BPFI ± 1X
2×BPFI ± 1X
3×BPFI ± 1X
```

Não deve inventar dimensões do rolamento a partir apenas do nome do defeito.

---

# 26. Severidade

Recomenda-se utilizar:

```text
severity ∈ [0,1]
```

com:

```text
0.0 = saudável
0.1–0.3 = incipiente
0.3–0.6 = moderada
0.6–0.8 = severa
0.8–1.0 = crítica
```

Essas faixas são **convenções de geração de dataset**, não limites normativos.

Um modelo simples:

\[
A_{fault}=A_{min}+
severity(A_{max}-A_{min})
\]

Para defeitos não lineares, como roçamento e folga, a relação entre severidade e amplitude deve poder ser não linear.

---

# 27. Resolução da FFT

A frequência de um pico depende da resolução:

\[
\Delta f=\frac{f_s}{N}
\]

onde:

- `fs` = frequência de amostragem;
- `N` = número de pontos da FFT.

O modelo não deve gerar picos infinitamente estreitos.

Para um dataset realista:

```text
pico = componente espectral + janela + leakage + ruído
```

Recomenda-se usar:

- Hann/Hanning;
- pequenas variações de amplitude;
- pequeno deslocamento de frequência;
- noise floor;
- leakage controlado.

---

# 28. Modelo de síntese recomendado

Uma FFT sintética pode ser construída como:

\[
X(f)=
\sum_i A_i P(f-f_i)
+
N(f)
\]

onde:

- `f_i` = frequência característica;
- `A_i` = amplitude;
- `P()` = forma do pico;
- `N(f)` = ruído.

Uma forma gaussiana simples:

\[
P(f-f_i)=
e^{-\frac{(f-f_i)^2}{2\sigma_i^2}}
\]

Isso produz um espectro visualmente mais realista que simplesmente colocar um valor em um único bin.

---

# 29. Regras para não gerar dados fisicamente inconsistentes

O modelo de IA **NÃO DEVE**:

1. usar `1X = RPM` em Hz;
2. esquecer a divisão por 60;
3. usar BPFO/BPFI sem geometria do rolamento;
4. tratar 2X isoladamente como prova de desalinhamento;
5. tratar qualquer pico em 1X como desbalanceamento;
6. gerar oil whirl exatamente em 0,5X sempre;
7. usar frequência fixa de rolamento independente da RPM;
8. ignorar bandas laterais;
9. ignorar a direção do sensor;
10. usar amplitudes absolutas como se fossem universais.

---

# 30. Estrutura JSON recomendada para dataset

```json
{
  "machine_id": "M001",
  "rpm": 1800,
  "rotational_frequency_hz": 30.0,
  "fault": {
    "class": "desalinhamento_paralelo",
    "severity": 0.65
  },
  "sensor": {
    "direction": "radial",
    "sampling_rate_hz": 5000,
    "fft_size": 8192
  },
  "peaks": [
    {
      "order_x": 1.0,
      "frequency_hz": 30.0,
      "amplitude_norm": 0.42,
      "type": "synchronous"
    },
    {
      "order_x": 2.0,
      "frequency_hz": 60.0,
      "amplitude_norm": 1.0,
      "type": "synchronous"
    },
    {
      "order_x": 4.0,
      "frequency_hz": 120.0,
      "amplitude_norm": 0.39,
      "type": "harmonic"
    }
  ]
}
```

---

# 31. Pseudocódigo do gerador

```python
fr = rpm / 60.0

if fault == "sem_defeito":
    peaks = [
        peak(1.0 * fr, 0.10, "synchronous"),
    ]

elif fault == "desbalanceamento":
    peaks = [
        peak(1.0 * fr, 1.00, "synchronous"),
        peak(2.0 * fr, 0.05, "harmonic"),
        peak(3.0 * fr, 0.02, "harmonic"),
    ]

elif fault == "desalinhamento_paralelo":
    peaks = [
        peak(1.0 * fr, 0.40, "synchronous"),
        peak(2.0 * fr, 1.00, "synchronous"),
        peak(4.0 * fr, 0.40, "harmonic"),
        peak(6.0 * fr, 0.18, "harmonic"),
        peak(8.0 * fr, 0.08, "harmonic"),
    ]

elif fault == "oil_whirl":
    ratio = random.uniform(0.39, 0.48)
    peaks = [
        peak(ratio * fr, 1.00, "sub_synchronous"),
        peak(1.0 * fr, 0.25, "synchronous"),
    ]

elif fault == "BPFI":
    bpfi = calculate_bpfi(...)
    peaks = []
    for k in range(1, 6):
        f0 = k * bpfi
        peaks.append(peak(f0, amplitude(k), "bearing"))

        # sidebands ±1X
        peaks.append(peak(f0 - fr, amplitude(k) * 0.20, "sideband"))
        peaks.append(peak(f0 + fr, amplitude(k) * 0.20, "sideband"))
```

---

# 32. Melhor estratégia para treinamento de IA

Para classificação robusta, não produzir somente um espectro perfeito para cada defeito.

Gerar, por classe:

```text
1000+ espectros
```

com variação de:

```text
RPM
severity
noise
sensor_position
load
harmonic_amplitude
frequency_resolution
bearing_geometry
coupling_type
critical_speed
```

A mesma falha deve gerar várias assinaturas diferentes.

Isso evita que a IA simplesmente memorize:

```text
2X = desalinhamento
1X = desbalanceamento
0,45X = oil whirl
```

e favorece o aprendizado da **assinatura espectral completa**.

---

# 33. Hierarquia de diagnóstico recomendada

O classificador deve analisar:

### Nível 1 — síncrono

```text
0,5X
1X
1,5X
2X
3X
4X...
```

### Nível 2 — subsíncrono/supersíncrono

```text
<1X
>1X
```

### Nível 3 — harmônicos

```text
2X, 3X, 4X, ...
```

### Nível 4 — famílias de frequência

```text
BPFO
BPFI
BSF
FTF
```

### Nível 5 — bandas laterais

```text
f ± 1X
f ± FTF
```

### Nível 6 — direção

```text
radial
axial
tangencial
```

### Nível 7 — evolução com RPM

Uma assinatura confiável deve acompanhar a mudança de RPM.

---

# 34. Referências técnicas

**[1]** Scientific Reports, *A hybrid VMD-CNN-autoencoder approach for speed-invariant fault detection of parallel and angular misalignment in rotating machinery*, 2026.

**[2]** Muszynska, A. *Vibrational Diagnostics of Rotating Machinery Malfunctions*. International Journal of Rotating Machinery, 1995.

**[3]** Desouki et al. *Dynamic Response of a Rotating Assembly under the Coupled Effects of Misalignment and Imbalance*. Shock and Vibration, 2020.

**[4]** Scientific Reports, *A hybrid VMD-CNN-autoencoder approach for speed-invariant fault detection of parallel and angular misalignment in rotating machinery*, 2026.

**[5]** *Effect of partial rotor-to-stator rub on shaft vibration*. Journal of the Korean Society for Precision Engineering / KCI.

**[6]** *Vibration response of a cracked rotor in presence of rotor–stator rub*. Journal of Sound and Vibration.

**[7]** SKF, *Vibration – Spectral Analysis*, material técnico sobre frequências de defeito de rolamentos.

**[8]** Randall, R. B.; Antoni, J. *Rolling element bearing diagnostics—A tutorial*. Mechanical Systems and Signal Processing, 2011.

**[9]** Tandon; Choudhury. *A review of vibration and acoustic measurement methods for the detection of defects in rolling element bearings*. Tribology International, 1999.

**[10]** Singh, S.; Howard, C. Q.; Hansen, C. H. *An extensive review of vibration modelling of rolling element bearings with localised and extended defects*. Journal of Sound and Vibration, 2015.

**[11]** Fluke, *Mechanical Looseness: What It Is and How to Detect It*.

**[12]** *Spectrum Analysis of Machinery Vibration Problems*, material técnico de análise espectral.

**[13]** Sekhar, A. S.; Prabhu, B. S. *Effects of coupling misalignment on vibrations of rotating machinery*. Journal of Sound and Vibration.

**[14]** Turbomachinery Magazine, *Back to Basics: Fluid Induced Instability — Oil Whirl/Oil Whip*.

**[15]** ScienceDirect Topics, *Oil Whirl*.

**[16]** Jiang, J. *The Analytical Solution and The Existence Condition of Dry Friction Backward Whirl in Rotor-to-Stator Contact Systems*. Journal of Vibration and Acoustics, 2007.

**[17]** Jiang, J.; Shang, Z.; Hong, L. *Characteristics of dry friction backward whirl — A self-excited oscillation in rotor-to-stator contact systems*. Science China Technological Sciences, 2010.

**[18]** Li et al. *Analysis of the dry whirl and dry whip response in a vertical active magnetic bearing drop test rig*. Journal of Sound and Vibration, 2023.

---

# 35. URLs/DOIs das principais fontes

- Muszynska, 1995: DOI `10.1155/S1023621X95000108`
- Randall & Antoni, 2011: DOI `10.1016/j.ymssp.2010.07.017`
- Singh, Howard & Hansen, 2015: DOI `10.1016/j.jsv.2015.04.037`
- Sekhar & Prabhu, 1995: DOI `10.1006/jsvi.1995.0407`
- Jiang, 2007: DOI `10.1115/1.2345677`
- Jiang, Shang & Hong, 2010: DOI `10.1007/s11431-010-0075-7`
- Li et al., 2023: DOI `10.1016/j.jsv.2023.117579`

---

# 36. Regra final para o agente de IA

Ao receber:

```text
RPM + DEFEITO
```

o agente deve:

```text
1. calcular fr = RPM / 60

2. selecionar a assinatura do defeito

3. calcular todas as frequências em função de fr

4. se for rolamento:
      exigir geometria
      calcular BPFO/BPFI/BSF/FTF

5. se for oil whirl:
      selecionar razão entre 0,39X e 0,48X

6. se for friction whirl:
      NÃO assumir razão fixa
      utilizar critical_speed/modelo rotodinâmico quando disponível

7. gerar harmônicos e sidebands apropriados

8. aplicar severidade

9. aplicar ruído e variação estocástica

10. retornar:
      frequência
      ordem
      amplitude
      tipo
      direção
      confiança

11. nunca afirmar que um único pico constitui diagnóstico definitivo.
```

## Princípio fundamental

> **A IA deve reproduzir uma assinatura espectral plausível, e não uma FFT determinística universal.**

A frequência é fortemente determinada pela cinemática e geometria; a amplitude e a distribuição das linhas espectrais dependem do sistema dinâmico real.
