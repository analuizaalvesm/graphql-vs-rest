import importlib


def test_can_import_src_package():
    pkg = importlib.import_module('src')
    assert pkg is not None


def test_can_import_config_and_keys():
    cfg = importlib.import_module('src.configs.config')
    assert hasattr(cfg, 'config')
    for key in ['github', 'experiment', 'output']:
        assert key in cfg.config


def test_can_import_analyzer_module():
    ar = importlib.import_module('src.analyzers.analyze_results')
    # Only check presence; do not execute analysis (requires CSV files)
    assert hasattr(ar, 'run_analysis')


def test_requirements_file_exists():
    import os
    assert os.path.exists(os.path.join('src', 'requirements.txt'))
