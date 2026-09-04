# MONOGRAFIA — PLANO

## Identificação

- **Título provisório**: ARGUS — Simulador de defeitos em máquinas rotativas: geração de sinais vibracionais sintéticos com análise espectral FFT e persistência seletiva para treinamento e pesquisa de diagnóstico de vibração
- **Curso**: Engenharia de Controle e Automação — `[VALIDAR COM O AUTOR]`
- **Instituição**: Instituto Federal Fluminense (IFF) — `[VALIDAR COM O AUTOR]`
- **Autor**: William da Silva Vianna
- **Orientador**: `[ORIENTADOR — NÃO INFORMADO]`

## Problema

Em monitoramento de condição de máquinas rotativas, a aquisição contínua de vibração gera volume massivo de dados brutos no domínio do tempo, cujo armazenamento indiscriminado torna-se passivo financeiro e operacional. Ao mesmo tempo, o treinamento de analistas e de algoritmos de IA em diagnóstico requer sinais de defeitos variados, o que é inviável em ativos reais (risco e indisponibilidade). Há, portanto, dois problemas interligados: (i) como reduzir o volume persistido sem perder capacidade diagnóstica (persistência seletiva), e (ii) como gerar sinais sintéticos tecnicamente válidos que reproduzam assinaturas espectrais de defeitos para treinamento sem expor ativos reais.

## Justificativa

- Redução do "storage liability" na manutenção preditiva (fontes primárias: `docs/criterioArmazenamento.txt`, `docs/descricao.txt`).
- Emulação de falhas para teste de algoritmos e treinamento de analistas (fonte primária: `docs/descricao.txt`).
- Evidência de implementação real disponível no workspace (código, testes, E2E, capturas).

## Objetivo geral

Projetar e implementar um simulador de defeitos em máquina rotativa que gere sinais vibracionais sintéticos com assinatura espectral parametrizável por tipo de defeito e que aplique persistência seletiva de leituras (regra de ouro + Paralelepípedo de Descarte R³), com interface web para análise e registro de snapshots de defeito.

## Objetivos específicos

1. Modelar e implementar a geração de sinais sintéticos cujas componentes espectrais (ordens, harmônicos, sub-harmônicos, frequências de rolamento) reproduzam o catálogo de defeitos de máquinas rotativas.
2. Implementar o processamento espectral (FFT) com extração de picos R³ (frequência, amplitude, fase), RMS total/ruído/picos, valor DC e limiar configurável de picos.
3. Implementar o motor de descarte (regra de ouro + Paralelepípedo de Descarte R³) e a persistência seletiva com hierarquia Planta→Área→Máquina→Ponto e armazenamento "trash".
4. Expor API REST e interface web com painel de sinal, gráfico FFT (com ordens N e rotação em Hz), indicadores de processamento/descarte e snapshot de defeito.
5. Validar por testes automatizados (unitário/integração/contrato) e de ponta a ponta as assinaturas espectrais e o fluxo de descarte.

## Delimitação

- Ambiente-alvo local (Docker Compose); sem autenticação nem produção (`NFR-005`/`NFR-006` em aberto).
- Sinais sintéticos (não medição real); rolamentos com geometria padrão.
- MVP: processamento síncrono por requisição; sem filas/lote.

## Estrutura planejada

1. Introdução
2. Fundamentação teórica
3. Trabalhos relacionados
4. Materiais e métodos
5. Desenvolvimento (arquitetura e implementação)
6. Experimentos e resultados
7. Discussão
8. Conclusão
- Referências
- Apêndices (contratos, exemplos de execução)

## Meta de extensão

Draft substantivo alinhado à faixa de 65–100 páginas de planejamento da skill; sem preenchimento artificial. Expansões futuras devem ser por conteúdo acadêmico necessário.

## LaTeX

- **Classe/modelo institucional**: `memoir` com preâmbulo ABNT customizado (abntex2 não disponível no ambiente). Instituição a validar — usar abntex2 se o modelo institucional exigir.
- **Compilador**: `pdflatex`
- **Ferramenta de compilação**: `pdflatex` + `bibtex` (sem `latexmk` no ambiente) — sequência documentada em `latexmkrc`.

## Pendências

- Orientador e confirmação de curso/instituição.
- Modelo institucional (abntex2?) e manual da instituição.
- Verificação/edição vigente das normas ABNT citadas.
- Consolidação da lista de referências por fonte acadêmica verificável.
