# Relatório Técnico: GraphQL vs Rest

## 1. Informações do grupo

- Curso: Engenharia de Software
- Disciplina: Laboratório de Experimentação de Software
- Período: 6° Período
- Professor(a): Prof. Dr. João Paulo Carneiro Aramuni
- Membros do Grupo: Ana Luiza Machado Alves, Lucas Henrique Chaves Barros, Raquel de Almeida Calazans

---

## 2. Introdução

Este relatório apresenta um experimento controlado comparando desempenho entre GraphQL e REST na API do GitHub. O objetivo é avaliar tempos de resposta e tamanho de payload sob diferentes condições de cache e carga concorrente, seguindo um desenho experimental fatorial e balanceado.

### 2.1. Questões de Pesquisa (Research Questions – RQs)

As questões de pesquisa foram definidas para guiar a investigação e estruturar a análise dos dados coletados:

Questões de Pesquisa (RQs):

| RQ   | Pergunta                                                    |
| ---- | ----------------------------------------------------------- |
| RQ01 | Respostas GraphQL são mais rápidas que REST?                |
| RQ02 | Respostas GraphQL têm tamanho de payload menor do que REST? |

### 2.2. Hipóteses

Hipóteses formais para cada RQ:

- H₀ (RQ1): Não há diferença significativa nos tempos de resposta entre GraphQL e REST.
- H₁ (RQ1): GraphQL apresenta tempos de resposta significativamente menores do que REST.

- H₀ (RQ2): Não há diferença significativa no tamanho dos payloads entre GraphQL e REST.
- H₁ (RQ2): GraphQL apresenta payloads significativamente menores do que REST.

Observações: Hipóteses focadas em desempenho de API, não em maturidade de repositórios.

### 2.3 Variáveis

- Independentes: `api_type` (REST, GraphQL), `query_type` (simple, nested, aggregated), `cache_state` (cold, warm), `concurrent_clients` (níveis de carga).
- Dependentes: `response_time_ms`, `payload_size_bytes`.

### 2.4 Tratamentos

- Comparação REST vs GraphQL.
- Cache ligado (warm) vs desligado (cold).
- Níveis de carga: valores de `concurrent_clients`.

### 2.5 Objetos experimentais

- REST: `simple`, `nested`, `aggregated` conforme endpoints.
- GraphQL: queries equivalentes conforme definidas.

### Tipo de projeto experimental

Fatorial completo e balanceado, entre-sujeitos, com medições repetidas por cliente em cada tratamento.

### Quantidade de medições (N)

`config['experiment']['repetitions']` por cliente. Para estabilidade em testes não-paramétricos, valores típicos N≥50 por condição.

### Ameaças à validade

- Conclusão: viés de implementação; interpretação sem tamanho de efeito.
- Interna: variação de rede/latência; caching em camadas não controladas.
- Externa: generalização limitada além do GitHub API.
- Estatística: não-normalidade; outliers; heterocedasticidade sob alta concorrência.

---

## 3. Tecnologias e ferramentas utilizadas

- Linguagem de Programação: Python
- Bibliotecas: requests, gql, pandas, scipy, matplotlib, seaborn
- APIs utilizadas: GitHub GraphQL API, GitHub REST API
- Estrutura geral de dados coletados (CSV):
  `timestamp, api_type, query_type, concurrent_clients, cache_state, response_time_ms, payload_size_bytes, status_code`.

---

## 4. Arquitetura e Organização

- `src/`
  - `main.py`: orquestra o fluxo (coleta → análise → gráficos) com logs.
  - `design.py` e `design_snapshot.md`: desenho experimental e snapshot.
  - `configs/`: configuração (`config.py`), consultas (`queries.py`), clientes (`clients.py`), geradores de requisição (`request_generators.py`).
- `collectors/`
  - `collector.py`: executa tratamentos concorrentes e grava CSV incremental.
- `analyzers/`
  - `analyze_results.py`: análise estatística e geração de gráficos; escreve `analysis_report.md` e imagens.
- `results/`: arquivos CSV por execução, análises e gráficos.
- `logs/`: `pipeline.log` (orquestração) e `experiment.log` (coleta).

---

## 5. Configuração de Ambiente

Ambiente recomendado para Windows (shell `bash.exe`):

- Pré-requisitos: Python 3.11+, um `GITHUB_TOKEN` válido.
- Criar ambiente virtual e instalar dependências:

```bash
python -m venv .venv
"$PWD/.venv/Scripts/python.exe" -m pip install -r src/requirements.txt
```

- Configurar variável de ambiente do GitHub:
  - Crie/edite `.env` na raiz com:

```
GITHUB_TOKEN=seu_token_aqui
```

- Opcional: verificar versão do Python usada pelo venv:

```bash
"$PWD/.venv/Scripts/python.exe" --version
```

Observações:

- Respeite o rate limit do GitHub (~5000 req/h por token).
- Ajuste parâmetros em `src/configs/config.py` (repetições, concorrência, cache).

---

## 5. Setup e Execução

- Pipeline completa (coleta → análise → gráficos):

```bash
"$PWD/.venv/Scripts/python.exe" -m src.main
```

- Apenas análise/gráficos (a partir de CSV existente em `results/`):

```bash
"$PWD/.venv/Scripts/python.exe" -m src.analyzers.analyze_results
```

- Saídas esperadas:
  - CSV: `results/experiment_YYYY-MM-DDTHH-MM-SS.csv`
  - Gráficos: `results/plots/`
  - Relatório de análise: `src/analyzers/analysis_report.md` e/ou `results/analysis/analysis_report.md`

---

## 6. Metodologia

O experimento segue as etapas: desenho, preparação, execução, análise e relatório. Os scripts estão em `src/`. A coleta consiste em executar consultas equivalentes REST e GraphQL contra a API do GitHub em diferentes tratamentos (cache cold/warm, níveis de carga 1/10/50 e tipos de consulta simple/nested/aggregated). Resultados são salvos em CSV com colunas: `timestamp, api_type, query_type, concurrent_clients, cache_state, response_time_ms, payload_size_bytes, status_code`.

---

### 6.1 Coleta de dados

Consultas e endpoints definidos em `src/queries.py`. Clientes REST/GraphQL em `src/clients.py`. Geração de requisições em `src/request_generators.py`. Execução em `src/run_experiment.py`.

---

### 6.2 Tratamentos e controle

Projeto fatorial completo e balanceado, entre-sujeitos por tratamento: `api_type` (REST/GraphQL) × `query_type` (simple/nested/aggregated) × `cache_state` (cold/warm) × `concurrent_clients` (1/10/50). Warm-up aplicado quando `cache_state=warm`. Número de repetições por cliente configurado em `src/config.py`.

---

### 6.3 Medições e amostragem

Medições registradas por cliente e por repetição. CSV incremental com as colunas padronizadas. Amostragem suficiente por tratamento configurada via `repetitions`.

---

### 6.4 Métricas

Métricas do experimento GraphQL vs REST:

#### Métricas (Lab)

| Código | Métrica            | Descrição                                    |
| ------ | ------------------ | -------------------------------------------- |
| M01    | response_time_ms   | Tempo de resposta observado em milissegundos |
| M02    | payload_size_bytes | Tamanho do payload observado em bytes        |
| F01    | status_code        | Código HTTP de retorno                       |
| F02    | cache_state        | Estado de cache: cold/warm                   |
| F03    | concurrent_clients | Número de clientes concorrentes              |
| F04    | query_type         | Tipo de consulta: simple/nested/aggregated   |
| F05    | api_type           | Tipo de API: REST/GraphQL                    |

#### Métricas adicionais (opcional)

| Código | Métrica                   | Descrição                                 |
| ------ | ------------------------- | ----------------------------------------- |
| A01    | tamanho de efeito (delta) | Estimativa com delta de Cliff             |
| A02    | distribuição normal       | Verificação Shapiro para escolha do teste |

---

### 6.5 Cálculo e testes estatísticos

Para cada RQ, comparamos grupos REST vs GraphQL usando t-test (se normalidade) ou Mann-Whitney (caso contrário). Estatísticas descritivas incluem média, mediana, desvio padrão e percentis. O tamanho de efeito é estimado com delta de Cliff. Implementação em `src/analyze_results.py`.

---

### 6.6 Execução

Script de execução: `src/run_experiment.py`. Saída: CSV em `results/experiment_YYYY-MM-DDTHH-MM-SS.csv`. Design snapshot em `src/design_snapshot.md`.

---

### 6.7 Relação das RQs com as Métricas

> As RQs foram associadas às métricas definidas na seção 6.4, garantindo investigação sistemática e mensurável.

A tabela a seguir apresenta a relação entre cada questão de pesquisa e as métricas utilizadas para sua avaliação:

Relação das RQs com Métricas:

| RQ   | Pergunta                            | Métrica utilizada  | Código da Métrica |
| ---- | ----------------------------------- | ------------------ | ----------------- |
| RQ01 | GraphQL é mais rápido que REST?     | Tempo de resposta  | M01               |
| RQ02 | GraphQL tem payload menor que REST? | Tamanho do payload | M02               |

---

## 7. Resultados

Resultados gerados a partir do CSV `results/experiment_YYYY-MM-DDTHH-MM-SS.csv` e analisados por `src/analyze_results.py`.

---

### 7.1 Visualizações

<p align="center">
  <img src="/src/results/analysis/plots/bar_means.png" height="500"/>
  <br/>
  <em>Gráfico 1 - Média do tempo de resposta por tratamento (<code>query_type</code> × <code>api_type</code>)</em>
</p>

- O gráfico de barras mostra que os tempos médios de resposta ficam em torno de 3,1–3,2 s para todos os tipos de consulta (`simple`, `nested`, `aggregated`) tanto em REST quanto em GraphQL.
- As diferenças entre REST e GraphQL em cada tipo de consulta são pequenas e dentro das barras de erro (intervalos de confiança), indicando que não há um ganho consistente de tempo de resposta ao trocar REST por GraphQL em nenhum dos três tipos de consulta.

<p align="center">
  <img src="/src/results/analysis/plots/boxplot_response_time.png" height="500"/>
  <br/>
  <em>Gráfico 2 - Boxplot de tempo de resposta por tipo de API e estado de cache</em>
</p>

- Os boxplots comparam response_time_ms para REST e GraphQL, separados em `cache_state = warm` e `cache_state = cold`.
- As medianas e os intervalos interquartis dos quatro grupos são bastante próximos, com forte sobreposição entre REST/GraphQL e entre warm/cold.
- Observa-se a presença de outliers de alta latência (acima de 6–7 s) em todos os cenários, o que reforça a escolha por testes não paramétricos.
- Em resumo, a variação interna de cada grupo é maior do que as diferenças entre APIs ou entre estados de cache, sugerindo que o tempo de resposta é fortemente influenciado por fatores externos (rede, variabilidade da API do GitHub).

<p align="center">
  <img src="/src/results/analysis/plots/hist_payload.png" height="500"/>
  <br/>
  <em>Gráfico 3 - Distribuição do tamanho de payload por tipo de API</em>
</p>

- O histograma/curva de densidade de payload_size_bytes indica uma distribuição altamente assimétrica, com grande concentração em payload 0 B (respostas sem corpo) e uma cauda longa de respostas com payload elevado.
- REST apresenta dois agrupamentos adicionais de payloads grandes (na faixa de alguns kB e dezenas de kB), enquanto GraphQL concentra-se mais em tamanhos intermediários, com menos ocorrências na cauda mais extrema.
- Visualmente, isso sugere uma diferença sistemática no tamanho dos payloads entre REST e GraphQL, o que será confirmado pelos testes estatísticos.

<p align="center"> <img src="/src/results/analysis/plots/success_rate_api_cache.png" height="500"/> <br/> <em>Gráfico 4 - Taxa de sucesso por tipo de API e estado de cache</em> </p>

- O gráfico de barras compara a proporção de requisições bem-sucedidas (taxa de sucesso, eixo Y) entre GraphQL vs REST, separando por `cache_state` = `cold`/`warm`.
- Visualmente, a REST com cache warm apresenta a maior taxa de sucesso (aprox. 0,33), enquanto REST cold fica por volta de 0,16. Isso sugere um efeito positivo do cache (`warm`) sobre sucesso mais forte em REST.
- Em GraphQL, a taxa de sucesso é baixa e praticamente não muda entre `cold` e `warm` (aprox. 0,11–0,12), sugerindo que o “warm cache” não altera muito o comportamento de sucesso nesse cenário.
- Ponto de atenção importante: as taxas absolutas estão bem baixas (todas abaixo de 0,35). Isso normalmente indica que:
  - a definição de “sucesso” pode estar restritiva (ex.: só `status_code == 200`), ou
  - há muitas respostas não-200, timeouts, erros, rate-limit etc.
- Há forte evidência visual de interação entre cache e API (warm ajuda bem mais a REST).

<p align="center"> <img src="/src/results/analysis/plots/violin_cache_api.png" height="500"/> <br/> <em>Gráfico 5 - Violino do tempo de resposta por estado de cache e tipo de API</em> </p>

- Os violinos mostram a distribuição completa de response_time_ms para cada cache_state (`cold`/`warm`), com comparação entre GraphQL e REST (cores).
- Os formatos são muito semelhantes entre GraphQL e REST, tanto em `cold` quanto em `warm`, com forte sobreposição. Isso reforça o padrão já visto: as diferenças entre APIs são pequenas quando comparadas à variabilidade interna.
- O gráfico sugere uma distribuição bimodal (dois “bojos”):
  - um grupo de respostas mais rápidas (~800–1200 ms),
  - e um grupo principal bem maior (~3300–4200 ms).
Isso pode indicar dois regimes de execução (ex.: tipos de consulta diferentes, condições de rede, variação do serviço do GitHub, concorrência, etc.).
- Há também cauda longa e outliers chegando a ~7–8 s, em ambos os estados de cache e APIs, o que novamente favorece a escolha de medidas robustas (mediana/percentis) e testes não paramétricos.
- Em resumo: `warm` vs `cold` não parece deslocar fortemente a distribuição, e GraphQL vs REST é muito parecido, mas existe bimodalidade e alta variabilidade, sugerindo influência dominante de fatores externos.

<p align="center"> <img src="/src/results/analysis/plots/dist_response_time.png" height="500"/> <br/> <em>Gráfico 6 - Distribuição global do tempo de resposta (histograma + densidade)</em> </p>

- O histograma com curva de densidade mostra a distribuição global de response_time_ms (sem separar por API/cache).
- O comportamento é claramente bimodal:
  - um pico menor por volta de ~900–1100 ms,
  - e um pico dominante por volta de ~3500–4000 ms.
- Isso sugere que o experimento mistura dois grupos de comportamento (por exemplo: endpoints/consultas com custos distintos, cache efetivo em parte do tráfego, variações de rede/servidor, ou até fases do experimento com carga diferente).
- A distribuição tem cauda longa até ~7500 ms, então a média pode ser pouco representativa do “típico”; faz mais sentido falar em mediana, p90/p95 e comparar ECDF/percentis.
- O tempo de resposta não é unimodal/normal; há estruturas internas (dois regimes), o que ajuda a explicar por que diferenças entre APIs podem ficar “diluídas” quando você olha só para média.

<p align="center"> <img src="/src/results/analysis/plots/ecdf_response_time.png" height="500"/> <br/> <em>Gráfico 7 - ECDF do tempo de resposta por tipo de API</em> </p>

- A ECDF* compara a fração acumulada de requisições com tempo ≤ X ms (percentis visuais).
- As curvas são quase sobrepostas, indicando que GraphQL e REST têm distribuições muito similares no geral.
- Há uma leve vantagem do GraphQL na região intermediária (percentis médios), mas a diferença é pequena e as caudas convergem — ou seja, nos piores casos extremos o comportamento é parecido.
- Visualmente, não há ganho consistente e grande de latência ao trocar REST por GraphQL.

> _*ECDF, ou Função de Distribuição Acumulada Empírica, é uma estimativa da função de distribuição cumulativa que gera um conjunto de dados amostrais, mostrando a proporção de observações menores ou iguais a um determinado valor._

<p align="center"> <img src="/src/results/analysis/plots/throughput_per_sec.png" height="500"/> <br/> <em>Gráfico 8 - Vazão aproximada (req/s) ao longo do tempo por API</em> </p>

- O gráfico mostra quantas requisições por segundo ocorreram ao longo do tempo, separadas por API.
- Os padrões de bursts/picos aparecem em ambos: existem períodos de alta atividade e períodos com baixa ou nenhuma requisição.
- O principal valor metodológico aqui é validar comparabilidade de carga: não parece que uma API foi testada sempre sob uma carga muito maior do que a outra (apesar de haver janelas alternadas).
- Em resumo: esse gráfico funciona como controle experimental (carga ao longo do tempo), complementando os gráficos de latência.

---

### 7.2 Estatísticas Descritivas

Estatísticas descritivas calculadas sobre `response_time_ms` e `payload_size_bytes` (média, mediana, desvio padrão, percentis) estão detalhadas em `src/analysis_report.md`.

| Métrica                | Código | Média   | Mediana | Desvio Padrão | P25     | P75     |
| ---------------------- | ------ | ------- | ------- | ------------- | ------- | ------- |
| Tempo de resposta (ms) | M01    | 3158.15 | 3574.87 | 1198.29       | 3023.76 | 3925.14 |
| Tamanho do payload (B) | M02    | 2904.98 | 0.00    | 8136.41       | 0.00    | 495.00  |

Esses valores foram extraídos do relatório de análise automática gerado pelo script (analysis_report.md).

Principais observações:

- O tempo de resposta médio está na ordem de 3,1 s, com mediana um pouco maior (≈3,6 s), indicando assimetria puxada por respostas mais lentas.
- O payload médio (~2,9 kB) é muito maior que a mediana (0 B), o que confirma a existência de muitos casos sem payload e alguns poucos casos com payload muito grande, que aumentam a média e o desvio padrão.

---

### 7.3 Testes estatísticos

Foram aplicados testes estatísticos para responder às RQs:

#### RQ1 — Tempos de resposta (GraphQL é mais rápido que REST?)

- Teste utilizado: Mann-Whitney U (distribuições não normais e presença de outliers).
- Resultado: stat = 669813258.0, p = 0.9907.
- Decisão: Com nível de significância de 5%, não rejeitamos H₀.
- Tamanho de efeito (delta de Cliff): ≈ 0,03, indicando efeito praticamente nulo.

Os dados não fornecem evidências de que GraphQL seja mais rápido que REST em termos de tempo de resposta. As diferenças observadas nos gráficos são pequenas e estatisticamente indistinguíveis da variabilidade natural do experimento.

#### RQ2 — Tamanho de payload (GraphQL tem payload menor?)

- Teste utilizado: Mann-Whitney U.
- Resultado: stat = 1025132470.0, p ≈ 0,0 (p-valor muito menor que 0,001).
- Decisão: Rejeitamos H₀; há diferença estatisticamente significativa entre os tamanhos de payload de REST e GraphQL.
- Tamanho de efeito (delta de Cliff): ≈ 0,53, considerado moderado a forte.

Há evidências robustas de que o tipo de API influencia de forma relevante o tamanho do payload retornado. Em conjunto com o histograma, isso aponta para um comportamento diferente de serialização/dados retornados entre REST e GraphQL, com um dos grupos produzindo payloads consistentemente menores em grande parte das requisições (alinhado com a hipótese de que GraphQL tende a evitar campos desnecessários).

---

### 7.4 Discussão dos resultados

Nesta subseção relacionamos os resultados com as hipóteses informais levantadas pelo grupo (expectativa de que GraphQL seria mais rápido e retornaria menos dados do que REST):

1. Hipótese “GraphQL é mais rápido que REST” (RQ1)

- Os resultados não confirmam essa hipótese.
- Tanto nas médias por tratamento quanto nas distribuições por cache_state, os tempos de resposta de REST e GraphQL são muito semelhantes, com forte sobreposição entre os grupos.
- Possíveis explicações:
  - O tempo total de resposta da API do GitHub parece ser dominado por fatores externos (latência de rede, processamento interno do GitHub, rate limiting), que afetam igualmente REST e GraphQL.
  - O overhead adicional de montagem e resolução das queries GraphQL pode compensar eventuais ganhos de evitar chamadas múltiplas, resultando em tempos equivalentes aos endpoints REST utilizados.

2. Hipótese “GraphQL retorna payload menor que REST” (RQ2)

- Essa hipótese é fortemente suportada pelos dados: o teste Mann-Whitney indica diferença estatística com tamanho de efeito moderado/forte, e a visualização de distribuição mostra padrões distintos de payload entre as APIs.
- Em termos práticos, isso sugere que o modelo declarativo de GraphQL, que permite solicitar apenas os campos necessários, tende a reduzir a quantidade de dados transferida em muitos cenários, ainda que não em todos (há casos com payloads grandes também em GraphQL).

3. Efeito de cache e carga concorrente

- Embora o desenho experimental inclua diferentes níveis de concurrent_clients e estados de cache, os gráficos indicam que a variabilidade intra-grupo é alta e as diferenças entre warm/cold não são suficientemente claras para alterar as conclusões principais.
- Isso reforça que, nas condições deste experimento, a escolha entre REST e GraphQL impacta muito mais o tamanho dos dados transferidos do que a latência observada, enquanto efeitos de cache e concorrência ficaram mascarados pela variabilidade da API real do GitHub.

4. Padrões e insights adicionais

- O grande número de respostas com payload 0 B sugere a presença de endpoints/consultas que retornam cabeçalhos ou confirmações sem corpo, o que influencia fortemente as estatísticas (mediana 0 B).
- A presença de outliers de tempo de resposta em todos os grupos indica que experimentos com APIs públicas estão sujeitos a flutuações significativas de ambiente, reforçando a importância de usar amostras grandes e testes robustos.

Em síntese, o experimento não encontrou evidências de vantagem de tempo de resposta para GraphQL, mas confirmou uma diferença relevante no tamanho dos payloads entre as duas abordagens, alinhando parcialmente os resultados às expectativas iniciais do grupo.

---

## 8. Conclusão

Este experimento controlado comparou a GitHub REST API e a GitHub GraphQL API quanto a duas dimensões principais: tempo de resposta e tamanho do payload. A partir de um desenho fatorial com diferentes tipos de consulta, estados de cache e níveis de concorrência, foram coletadas mais de 73 mil requisições para REST e GraphQL para análise estatística.

Em relação à RQ1 (tempos de resposta), os resultados indicam que não há diferença estatisticamente significativa entre REST e GraphQL. As médias e distribuições de response_time_ms são muito próximas, e o teste de Mann-Whitney (Mann-Whitney U; Cliff’s delta ≈ 0,03) com tamanho de efeito baixo reforça que qualquer vantagem de uma API sobre a outra é, na prática, desprezível nas condições deste estudo. Isso sugere que, para os endpoints e consultas utilizados, a latência é dominada por fatores externos (infraestrutura do GitHub, rede, limitação de taxa, variação de carga) que afetam igualmente ambos os estilos de API.

Já para a RQ2 (tamanho dos payloads), os resultados foram mais claros: há diferença estatística significativa entre os tamanhos de payload de REST e GraphQL, com tamanho de efeito moderado/forte (Cliff’s delta ≈ 0,53). As distribuições mostram que GraphQL tende a produzir respostas com menos dados em grande parte dos casos, o que é coerente com o modelo declarativo da linguagem, em que o cliente especifica exatamente quais campos deseja receber. Na prática, isso pode representar economia de largura de banda e potencial benefício em cenários com conexões limitadas ou alto volume de chamadas.

No conjunto, o estudo mostra que a escolha entre REST e GraphQL, neste contexto, impacta mais o volume de dados trafegados do que o tempo de resposta. Assim, equipes que avaliam migrar ou combinar essas tecnologias devem considerar que GraphQL pode ser vantajoso para reduzir payloads e consolidar consultas, mas não se deve assumir automaticamente que isso trará ganhos de latência.

Como trabalhos futuros, seria interessante: (i) repetir o experimento com outros tipos de operações e em ambientes mais controlados, reduzindo a interferência de fatores externos; (ii) analisar métricas adicionais, como consumo de CPU/memória do cliente, número de chamadas necessárias para cenários reais de agregação de dados e taxas de erro; e (iii) investigar como diferentes estratégias de cache e modelagem de schema GraphQL influenciam tanto a latência quanto o tamanho das respostas. Essas extensões podem oferecer uma visão ainda mais completa sobre quando e por que adotar REST, GraphQL ou uma combinação de ambos em sistemas reais.

---

## 9. Referências

Referências:

- [📌 GitHub API Documentation - GraphQL](https://docs.github.com/en/graphql)
- [📌 GitHub API Documentation - REST](https://docs.github.com/en/rest?apiVersion=2022-11-28)
- [📌 Pandas](https://pandas.pydata.org/)
- [📌 SciPy](https://scipy.org/)
- [📌 Seaborn](https://seaborn.pydata.org/)
- [📌 Python Official Documentation](https://docs.python.org/3/)

---

## 10. Apêndices

- Scripts utilizados para coleta e análise de dados: `src/`
- Consultas GraphQL e endpoints REST: `src/queries.py`
- Arquivos CSV gerados: `results/`
- Google Looker Studio: [Dashboard - LAB05S03](https://lookerstudio.google.com/reporting/c981ba21-8fff-4106-9dc2-f9d9fe5e1e51)
