"""
Request generators and load configuration helpers using local app modules.
"""
from typing import Dict, Any, List
from datetime import datetime

from .clients import RestClient, GraphQLClientWrapper
from .queries import rest_queries, graphql_queries


def generate_rest_request(query_type: str) -> Dict[str, Any]:
    client = RestClient()
    q = rest_queries[query_type]
    if query_type == "aggregated":
        return client.make_aggregated_request(q["urls"])
    return client.make_request(q["url"])


def generate_graphql_request(query_type: str) -> Dict[str, Any]:
    client = GraphQLClientWrapper()
    q = graphql_queries[query_type]
    return client.make_request(q)


def build_record(api_type: str, query_type: str, concurrent_clients: int, cache_state: str, result: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "api_type": api_type,
        "query_type": query_type,
        "concurrent_clients": concurrent_clients,
        "cache_state": cache_state,
        "response_time_ms": round(result.get("responseTime", 0), 3),
        "payload_size_bytes": result.get("payloadSize", 0),
        "status_code": result.get("statusCode", 0),
    }


def get_load_levels(levels: List[int]) -> List[int]:
    return list(levels)


def cache_enabled(cache_state: str) -> bool:
    return cache_state.lower() == "warm"
