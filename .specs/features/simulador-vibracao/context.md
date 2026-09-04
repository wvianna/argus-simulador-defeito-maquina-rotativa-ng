# context.md — Decisões técnicas (simulador-vibracao)

> Registradas em 2026-09-04. Todas as decisões abaixo foram tomadas de forma autônoma porque o usuário respondeu indisponível ("Work autonomously and make good decisions") às perguntas bloqueadoras levantadas em `SPECIFICATION.md`. **Revise antes de considerar definitivas.**

## Decisões

| Pergunta bloqueadora original (`SPECIFICATION.md`) | Decisão tomada | Justificativa |
|---|---|---|
| Qual stack tecnológico? | Back-end: Python 3.12 + FastAPI. Front-end: React 18 + Vite + TypeScript. Banco: PostgreSQL 16. | Python tem ecossistema maduro para FFT/processamento de sinal (NumPy/SciPy), reduzindo risco de reimplementar matemática de sinal manualmente. FastAPI gera contrato OpenAPI automaticamente, útil para rastreabilidade de contrato (`FR-014` tabela de interface). React é o padrão mais comum para SPA com gráficos interativos (Recharts). PostgreSQL suporta `JSONB` para os vetores `R^3`, atendendo a `NFR-003` sem exigir banco especializado. |
| Quais tolerâncias padrão do Paralelepípedo de Descarte e do desvio de rotação? | Não fixar valores numéricos; tornar configurável via variável de ambiente/arquivo de configuração, sem default codificado. | Os documentos de origem não fornecem valores numéricos de referência; fixar um número arbitrário violaria o Princípio 3 da skill `sdd-software` ("não invente detalhes técnicos"). Tornar configurável permite calibração posterior sem alterar código. |
| O "trash" deve ser persistido fisicamente ou é só métrica? | Persistir fisicamente em tabela separada (`leituras_trash`). | A documentação de origem (`docs/criterioArmazenamento.txt`) descreve o "trash" como parte do fluxo de simulação, útil para auditar a taxa de descarte e validar o algoritmo durante testes; persistência física permite essa auditoria sem custo relevante no MVP. |
| Há requisito de autenticação? | Nenhuma autenticação nesta fase; uso local/interno. | Não há indicação de exposição pública do sistema nos documentos de origem; o sistema é descrito como ferramenta de simulação/treinamento. Autenticação pode ser adicionada na Fase 5 (hardening) se o ambiente-alvo mudar. |
| Qual volume esperado de simulações concorrentes? | Não definido; tratado como `NFR-005` em aberto no roadmap (Fase 5). | Sem indicação de volume nos documentos de origem; adicionar meta numérica seria inventar dado não fornecido. |

## Impacto nas decisões acima

- `constitution.md`, `STACK.md`, `ARCHITECTURE.md` e `README.md` foram escritos assumindo estas decisões.
- Se o responsável pelo projeto trocar a stack (ex.: preferir Node.js no back-end), os arquivos citados acima e `design.md`/`tasks.md` precisam ser revisados antes de continuar a implementação — não apenas este arquivo.

## Como revisar

1. Ler esta tabela e confirmar ou substituir cada decisão.
2. Atualizar `SPECIFICATION.md` (seção "Perguntas bloqueadoras") removendo as perguntas respondidas.
3. Atualizar `STATUS.md` registrando a confirmação.
4. Se alguma decisão mudar, atualizar `constitution.md`, `STACK.md`, `ARCHITECTURE.md`, `design.md` e `tasks.md` na mesma tarefa.
