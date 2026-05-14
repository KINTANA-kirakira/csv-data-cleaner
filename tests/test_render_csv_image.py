from __future__ import annotations

from pathlib import Path

import pandas as pd

from csv_data_cleaner.render_csv_image import render_csv_to_image


def test_render_csv_to_image_creates_png(tmp_path: Path) -> None:
    input_path = tmp_path / "sales.csv"
    output_path = tmp_path / "sales.png"
    pd.DataFrame(
        [
            {"注文日": "2026-04-01", "顧客名": "青山食品", "金額": 54000},
            {"注文日": "2026-04-02", "顧客名": "北川物流", "金額": 81000},
        ]
    ).to_csv(input_path, index=False, encoding="utf-8-sig")

    render_csv_to_image(input_path, output_path, title="実行後CSV", max_rows=2)

    assert output_path.exists()
    assert output_path.stat().st_size > 0
    assert output_path.read_bytes().startswith(b"\x89PNG\r\n\x1a\n")
