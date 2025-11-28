1. Desenho do Experimento
A. Hipóteses
RQ1 — Tempo de resposta

H0 (nula): Não há diferença significativa no tempo de resposta entre consultas feitas via GraphQL e via REST.

H1 (alternativa): As respostas a consultas GraphQL têm tempos de resposta diferentes (tipicamente menores) que as respostas REST.

RQ2 — Tamanho da resposta

H0 (nula): Não há diferença significativa no tamanho (bytes) das respostas entre GraphQL e REST.

H1 (alternativa): As respostas GraphQL têm tamanho diferente (tipicamente menor) que as respostas REST.

B. Variáveis Dependentes (VD)

Tempo de resposta (ms) por requisição.

Tamanho da resposta (bytes) do payload.

(Opcional) Throughput (req/s) sob carga.

C. Variáveis Independentes (VI)

Tipo de API: GraphQL vs REST.

Tipo de consulta: simples, nested, agregada.

Carga: número de clientes concorrentes (1, 10, 50).

Estado de cache: cold vs warm.

Payload solicitado: profundidade e quantidade de campos retornados.

D. Tratamentos

Combinações entre Tipo de API, Tipo de Consulta, Carga e Cache:

T1: REST — consulta simples — 1 cliente — cold cache

T2: GraphQL — consulta simples — 1 cliente — cold cache

T3: REST — consulta nested — 10 clientes — warm cache

T4: GraphQL — consulta nested — 10 clientes — warm cache

T5: REST — consulta agregada — 50 clientes — warm cache

T6: GraphQL — consulta agregada — 50 clientes — warm cache

(O experimento executará todos os pares REST/GraphQL equivalentes.)

E. Objetos Experimentais

APIs implementadas:

Uma API REST com endpoints equivalentes.

Uma API GraphQL expondo schema equivalente.

Banco de dados: mesmo dataset e mesma instância para ambas as APIs.

Dataset sintético: ~200 usuários, 10.000 posts, 50.000 comentários.

Scripts de medição: ferramentas como curl, wrk, hey e scripts Python/Bash.

Máquina de execução: servidor onde as APIs rodam e cliente que dispara requisições.

F. Tipo de Projeto Experimental

Within-subjects (medidas repetidas): ambas as APIs testadas sobre o mesmo ambiente/dataset.

Randomização / contrabalanceamento: ordem das execuções variada para evitar viés de ordem.

G. Quantidade de Medições

30 repetições por combinação (API × consulta × carga × cache).

Warm-up: 10 requisições iniciais para estabilização quando o cache for warm.

Total estimado: 1.080 medições (3 tipos de consulta × 3 cargas × 2 caches × 2 APIs × 30 repetições).

Replicações adicionais: até 3 rodadas completas para reduzir variabilidade temporal.

H. Ameaças à Validade
Validade Interna

Variações na carga da máquina (CPU, GC, processos).

Efeito de ordem entre GraphQL e REST.

Instabilidade de rede.

Mitigação: ambiente isolado, ordem randomizada, janelas de teste controladas.

Validade Externa

Implementações específicas podem favorecer uma API.

Dataset sintético pode não representar cenários reais.

Mitigação: documentar stack e limitações; base inspirada em dados reais.

Validade de Construto

Diferença entre o que se mede (tempo total/payload) e o que se quer avaliar (eficiência da abordagem).

Compressão HTTP pode distorcer tamanho.

Mitigação: usar Accept-Encoding: identity e registrar métricas exatas.

Validade de Conclusão

Outliers, timeouts ou falhas podem enviesar resultados.

Mitigação: registrar e tratar outliers, definir regras claras de inclusão/exclusão.