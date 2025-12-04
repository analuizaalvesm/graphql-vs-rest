import json
import time
from typing import List, Dict, Any

import requests
from requests import Response
from gql import Client, gql
from gql.transport.requests import RequestsHTTPTransport

from .config import config


class RestClient:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"token {config['github']['token']}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "GraphQL-vs-REST-Experiment",
        })
        self.base_url = config["github"]["rest_base_url"]
        self.timeout = config["experiment"]["timeout"]

    def make_request(self, url: str) -> Dict[str, Any]:
        start = time.perf_counter()
        try:
            resp: Response = self.session.get(
                self.base_url + url, timeout=self.timeout)
            elapsed_ms = (time.perf_counter() - start) * 1000
            data = resp.json()
            payload_size = len(json.dumps(data))
            return {
                "responseTime": elapsed_ms,
                "payloadSize": payload_size,
                "statusCode": resp.status_code,
                "success": True,
                "data": data,
            }
        except requests.RequestException as e:
            elapsed_ms = (time.perf_counter() - start) * 1000
            status = getattr(getattr(e, 'response', None),
                             'status_code', 0) or 0
            return {
                "responseTime": elapsed_ms,
                "payloadSize": 0,
                "statusCode": status,
                "success": False,
                "error": str(e),
            }

    def make_aggregated_request(self, urls: List[str]) -> Dict[str, Any]:
        start = time.perf_counter()
        try:
            responses = [self.session.get(
                self.base_url + u, timeout=self.timeout) for u in urls]
            for r in responses:
                r.raise_for_status()
            combined = [r.json() for r in responses]
            elapsed_ms = (time.perf_counter() - start) * 1000
            payload_size = len(json.dumps(combined))
            return {
                "responseTime": elapsed_ms,
                "payloadSize": payload_size,
                "statusCode": 200,
                "success": True,
                "data": combined,
            }
        except requests.RequestException as e:
            elapsed_ms = (time.perf_counter() - start) * 1000
            status = getattr(getattr(e, 'response', None),
                             'status_code', 0) or 0
            return {
                "responseTime": elapsed_ms,
                "payloadSize": 0,
                "statusCode": status,
                "success": False,
                "error": str(e),
            }


class GraphQLClientWrapper:
    def __init__(self):
        transport = RequestsHTTPTransport(
            url=config["github"]["graphql_url"],
            headers={
                "Authorization": f"Bearer {config['github']['token']}",
                "User-Agent": "GraphQL-vs-REST-Experiment",
            },
            timeout=config["experiment"]["timeout"],
            verify=True,
        )
        self.client = Client(transport=transport,
                             fetch_schema_from_transport=False)

    def make_request(self, query: str) -> Dict[str, Any]:
        start = time.perf_counter()
        try:
            data = self.client.execute(gql(query))
            elapsed_ms = (time.perf_counter() - start) * 1000
            payload_size = len(json.dumps(data))
            return {
                "responseTime": elapsed_ms,
                "payloadSize": payload_size,
                "statusCode": 200,
                "success": True,
                "data": data,
            }
        except Exception as e:
            elapsed_ms = (time.perf_counter() - start) * 1000
            status = 0
            return {
                "responseTime": elapsed_ms,
                "payloadSize": 0,
                "statusCode": status,
                "success": False,
                "error": str(e),
            }
