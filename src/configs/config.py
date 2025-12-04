import os

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

config = {
    "github": {
        "token": GITHUB_TOKEN,
        "rest_base_url": "https://api.github.com",
        "graphql_url": "https://api.github.com/graphql",
    },
    "experiment": {
        "repetitions": 100,
        "warmup_requests": 15,
        "request_interval": 0.1,
        "timeout": 30,
        "concurrent_clients": [1, 10, 50],
        "query_types": ["simple", "nested", "aggregated"],
        "cache_states": ["cold", "warm"],
    },
    "output": {
        "results_dir": "./results",
        "csv_headers": [
            "timestamp",
            "api_type",
            "query_type",
            "concurrent_clients",
            "cache_state",
            "response_time_ms",
            "payload_size_bytes",
            "status_code",
        ],
    },
}
