"""
Main orchestrator for GraphQL vs REST experiment.
- Runs data collection
- Runs analysis and generates plots
- Logs the pipeline steps
"""
import logging
import os
import sys
import analyzers.analyze_results as analysis

# Ensure project root on sys.path
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


def setup_logging():
    os.makedirs(os.path.join(ROOT, "logs"), exist_ok=True)
    log_file = os.path.join(ROOT, "logs", "pipeline.log")
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(log_file, encoding="utf-8"),
            logging.StreamHandler()
        ],
    )
    logging.info("Pipeline logging initialized")


def run_pipeline():
    setup_logging()
    logging.info("Starting experiment pipeline")

    # 1) Run experiment (collection)
    logging.info("Step 1/3: Running experiment (collection)")
    from .collectors.collector import run_experiment
    csv_path = run_experiment()
    logging.info(f"Experiment completed. CSV: {csv_path}")

    # 2) Run analysis (stats + plots)
    logging.info("Step 2/3: Running analysis")
    try:
        if hasattr(analysis, "main"):
            analysis.main()
        elif hasattr(analysis, "run"):
            analysis.run()
        elif hasattr(analysis, "analyze"):
            analysis.analyze()
        else:
            logging.warning(
                "Could not find an entrypoint in app.analyze_results. Ensure it has main()/run()/analyze().")
    except Exception as e:
        logging.exception("Analysis step failed: %s", e)
        raise

    logging.info(
        "Analysis completed. See analyzers/analysis_report.md and results/plots/")
    logging.info("Step 3/3: Pipeline finished")


if __name__ == "__main__":
    run_pipeline()
