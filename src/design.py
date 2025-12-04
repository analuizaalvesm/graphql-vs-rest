"""
Experiment Design Module: GraphQL vs REST
Provides ready-to-use strings and helper accessors for the report.
"""
from dataclasses import dataclass
from typing import List

# 1. Hypotheses (RQ1, RQ2)
HYPOTHESES_TEXT = {
    "RQ1": {
        "H0": "Não há diferença significativa nos tempos de resposta entre GraphQL e REST.",
        "H1": "GraphQL apresenta tempos de resposta significativamente menores do que REST."
    },
    "RQ2": {
        "H0": "Não há diferença significativa no tamanho dos payloads entre GraphQL e REST.",
        "H1": "GraphQL apresenta payloads significativamente menores do que REST."
    }
}

# 2. Variables
VARIABLES_TEXT = {
    "independentes": [
        "api_type (REST, GraphQL)",
        "query_type (simple, nested, aggregated)",
        "cache_state (cold, warm)",
        "concurrent_clients (níveis de carga)"
    ],
    "dependentes": [
        "response_time_ms",
        "payload_size_bytes"
    ]
}

# 3. Treatments
TREATMENTS_TEXT = [
    "Comparação REST vs GraphQL",
    "Cache ligado (warm) vs desligado (cold)",
    "Níveis de carga: valores de concurrent_clients"
]

# 4. Experimental Objects
EXPERIMENTAL_OBJECTS_TEXT = {
    "REST": {
        "simple": "GET /repos/facebook/react",
        "nested": "GET /repos/facebook/react/issues?state=open&per_page=10",
        "aggregated": [
            "GET /repos/facebook/react",
            "GET /repos/facebook/react/contributors?per_page=5",
            "GET /repos/facebook/react/languages"
        ]
    },
    "GraphQL": {
        "simple": "query SimpleQuery { repository(owner: \"facebook\", name: \"react\") { id name description stargazerCount forkCount createdAt updatedAt } }",
        "nested": "query NestedQuery { repository(owner: \"facebook\", name: \"react\") { id name description stargazerCount forkCount issues(first: 10, states: OPEN) { nodes { id title createdAt author { login } comments(first: 3) { nodes { id body createdAt author { login } } } } } } }",
        "aggregated": "query AggregatedQuery { repository(owner: \"facebook\", name: \"react\") { id name description stargazerCount forkCount languages(first: 10) { nodes { name color } } collaborators(first: 5) { nodes { login name avatarUrl } } releases(first: 5) { nodes { id name tagName createdAt } } } }"
    }
}

# 5. Design Type
DESIGN_TYPE_TEXT = (
    "Projeto fatorial completo e balanceado, entre-sujeitos por tratamento (combinações de api_type, query_type, cache_state e níveis de concurrent_clients). "
    "As medições são repetidas por cliente em cada tratamento para capturar variabilidade intra-tratamento."
)

# 6. Number of Measurements (N)
SAMPLE_SIZE_TEXT = (
    "Definimos N por tratamento considerando estabilidade estatística dos estimadores (média/mediana) e poder do teste. "
    "Valores típicos de N≥50 por condição são desejáveis para testes não-paramétricos e para mitigar variância sob alta concorrência. "
    "Neste experimento, adotamos N=config['experiment']['repetitions'] por cliente, garantindo amostragem suficiente por combinação de tratamentos."
)

# 7. Threats to Validity
THREATS_TEXT = {
    "conclusao": [
        "Viés de implementação: diferenças específicas de endpoints podem favorecer um estilo de API.",
        "Interpretação indevida de significância estatística sem tamanho de efeito."
    ],
    "interna": [
        "Variações de rede/latência externa durante as medidas.",
        "Efeito de aquecimento/caching em camadas não controladas (CDN/servidor)."
    ],
    "externa": [
        "Generalização limitada a outros domínios além do GitHub API.",
        "Resultados podem depender de modelos de dados e cargas diferentes."
    ],
    "estatistica": [
        "Não-normalidade das distribuições de tempo/tamanho; necessidade de testes não-paramétricos.",
        "Outliers e heterocedasticidade sob concorrência alta."
    ]
}

DESIGN_MARKDOWN = f"""
# Desenho do Experimento — GraphQL vs REST

## Hipóteses
- RQ1 — H0: {HYPOTHESES_TEXT['RQ1']['H0']}
- RQ1 — H1: {HYPOTHESES_TEXT['RQ1']['H1']}
- RQ2 — H0: {HYPOTHESES_TEXT['RQ2']['H0']}
- RQ2 — H1: {HYPOTHESES_TEXT['RQ2']['H1']}

## Variáveis
- Independentes: {', '.join(VARIABLES_TEXT['independentes'])}
- Dependentes: {', '.join(VARIABLES_TEXT['dependentes'])}

## Tratamentos
- {TREATMENTS_TEXT[0]}
- {TREATMENTS_TEXT[1]}
- {TREATMENTS_TEXT[2]}

## Objetos experimentais
- REST: simple, nested, aggregated conforme endpoints definidos.
- GraphQL: queries equivalentes conforme definidas.

## Tipo de Projeto Experimental
{DESIGN_TYPE_TEXT}

## Quantidade de medições (N)
{SAMPLE_SIZE_TEXT}

## Ameaças à validade
- Conclusão: {'; '.join(THREATS_TEXT['conclusao'])}
- Interna: {'; '.join(THREATS_TEXT['interna'])}
- Externa: {'; '.join(THREATS_TEXT['externa'])}
- Estatística: {'; '.join(THREATS_TEXT['estatistica'])}
"""


@dataclass
class DesignSummary:
    hypotheses: dict
    variables: dict
    treatments: List[str]
    objects: dict
    design_type: str
    sample_size_text: str
    threats: dict


def get_design_summary() -> DesignSummary:
    return DesignSummary(
        hypotheses=HYPOTHESES_TEXT,
        variables=VARIABLES_TEXT,
        treatments=TREATMENTS_TEXT,
        objects=EXPERIMENTAL_OBJECTS_TEXT,
        design_type=DESIGN_TYPE_TEXT,
        sample_size_text=SAMPLE_SIZE_TEXT,
        threats=THREATS_TEXT,
    )
