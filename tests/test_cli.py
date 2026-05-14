from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CLI_PATH = PROJECT_ROOT / "src" / "clean_csv.py"
CLI_ENV = {**os.environ, "PYTHONIOENCODING": "utf-8"}


def test_cli_creates_cleaned_csv(tmp_path: Path) -> None:
    input_path = tmp_path / "sales_raw.csv"
    output_path = tmp_path / "sales_cleaned.csv"
    pd.DataFrame(
        [
            {
                "注文日": "2026-04-02",
                "顧客名": "北川物流",
                "商品名": "モニター",
                "数量": 3,
                "金額": "81,000",
                "社内メモ": "月末請求",
            },
            {
                "注文日": "2026-04-01",
                "顧客名": "青山食品",
                "商品名": "プリンター",
                "数量": 2,
                "金額": "54,000",
                "社内メモ": "電話確認済み",
            },
            {
                "注文日": "2026-04-02",
                "顧客名": "北川物流",
                "商品名": "モニター",
                "数量": 3,
                "金額": "81,000",
                "社内メモ": "月末請求",
            },
        ]
    ).to_csv(input_path, index=False, encoding="utf-8-sig")

    result = subprocess.run(
        [
            sys.executable,
            str(CLI_PATH),
            "--input",
            str(input_path),
            "--output",
            str(output_path),
            "--columns",
            "注文日,顧客名,商品名,数量,金額",
            "--dedupe",
            "--sort-by",
            "注文日",
            "--sort-type",
            "date",
            "--sort-order",
            "asc",
        ],
        cwd=PROJECT_ROOT,
        env=CLI_ENV,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )

    assert result.returncode == 0
    cleaned = pd.read_csv(output_path, encoding="utf-8-sig")
    assert list(cleaned.columns) == ["注文日", "顧客名", "商品名", "数量", "金額"]
    assert list(cleaned["注文日"]) == ["2026-04-01", "2026-04-02"]


def test_cli_returns_error_for_missing_column(tmp_path: Path) -> None:
    input_path = tmp_path / "sales_raw.csv"
    output_path = tmp_path / "sales_cleaned.csv"
    pd.DataFrame([{"注文日": "2026-04-01", "金額": 1000}]).to_csv(
        input_path,
        index=False,
        encoding="utf-8-sig",
    )

    result = subprocess.run(
        [
            sys.executable,
            str(CLI_PATH),
            "--input",
            str(input_path),
            "--output",
            str(output_path),
            "--columns",
            "注文日,存在しない列",
        ],
        cwd=PROJECT_ROOT,
        env=CLI_ENV,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )

    assert result.returncode == 1
    assert "存在しない列" in result.stderr
    assert not output_path.exists()
