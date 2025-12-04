
# Desenho do Experimento — GraphQL vs REST

## Hipóteses
- RQ1 — H0: Não há diferença significativa nos tempos de resposta entre GraphQL e REST.
- RQ1 — H1: GraphQL apresenta tempos de resposta significativamente menores do que REST.
- RQ2 — H0: Não há diferença significativa no tamanho dos payloads entre GraphQL e REST.
- RQ2 — H1: GraphQL apresenta payloads significativamente menores do que REST.

## Variáveis
- Independentes: api_type (REST, GraphQL), query_type (simple, nested, aggregated), cache_state (cold, warm), concurrent_clients (níveis de carga)
- Dependentes: response_time_ms, payload_size_bytes

## Tratamentos
- Comparação REST vs GraphQL
- Cache ligado (warm) vs desligado (cold)
- Níveis de carga: valores de concurrent_clients

## Objetos experimentais
- REST: simple, nested, aggregated conforme endpoints definidos.
- GraphQL: queries equivalentes conforme definidas.

## Tipo de Projeto Experimental
Projeto fatorial completo e balanceado, entre-sujeitos por tratamento (combinações de api_type, query_type, cache_state e níveis de concurrent_clients). As medições são repetidas por cliente em cada tratamento para capturar variabilidade intra-tratamento.

## Quantidade de medições (N)
Definimos N por tratamento considerando estabilidade estatística dos estimadores (média/mediana) e poder do teste. Valores típicos de N≥50 por condição são desejáveis para testes não-paramétricos e para mitigar variância sob alta concorrência. Neste experimento, adotamos N=config['experiment']['repetitions'] por cliente, garantindo amostragem suficiente por combinação de tratamentos.

## Ameaças à validade
- Conclusão: Viés de implementação: diferenças específicas de endpoints podem favorecer um estilo de API.; Interpretação indevida de significância estatística sem tamanho de efeito.
- Interna: Variações de rede/latência externa durante as medidas.; Efeito de aquecimento/caching em camadas não controladas (CDN/servidor).
- Externa: Generalização limitada a outros domínios além do GitHub API.; Resultados podem depender de modelos de dados e cargas diferentes.
- Estatística: Não-normalidade das distribuições de tempo/tamanho; necessidade de testes não-paramétricos.; Outliers e heterocedasticidade sob concorrência alta.
