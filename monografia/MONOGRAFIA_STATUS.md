# MONOGRAFIA — STATUS

_Última atualização: 2026-09-04 (draft compilado)._

## Estado geral

- [x] Auditoria do workspace (fontes primárias mapeadas)
- [x] Plano, evidências, rastreabilidade e pendências criados
- [x] Estrutura LaTeX modular criada (`monografia/`)
- [x] Capítulos redigidos (Introdução a Conclusão + apêndices)
- [x] Compilação PDF validada (`pdflatex` + `bibtex` → `main.pdf`, ~54 páginas)
- [x] Diagramas TikZ e figuras reais inseridos e renderizados
- [x] Listas (figuras/tabelas/sumário) e referências cruzadas OK (0 undefined)
- [ ] Revisão em camadas com o orientador (conteúdo/engenharia/evidências/ABNT)
- [ ] Metadados institucionais e pendências resolvidas

## Estágio atual

**Draft técnico completo e compilável entregue** (`main.pdf`, 54 páginas).
Usuário indisponível nesta sessão → decisões provisórias registradas em
`MONOGRAFIA_PLANO.md` e `MONOGRAFIA_PENDENCIAS.md`.

## Decisões provisórias (rever com o autor/orientador)

1. Classe LaTeX: `memoir` com formatação ABNT customizada (abntex2 não instalado
   no ambiente). Migrar se o modelo institucional exigir.
2. Citações numéricas (`plain`); blocos de código em `verbatim`.
3. Metadados: autor William da Silva Vianna; instituição/curso provisórios
   (IFF — Eng. de Controle e Automação); orientador pendente.
4. Figuras de resultado: capturas reais do dashboard (não fabricadas).
5. Dados de resultado (cap. 6): contagens reais de testes (63/12) e capturas
   reais via API (decisões de descarte e picos de rolamento BPFI).

## Extensão

- `main.pdf` ≈ 54 páginas (inclui pré-textuais, referências e apêndices).
- Meta de planejamento da skill: 65–100 páginas. Expansão futura deve ser por
  conteúdo acadêmico necessário (aprofundar fundamentação/trabalhos
  relacionados/discussão) sob orientação — ver `MONOGRAFIA_PENDENCIAS.md`.

## Próximo passo

1. Revisão humana (orientador): conteúdo, evidências, referências e ABNT.
2. Preencher metadados (instituição, orientador, cidade, título).
3. Decidir modelo institucional (abntex2?) e aplicá-lo se necessário.
4. Expandir capítulos conforme orientação e recompilar.
