"""
Analysis of GraphQL vs REST CSV results.
Generates stats, tests, visualizations, and a Markdown report.
"""
import os
import math
import json
from typing import Tuple

import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns

RESULTS_DIR = "results"
OUTPUT_DIR = os.path.join("results", "analysis")
REPORT_MD = os.path.join(OUTPUT_DIR, "analysis_report.md")
PLOTS_DIR = os.path.join(OUTPUT_DIR, "plots")

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(PLOTS_DIR, exist_ok=True)


def _load_latest_csv() -> str:
    files = [f for f in os.listdir(RESULTS_DIR) if f.endswith(".csv")]
    if not files:
        raise FileNotFoundError("No CSV files found in results directory.")
    latest = sorted(files)[-1]
    return os.path.join(RESULTS_DIR, latest)


def _validate(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df = df[df["response_time_ms"].between(0, 600000)]
    df = df[df["payload_size_bytes"] >= 0]
    df = df[df["status_code"].between(0, 599)]
    return df


def _descriptive(df: pd.DataFrame, col: str) -> dict:
    series = df[col].dropna()
    desc = {
        "count": int(series.count()),
        "mean": float(series.mean()) if series.size else math.nan,
        "median": float(series.median()) if series.size else math.nan,
        "std": float(series.std(ddof=1)) if series.size > 1 else math.nan,
        "p25": float(series.quantile(0.25)) if series.size else math.nan,
        "p75": float(series.quantile(0.75)) if series.size else math.nan,
    }
    return desc


def _normality(series: pd.Series) -> Tuple[float, float]:
    series = series.dropna()
    if series.size < 8:
        return (np.nan, np.nan)
    stat, p = stats.shapiro(series.sample(min(5000, series.size)))
    return stat, p


def _compare_groups(df: pd.DataFrame, col: str) -> dict:
    rest = df[df["api_type"] == "REST"][col].dropna()
    gql = df[df["api_type"] == "GraphQL"][col].dropna()
    sh_rest = _normality(rest)[1]
    sh_gql = _normality(gql)[1]
    method = "mannwhitney"
    pval = np.nan
    stat = np.nan

    if (sh_rest is not np.nan and sh_rest > 0.05) and (sh_gql is not np.nan and sh_gql > 0.05):
        method = "t-test"
        stat, pval = stats.ttest_ind(
            rest, gql, equal_var=False, nan_policy="omit")
    else:
        stat, pval = stats.mannwhitneyu(rest, gql, alternative="two-sided")

    eff = np.nan
    try:
        def cliffs_delta(a, b):
            gt = sum(x > y for x in a for y in b)
            lt = sum(x < y for x in a for y in b)
            return (gt - lt) / (len(a) * len(b))
        eff = cliffs_delta(list(rest.sample(min(1000, len(rest)), replace=False)), list(
            gql.sample(min(1000, len(gql)), replace=False)))
    except Exception:
        pass

    return {"method": method, "stat": float(stat) if not np.isnan(stat) else np.nan, "p": float(pval) if not np.isnan(pval) else np.nan, "effect": eff}


def _plots(df: pd.DataFrame):
    sns.set(style="whitegrid")
    plt.figure(figsize=(10, 6))
    sns.boxplot(data=df, x="api_type", y="response_time_ms", hue="cache_state")
    plt.title("Tempo de resposta por tipo de API e cache")
    plt.xlabel("Tipo de API")
    plt.ylabel("Tempo de resposta (ms)")
    plt.legend(title="Estado do cache", loc="best")
    path1 = os.path.join(PLOTS_DIR, "boxplot_response_time.png")
    plt.savefig(path1, bbox_inches="tight")
    plt.close()

    plt.figure(figsize=(10, 6))
    sns.histplot(data=df, x="payload_size_bytes",
                 hue="api_type", kde=True, bins=40)
    plt.title("Distribuição do tamanho do payload")
    plt.xlabel("Tamanho do payload (bytes)")
    plt.ylabel("Contagem")
    plt.legend(title="Tipo de API", loc="best")
    path2 = os.path.join(PLOTS_DIR, "hist_payload.png")
    plt.savefig(path2, bbox_inches="tight")
    plt.close()

    grouped = df.groupby(["api_type", "query_type", "cache_state"]).agg(
        {"response_time_ms": "mean"}).reset_index()
    plt.figure(figsize=(12, 6))
    sns.barplot(data=grouped, x="query_type",
                y="response_time_ms", hue="api_type")
    plt.title("Média de tempo de resposta por tratamento (cache agregado)")
    plt.xlabel("Tipo de consulta (query_type)")
    plt.ylabel("Tempo de resposta médio (ms)")
    plt.legend(title="Tipo de API", loc="best")
    path3 = os.path.join(PLOTS_DIR, "bar_means.png")
    plt.savefig(path3, bbox_inches="tight")
    plt.close()

    return [path1, path2, path3]


def _write_report(stats_rt: dict, stats_pl: dict, test_rt: dict, test_pl: dict, plots: list):
    lines = []
    lines.append("# Análise dos Resultados — GraphQL vs REST")
    lines.append("")
    lines.append("## Estatísticas Descritivas")
    lines.append(
        f"- response_time_ms: {json.dumps(stats_rt, ensure_ascii=False)}")
    lines.append(
        f"- payload_size_bytes: {json.dumps(stats_pl, ensure_ascii=False)}")
    lines.append("")
    lines.append("## RQ1 — Tempos de resposta")
    lines.append(
        f"- Teste: {test_rt['method']} (stat={test_rt['stat']}, p={test_rt['p']})")
    decision_rt = "Rejeita H0" if (not math.isnan(
        test_rt['p']) and test_rt['p'] < 0.05) else "Não rejeita H0"
    lines.append(f"- Decisão: {decision_rt}")
    lines.append(f"- Tamanho de efeito aproximado: {test_rt['effect']}")

    lines.append("")
    lines.append("## RQ2 — Tamanho de payload")
    lines.append(
        f"- Teste: {test_pl['method']} (stat={test_pl['stat']}, p={test_pl['p']})")
    decision_pl = "Rejeita H0" if (not math.isnan(
        test_pl['p']) and test_pl['p'] < 0.05) else "Não rejeita H0"
    lines.append(f"- Decisão: {decision_pl}")
    lines.append(f"- Tamanho de efeito aproximado: {test_pl['effect']}")

    lines.append("")
    lines.append("## Visualizações")
    lines.append(
        "![Boxplot Tempo de Resposta](plots/boxplot_response_time.png)")
    lines.append("![Distribuição do Payload](plots/hist_payload.png)")
    lines.append("![Média por Tratamento](plots/bar_means.png)")

    with open(REPORT_MD, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"Analysis report written to {REPORT_MD}")


def run_analysis(csv_path: str | None = None):
    if csv_path is None:
        csv_path = _load_latest_csv()
    print(f"Loading data from {csv_path}")
    df = pd.read_csv(csv_path)
    df = _validate(df)

    stats_rt = _descriptive(df, "response_time_ms")
    stats_pl = _descriptive(df, "payload_size_bytes")

    test_rt = _compare_groups(df, "response_time_ms")
    test_pl = _compare_groups(df, "payload_size_bytes")

    plots = _plots(df)
    _write_report(stats_rt, stats_pl, test_rt, test_pl, plots)


if __name__ == "__main__":
    run_analysis()
