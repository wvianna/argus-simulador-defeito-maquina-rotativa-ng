# CONVENTIONS.md — Convenções de código do Argus

## Back-end (Python)

- Estilo: PEP 8, aplicado via `ruff format` (substituto do `black`) e `ruff check` para lint.
- Type-checking: `mypy` em modo estrito para os módulos `signal_generator`, `fft_processor` e `discard_engine` (lógica crítica de negócio).
- Nomenclatura: módulos e funções em `snake_case`; classes em `PascalCase`; constantes em `UPPER_SNAKE_CASE`.
- Estrutura sugerida:
  ```text
  backend/
    app/
      api/            # rotas FastAPI
      domain/          # signal_generator, fft_processor, discard_engine (lógica pura, sem I/O)
      persistence/     # modelos SQLAlchemy, repositórios
      config.py        # leitura de variáveis de ambiente (tolerâncias, conexão DB)
    tests/
      unit/
      integration/
    alembic/
  ```
- Lógica de negócio pura (geração de sinal, FFT, decisão de descarte) deve ficar isolada de I/O (banco de dados, rede), recebendo dependências injetadas para permitir teste unitário sem banco real.
- Toda função pública que implemente um requisito deve citar o ID (`FR-###`/`NFR-###`) em um comentário de uma linha ou no nome do teste correspondente, para rastreabilidade.

## Front-end (React/TypeScript)

- Componentes em `PascalCase`, hooks em `useCamelCase`, arquivos de componente `NomeComponente.tsx`.
- Lint/format: ESLint + Prettier, configuração compartilhada no `package.json` raiz do front-end.
- Estrutura sugerida:
  ```text
  frontend/
    src/
      components/      # PainelSimulacao, GraficoFFT, ChecklistValidacao
      api/             # client HTTP tipado para a API do back-end
      types/           # tipos compartilhados (espelham os schemas da API)
    tests/
  ```
- Chamadas à API devem usar tipos gerados/derivados do contrato documentado em `design.md` (evitar `any`).

## Commits e branches

- Commits atômicos por tarefa `T-###`; mensagem no formato `T-###: <resumo curto do que mudou>`.
- Não misturar refatoração não relacionada com a tarefa em andamento.
- Não fazer commit automaticamente — apenas quando solicitado explicitamente pelo usuário.

## Documentação

- Toda mudança de comportamento observável exige atualização de `SPECIFICATION.md` e, se aplicável, `design.md`/`tasks.md` na mesma tarefa (Princípio 11 da skill `sdd-software`).
- `README.md` deve permanecer a única porta de entrada para instalar, configurar, buildar, testar e executar o projeto.
