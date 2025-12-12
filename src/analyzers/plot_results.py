import os
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def load_data(csv_path: Path) -> pd.DataFrame:
    df = pd.read_csv(csv_path, parse_dates=["timestamp"], infer_datetime_format=True)
    # Normalize categorical columns
    for col in ["api_type", "query_type", "cache_state"]:
        if col in df.columns:
            df[col] = df[col].astype("category")
    return df


def save_figure(fig: plt.Figure, out_dir: Path, name: str):
    out_path = out_dir / f"{name}.png"
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    print(f"Figura salva: {out_path}")
    plt.close(fig)


def plot_distributions(df: pd.DataFrame, out_dir: Path):
    sns.set_theme(style="whitegrid")

    # Overall response time distribution
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.histplot(df["response_time_ms"], kde=True, ax=ax, bins=50, color="#3b82f6")
    ax.set_title("Distribuição de Tempo de Resposta (ms)")
    ax.set_xlabel("Tempo de resposta (ms)")
    ax.set_ylabel("Contagem")
    save_figure(fig, out_dir, "dist_response_time")

    # Violin por cache_state
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.violinplot(
        data=df,
        x="cache_state",
        y="response_time_ms",
        hue="api_type",
        split=True,
        ax=ax,
    )
    ax.set_title("Distribuição por Estado de Cache e API")
    ax.set_xlabel("Estado de cache")
    ax.set_ylabel("Tempo de resposta (ms)")
    save_figure(fig, out_dir, "violin_cache_api")


def plot_time_series(df: pd.DataFrame, out_dir: Path):
    sns.set_theme(style="whitegrid")
    # Rolling median por api_type
    fig, ax = plt.subplots(figsize=(10, 6))
    for api in df["api_type"].cat.categories:
        sub = df[df["api_type"] == api].sort_values("timestamp")
        sub = sub.set_index("timestamp").resample("1S").median(numeric_only=True)
        ax.plot(sub.index, sub["response_time_ms"].rolling(5, min_periods=1).median(), label=api)
    ax.set_title("Série Temporal (Mediana Móvel) de Tempo de Resposta")
    ax.set_xlabel("Tempo")
    ax.set_ylabel("Tempo de resposta (ms)")
    ax.legend(title="API")
    save_figure(fig, out_dir, "ts_response_time_median")

    # ECDF por api_type
    fig, ax = plt.subplots(figsize=(8, 5))
    for api in df["api_type"].cat.categories:
        sub = df[df["api_type"] == api]["response_time_ms"].sort_values()
        y = pd.Series(range(1, len(sub) + 1)) / len(sub)
        ax.step(sub.values, y.values, where="post", label=api)
    ax.set_title("ECDF de Tempo de Resposta por API")
    ax.set_xlabel("Tempo de resposta (ms)")
    ax.set_ylabel("Probabilidade acumulada")
    ax.legend(title="API")
    save_figure(fig, out_dir, "ecdf_response_time")


def plot_relationships(df: pd.DataFrame, out_dir: Path):
    sns.set_theme(style="whitegrid")

    # Scatter payload vs response, color por cache_state e shape por api_type
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.scatterplot(
        data=df,
        x="payload_size_bytes",
        y="response_time_ms",
        hue="cache_state",
        style="api_type",
        ax=ax,
        alpha=0.6,
    )
    ax.set_title("Payload vs Tempo de Resposta")
    ax.set_xlabel("Payload (bytes)")
    ax.set_ylabel("Tempo de resposta (ms)")
    save_figure(fig, out_dir, "scatter_payload_response")

    # Throughput aproximado por janela (req/s) por api_type
    fig, ax = plt.subplots(figsize=(10, 6))
    for api in df["api_type"].cat.categories:
        sub = df[df["api_type"] == api].copy()
        sub = sub.set_index("timestamp").sort_index()
        per_sec = sub["response_time_ms"].resample("1S").count()
        ax.plot(per_sec.index, per_sec.values, label=api)
    ax.set_title("Vazão Aproximada (req/s) por API")
    ax.set_xlabel("Tempo")
    ax.set_ylabel("Requisições por segundo")
    ax.legend(title="API")
    save_figure(fig, out_dir, "throughput_per_sec")

    # Taxa de sucesso/erro por api_type e cache_state
    df["is_success"] = (df.get("status_code", 200) >= 200) & (df.get("status_code", 200) < 300)
    fig, ax = plt.subplots(figsize=(10, 6))
    pct = (
        df.groupby(["api_type", "cache_state"])['is_success']
        .mean()
        .reset_index()
    )
    sns.barplot(data=pct, x="api_type", y="is_success", hue="cache_state", ax=ax)
    ax.set_title("Taxa de Sucesso por API e Cache")
    ax.set_xlabel("API")
    ax.set_ylabel("Taxa de sucesso")
    ax.set_ylim(0, 1)
    save_figure(fig, out_dir, "success_rate_api_cache")


def plot_dashboard(df: pd.DataFrame, out_dir: Path):
    sns.set_theme(style="whitegrid")
    fig, axes = plt.subplots(nrows=2, ncols=3, figsize=(18, 10))

    # dist_response_time
    ax = axes[0, 0]
    sns.histplot(df["response_time_ms"], kde=True, ax=ax, bins=50, color="#3b82f6")
    ax.set_title("Distribuição de Tempo de Resposta (ms)")
    ax.set_xlabel("Tempo de resposta (ms)")
    ax.set_ylabel("Contagem")

    # ecdf_response_time
    ax = axes[0, 1]
    for api in df["api_type"].cat.categories:
        sub = df[df["api_type"] == api]["response_time_ms"].sort_values()
        y = pd.Series(range(1, len(sub) + 1)) / len(sub)
        ax.step(sub.values, y.values, where="post", label=api)
    ax.set_title("ECDF de Tempo de Resposta por API")
    ax.set_xlabel("Tempo de resposta (ms)")
    ax.set_ylabel("Probabilidade acumulada")
    ax.legend(title="API")

    # success_rate_api_cache
    ax = axes[0, 2]
    df["is_success"] = (df.get("status_code", 200) >= 200) & (df.get("status_code", 200) < 300)
    pct = (
        df.groupby(["api_type", "cache_state"])['is_success']
        .mean()
        .reset_index()
    )
    sns.barplot(data=pct, x="api_type", y="is_success", hue="cache_state", ax=ax)
    ax.set_title("Taxa de Sucesso por API e Cache")
    ax.set_xlabel("API")
    ax.set_ylabel("Taxa de sucesso")
    ax.set_ylim(0, 1)

    # throughput_per_second (req/s)
    ax = axes[1, 0]
    for api in df["api_type"].cat.categories:
        sub = df[df["api_type"] == api].copy()
        sub = sub.set_index("timestamp").sort_index()
        per_sec = sub["response_time_ms"].resample("1S").count()
        ax.plot(per_sec.index, per_sec.values, label=api)
    ax.set_title("Vazão Aproximada (req/s) por API")
    ax.set_xlabel("Tempo")
    ax.set_ylabel("Requisições por segundo")
    ax.legend(title="API")

    # violin_cache_api
    ax = axes[1, 1]
    sns.violinplot(
        data=df,
        x="cache_state",
        y="response_time_ms",
        hue="api_type",
        split=True,
        ax=ax,
    )
    ax.set_title("Distribuição por Estado de Cache e API")
    ax.set_xlabel("Estado de cache")
    ax.set_ylabel("Tempo de resposta (ms)")

    # Hide unused subplot
    axes[1, 2].axis('off')

    save_figure(fig, out_dir, "dashboard_overview")

def generate_all_plots(csv_path: str, out_dir: str | None = None):
    csv_path = Path(csv_path)
    if out_dir is None:
        # Save under src/results/analysis/plots
        out_dir = Path(__file__).resolve().parents[1] / "results" / "analysis" / "plots"
    else:
        out_dir = Path(out_dir)
    ensure_dir(out_dir)

    df = load_data(csv_path)
    plot_distributions(df, out_dir)
    plot_time_series(df, out_dir)
    plot_relationships(df, out_dir)
    plot_dashboard(df, out_dir)


if __name__ == "__main__":
    # Default to the latest experiment CSV in src/results
    base = Path(__file__).resolve().parents[1] / "results"
    candidates = sorted(base.glob("experiment_*.csv"))
    if not candidates:
        raise SystemExit("Nenhum arquivo de experimento encontrado em src/results")
    latest = candidates[-1]
    print(f"Gerando gráficos a partir de: {latest}")
    # Save under src/results/analysis/plots
    out = Path(__file__).resolve().parents[1] / "results" / "analysis" / "plots"
    generate_all_plots(str(latest), str(out))
