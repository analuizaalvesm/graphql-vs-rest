"""
Run the full GraphQL vs REST experiment.
Executes all treatments and saves CSV incrementally.
"""
import csv
import os
import time
import random
import logging
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, Any, List

from tqdm import tqdm

from ..configs.config import config
from ..design import get_design_summary, DESIGN_MARKDOWN
from ..configs.request_generators import (
    generate_rest_request,
    generate_graphql_request,
    build_record,
    get_load_levels,
    cache_enabled,
)

RESULTS_DIR = config["output"]["results_dir"]
CSV_HEADERS = config["output"]["csv_headers"]


def _ensure_dirs():
    os.makedirs(RESULTS_DIR, exist_ok=True)
    os.makedirs("src", exist_ok=True)
    design_md_path = os.path.join("src", "design_snapshot.md")
    if not os.path.exists(design_md_path):
        with open(design_md_path, "w", encoding="utf-8") as f:
            f.write(DESIGN_MARKDOWN)
    os.makedirs("logs", exist_ok=True)


def _setup_logging():
    _ensure_dirs()
    log_file = os.path.join("logs", "experiment.log")
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(log_file, encoding="utf-8"),
            logging.StreamHandler()
        ],
    )
    logging.info("Logging initialized for experiment run")


def _new_csv_path() -> str:
    ts = time.strftime("%Y-%m-%dT%H-%M-%S", time.gmtime())
    return os.path.join(RESULTS_DIR, f"experiment_{ts}.csv")


def _run_single_measurement(api_type: str, query_type: str, concurrent_clients: int, cache_state: str) -> Dict[str, Any]:
    if api_type == "REST":
        result = generate_rest_request(query_type)
    else:
        result = generate_graphql_request(query_type)
    return build_record(api_type, query_type, concurrent_clients, cache_state, result)


def _run_treatment(writer, api_type: str, query_type: str, concurrent_clients: int, cache_state: str):
    if cache_enabled(cache_state):
        warmups = config["experiment"]["warmup_requests"]
        for _ in range(warmups):
            _run_single_measurement(
                api_type, query_type, concurrent_clients, cache_state)
            time.sleep(config["experiment"]["request_interval"])

    reps = config["experiment"]["repetitions"]
    interval = config["experiment"]["request_interval"]

    def client_loop(progress_cb=None):
        for i in range(reps):
            rec = _run_single_measurement(
                api_type, query_type, concurrent_clients, cache_state)
            writer.writerow(rec)
            if progress_cb:
                progress_cb(1)
            if i < reps - 1:
                time.sleep(interval)

    total_iters = concurrent_clients * reps
    with ThreadPoolExecutor(max_workers=concurrent_clients) as pool:
        with tqdm(total=total_iters, desc=f"Coleta {api_type}/{query_type} (cache={cache_state}, cc={concurrent_clients})") as pbar:
            def progress_cb(n): return pbar.update(n)
            futures = [pool.submit(client_loop, progress_cb)
                       for _ in range(concurrent_clients)]
            for f in futures:
                f.result()


def _generate_treatments() -> List[Dict[str, Any]]:
    treatments: List[Dict[str, Any]] = []
    for qt in config["experiment"]["query_types"]:
        for cc in get_load_levels(config["experiment"]["concurrent_clients"]):
            for cs in config["experiment"]["cache_states"]:
                treatments.append(
                    {"api": "REST", "qt": qt, "cc": cc, "cs": cs})
                treatments.append(
                    {"api": "GraphQL", "qt": qt, "cc": cc, "cs": cs})
    random.shuffle(treatments)
    return treatments


def run_experiment() -> str:
    _setup_logging()
    _ = get_design_summary()
    csv_path = _new_csv_path()

    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
        writer.writeheader()

        treatments = _generate_treatments()
        logging.info(f"Total treatments: {len(treatments)}")
        for idx, t in enumerate(treatments, start=1):
            logging.info(f"Running treatment {idx}/{len(treatments)}: {t}")
            _run_treatment(writer, t["api"], t["qt"], t["cc"], t["cs"])
            if idx < len(treatments):
                logging.info("Stabilization interval...")
                time.sleep(30.0)

    logging.info(f"Results saved to: {csv_path}")
    return csv_path


if __name__ == "__main__":
    run_experiment()
