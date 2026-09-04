# MONOGRAFIA — STATUS

_Última atualização: 2026-09-04._

## Estado geral

- [x] Auditoria do workspace (fontes primárias mapeadas)
- [x] Plano, evidências, rastreabilidade e pendências criados
- [x] Estrutura LaTeX modular criada (`monografia/`)
- [x] Capítulos redigidos (draft do núcleo técnico)
- [ ] Compilação PDF validada (pdflatex + bibtex)
- [ ] Revisão em camadas (conteúdo/engenharia/evidências/ABNT)
- [ ] Revisão humana (orientador) e metadados institucionais

## Estágio atual

Escrita do draft técnico e preparação para compilação. Usuário indisponível nesta sessão → decisões provisórias registradas em `MONOGRAFIA_PLANO.md` e `MONOGRAFIA_PENDENCIAS.md`.

## Decisões provisórias (revisar com o autor)

1. Classe LaTeX: `memoir` com preâmbulo ABNT (abntex2 não instalado no ambiente). Migrar se o modelo institucional exigir.
2. Compilação: `pdflatex` + `bibtex`.
3. Metadados: autor William da Silva Vianna; instituição/curso provisórios (IFF — Eng. de Controle e Automação); orientador pendente.
4. Figuras de resultado: capturas reais do dashboard (não fabricadas).

## Próximo passo

1. Compilar `main.tex` e corrigir erros.
2. Inspecionar o PDF.
3. Revisão por camadas e preenchimento das pendências com o autor.
