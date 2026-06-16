from __future__ import annotations

import json
import sys
from pathlib import Path

APP_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(APP_DIR))

from utils.data_loader import DATA_PATH, DATASET_VERSION, load_or_create_data
from utils.monitoring import challenger_comparison, portfolio_report


def main() -> None:
    df = load_or_create_data(DATA_PATH)
    report = portfolio_report(df)
    report["dataset_version"] = DATASET_VERSION
    report["champion_challenger_sample"] = challenger_comparison(df, limit=25).to_dict(orient="records")

    output_path = APP_DIR / "artifacts" / "portfolio_metrics_report.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
    print(json.dumps(report, indent=2, default=str))


if __name__ == "__main__":
    main()
