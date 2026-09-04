# HANDOFF.md — Transferência de contexto entre agentes

_Registrado em: 2026-09-04._

## Contexto

O usuário pediu a criação da especificação (`SPECIFICATION.md`) a partir de `docs/descricao.txt` e, em seguida, pediu a criação de `design.md`, `tasks.md` e demais documentos necessários para que agentes de IA possam implementar o sistema. O usuário não estava disponível para responder às perguntas bloqueadoras da especificação e autorizou explicitamente o agente a "trabalhar de forma autônoma e tomar boas decisões".

## Estado atual

- Especificação, constituição, roadmap, documentação de codebase, design e tarefas do MVP estão completos (ver `STATUS.md` para a lista detalhada de arquivos).
- Nenhum código de aplicação foi escrito. `backend/`, `frontend/` e `docker-compose.yml` ainda não existem.

## Alterações realizadas nesta sessão

- Criados: `SPECIFICATION.md`, `LICENSE`, `.gitignore`, `README.md`, `AGENTS.md`, `STATUS.md`, `HANDOFF.md`, `.specs/project/constitution.md`, `.specs/project/ROADMAP.md`, `.specs/codebase/STACK.md`, `.specs/codebase/ARCHITECTURE.md`, `.specs/codebase/CONVENTIONS.md`, `.specs/codebase/TESTING.md`, `.specs/features/simulador-vibracao/design.md`, `.specs/features/simulador-vibracao/tasks.md`, `.specs/features/simulador-vibracao/context.md`.

## Decisões tomadas (sem confirmação humana ainda)

Todas registradas com justificativa em `.specs/features/simulador-vibracao/context.md`:

1. Back-end: Python 3.12 + FastAPI.
2. Front-end: React 18 + Vite + TypeScript + Recharts.
3. Banco de dados: PostgreSQL 16.
4. Persistência do "trash": física, em tabela separada.
5. Autenticação: nenhuma nesta fase (uso local/interno).
6. Tolerâncias do Paralelepípedo de Descarte e desvio de rotação: configuráveis via variáveis de ambiente/arquivo de configuração, sem valor numérico fixo no código.
7. Ambiente-alvo inicial: local via Docker Compose, sem CI nem staging/produção definidos.

## Problemas

- Nenhum problema técnico. O único risco é a ausência de confirmação humana das decisões acima — se o responsável pelo projeto discordar de alguma, `SPECIFICATION.md`, `constitution.md`, `STACK.md` e `context.md` precisam ser atualizados antes de prosseguir com a implementação baseada neles.

## Testes

- Nenhum executado (não há código).

## Pendências

- Implementar `T-001` em diante (`.specs/features/simulador-vibracao/tasks.md`).
- Confirmar (ou revisar) as decisões técnicas listadas acima com o responsável pelo projeto.
- Configurar CI quando houver decisão sobre o ambiente de validação contínua.

## Próximo passo

Começar pela Fase 1 do roadmap: schema de banco de dados e módulo de geração de sinal (`T-001` e `T-002`), seguindo `design.md` e o gate de testes definido em `TESTING.md`.

## Cuidados

- Não alterar o algoritmo de descarte (regra de ouro + Paralelepípedo `R^3`) sem atualizar `SPECIFICATION.md` (`FR-007`–`FR-010`) e `design.md` na mesma tarefa.
- Não iniciar tarefas fora de ordem: `tasks.md` define dependências explícitas (`Depende de`).
- Manter a documentação atualizada a cada tarefa concluída (Princípio 11 da skill `sdd-software`).

## Critério de conclusão

Este handoff é considerado resolvido quando as decisões autônomas listadas acima forem confirmadas (ou revisadas) pelo responsável pelo projeto e a Fase 1 do roadmap estiver implementada com o gate mínimo de testes aprovado.
