# GraphQL vs REST: Experimento Controlado

## Contexto e Motivação

A linguagem de consulta GraphQL, desenvolvida pelo Facebook, representa uma alternativa às tradicionais APIs REST. Enquanto GraphQL permite consultas flexíveis baseadas em schemas de grafos, REST utiliza endpoints pré-definidos para operações específicas. Apesar da crescente adoção do GraphQL, os benefícios quantitativos em relação ao REST ainda não estão claramente estabelecidos.

Este experimento visa avaliar empiricamente as diferenças de performance entre GraphQL e REST, fornecendo dados objetivos para decisões arquiteturais.

## Perguntas de Pesquisa e Hipóteses

### RQ1. Respostas às consultas GraphQL são mais rápidas que respostas às consultas REST?

**Justificativa**: GraphQL pode reduzir o número de requisições necessárias através de consultas aninhadas, potencialmente diminuindo a latência total.

- **H0 (nula)**: Não há diferença significativa no tempo de resposta entre consultas GraphQL e REST
- **H1 (alternativa)**: GraphQL apresenta tempos de resposta significativamente diferentes de REST

### RQ2. Respostas às consultas GraphQL têm tamanho menor que respostas às consultas REST?

**Justificativa**: GraphQL permite seleção específica de campos, evitando over-fetching comum em APIs REST.

- **H0 (nula)**: Não há diferença significativa no tamanho das respostas entre GraphQL e REST
- **H1 (alternativa)**: GraphQL produz respostas com tamanho significativamente diferente de REST

## Desenho Experimental

### Variáveis Dependentes (VD)

- **Tempo de resposta**: latência em milissegundos desde o envio até o recebimento completo
- **Tamanho da resposta**: bytes do payload JSON (sem headers HTTP)
- **Throughput**: requisições por segundo sob carga (métrica secundária)

### Variáveis Independentes (VI)

- **Tipo de API**: GraphQL vs REST (variável principal)
- **Complexidade da consulta**: 
  - Simples: busca direta de entidade
  - Nested: consulta com relacionamentos (1-2 níveis)
  - Agregada: múltiplas entidades com filtros
- **Carga concorrente**: 1, 10, 50 clientes simultâneos
- **Estado do cache**: cold (primeira execução) vs warm (cache aquecido)
- **Seletividade**: quantidade de campos solicitados (25%, 50%, 100% dos disponíveis)

### Tratamentos Experimentais

O experimento seguirá um design fatorial 2×3×3×2, totalizando 36 combinações:

**Exemplos de tratamentos principais**:
- **T1-T2**: REST vs GraphQL — consulta simples — 1 cliente — cold cache
- **T7-T8**: REST vs GraphQL — consulta nested — 10 clientes — warm cache  
- **T17-T18**: REST vs GraphQL — consulta agregada — 50 clientes — warm cache

**Estratégia de execução**:
- Cada par REST/GraphQL será executado sequencialmente
- Ordem randomizada para evitar efeitos de aprendizado
- Intervalo de 30s entre tratamentos para estabilização

### Objetos Experimentais

**APIs testadas**:
- **GitHub REST API v4**: endpoints oficiais para repositórios, usuários e issues
- **GitHub GraphQL API v4**: schema oficial equivalente aos endpoints REST
- **Autenticação**: tokens pessoais para ambas as APIs

**Cenários de consulta**:
- **Simples**: busca de repositório por nome
- **Nested**: repositório com issues e comentários
- **Agregada**: múltiplos repositórios com estatísticas

**Ferramentas de implementação**:
- **Node.js**: runtime para execução dos scripts
- **Axios**: cliente HTTP para requisições REST
- **GraphQL-request**: cliente para consultas GraphQL
- **fs-extra**: manipulação de arquivos CSV

**Coleta de dados**:
- **Formato de saída**: arquivos CSV com timestamp, tipo_api, tempo_resposta, tamanho_payload
- **Estrutura**: `results/experiment_YYYYMMDD_HHMMSS.csv`
- **Campos**: timestamp, api_type, query_type, response_time_ms, payload_size_bytes, status_code

**Ambiente de execução**:
- **Local**: máquina de desenvolvimento para controle de variáveis
- **Rate limiting**: respeitando limites da API do GitHub (5000 req/h)
- **Monitoramento**: logs detalhados de cada requisição

### Tipo de Projeto Experimental

**Design within-subjects**: cada combinação de fatores é testada em ambas as APIs (REST e GraphQL) no mesmo ambiente, permitindo comparação direta e reduzindo variabilidade entre sujeitos.

**Controles experimentais**:
- **Contrabalanceamento**: ordem de execução REST/GraphQL alternada
- **Randomização**: sequência de tratamentos embaralhada
- **Isolamento**: reinicialização de containers entre sessões

### Plano de Medições

**Repetições por tratamento**: 50 medições para garantir poder estatístico adequado (α=0.05, β=0.20)

**Protocolo de execução**:
- **Warm-up**: 15 requisições de aquecimento (descartadas)
- **Coleta**: 50 medições válidas por combinação
- **Intervalo**: 100ms entre requisições individuais
- **Timeout**: 30s por requisição (falhas registradas)

**Volume total estimado**: 1.800 medições válidas
- 18 combinações × 2 APIs × 50 repetições = 1.800 pontos de dados
- Tempo estimado: 4-6 horas de execução (respeitando rate limits)

**Critérios de qualidade**:
- Taxa de sucesso mínima: 95% por tratamento
- Coeficiente de variação máximo: 30% por grupo

### Ameaças à Validade e Mitigações

#### Validade Interna
**Ameaças identificadas**:
- Variações de performance do sistema (CPU, GC, I/O)
- Efeitos de ordem e aprendizado entre execuções
- Interferência de processos concorrentes

**Estratégias de mitigação**:
- Containers isolados com recursos limitados
- Monitoramento contínuo de CPU/memória
- Randomização da ordem de execução
- Execução em horários controlados

#### Validade Externa
**Limitações reconhecidas**:
- Implementações específicas (Node.js/Express vs Apollo)
- Dataset sintético pode não refletir uso real
- Ambiente localhost não representa produção

**Abordagens para generalização**:
- Documentação detalhada das implementações
- Dataset baseado em padrões reais de uso
- Discussão explícita das limitações nos resultados

#### Validade de Construto
**Questões de medição**:
- Tempo total vs tempo de processamento puro
- Tamanho bruto vs tamanho útil da informação
- Métricas de throughput sob diferentes cargas

**Refinamentos metodológicos**:
- Medição em múltiplos pontos (cliente, servidor, banco)
- Desabilitação de compressão HTTP
- Análise separada de overhead de protocolo

#### Validade de Conclusão Estatística
**Riscos aos resultados**:
- Outliers por falhas de rede ou sistema
- Distribuições não-normais dos tempos de resposta
- Correlações temporais entre medições

**Tratamento estatístico**:
- Detecção automática de outliers (IQR method)
- Testes não-paramétricos quando apropriado
- Análise de séries temporais para autocorrelação

## Cronograma de Execução

### Sprint 1: Preparação (Semana 1)
- Desenvolvimento dos scripts de medição em Node.js
- Configuração de autenticação com GitHub API
- Implementação das consultas REST e GraphQL
- Testes iniciais e validação do setup

### Sprint 2: Execução e Análise (Semana 2)
- Execução do experimento completo
- Coleta de dados em arquivos CSV
- Análise estatística dos resultados
- Elaboração do relatório técnico

### Sprint 3: Visualização (Semana 3)
- Desenvolvimento do dashboard com os dados coletados
- Criação de gráficos e tabelas explicativas
- Documentação final e apresentação dos resultados

## Análise Estatística Planejada

**Testes primários**:
- ANOVA de medidas repetidas para comparar médias
- Teste de Wilcoxon para dados não-paramétricos
- Análise de tamanho de efeito (Cohen's d)

**Análises exploratórias**:
- Correlação entre complexidade e diferença de performance
- Impacto da carga na vantagem relativa
- Análise de regressão para fatores preditivos

**Critérios de significância**:
- Nível α = 0.05 para testes de hipótese
- Tamanho de efeito mínimo relevante: d = 0.3
- Intervalos de confiança de 95% para estimativas

---

**Laboratório de Experimentação de Software - UFLA**  
*Prof. João Paulo Carneiro Aramuni*  
*Engenharia de Software - 6º Período*