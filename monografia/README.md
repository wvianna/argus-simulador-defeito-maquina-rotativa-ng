# Monografia (LaTeX/ABNT) — projeto ARGUS

Projeto LaTeX da monografia de conclusão de curso sobre o simulador ARGUS
(geração de sinais vibracionais sintéticos, análise espectral FFT e
persistência seletiva \(R^3\)).

## Estrutura

```text
monografia/
├── main.tex                 # documento principal (memoir + formatação ABNT)
├── latexmkrc                # documenta a sequência de compilação
├── references.bib           # bibliografia
├── chapters/                # capítulos 1 a 8
├── pretextual/              # capa, folha de rosto, resumo, abstract
├── figures/                 # capturas reais do dashboard (docs/image)
├── diagrams/                # diagramas TikZ (arquitetura, fluxo, estados)
├── appendices/              # contratos de API e exemplos de execução
├── MONOGRAFIA_PLANO.md
├── MONOGRAFIA_EVIDENCIAS.md
├── MONOGRAFIA_RASTREABILIDADE.md
├── MONOGRAFIA_PENDENCIAS.md
└── MONOGRAFIA_STATUS.md
```

## Compilação

Sem `latexmk` no ambiente, compilar na pasta `monografia/`:

```bash
pdflatex -interaction=nonstopmode -halt-on-error main.tex
bibtex main
pdflatex -interaction=nonstopmode -halt-on-error main.tex
pdflatex -interaction=nonstopmode -halt-on-error main.tex
```

Com `latexmk` disponível:

```bash
latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex
```

Resultado atual: `main.pdf` (~54 páginas).

## Decisões de formatação (rever com a instituição)

- Classe `memoir` com formatação ABNT customizada (abntex2 não disponível no
  ambiente). Se a instituição exigir abntex2/modelo próprio, migrar o
  `main.tex`.
- Citações numéricas (estilo `plain`), ordenadas alfabeticamente. Sistema
  autor-data (abntex2cite) é alternativa a avaliar.
- Blocos de código em `verbatim` (robustez de compilação).
- Metadados (instituição/curso/orientador/cidade) ainda são marcadores
  `[a validar]` — ver `MONOGRAFIA_PENDENCIAS.md`.
