from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib import font_manager


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="CSVを提出用の表画像に変換します。")
    parser.add_argument("--input", required=True, help="入力CSVファイルのパス")
    parser.add_argument("--output", required=True, help="出力PNGファイルのパス")
    parser.add_argument("--title", help="画像上部に表示するタイトル")
    parser.add_argument(
        "--max-rows",
        type=int,
        default=20,
        help="画像に表示する最大行数",
    )
    return parser


def render_csv_to_image(
    input_path: str | Path,
    output_path: str | Path,
    *,
    title: str | None = None,
    max_rows: int = 20,
) -> None:
    setup_japanese_font()

    source = Path(input_path)
    output = Path(output_path)
    df = pd.read_csv(source, encoding="utf-8-sig")
    display_df = df.head(max_rows).astype(str)

    row_count = max(len(display_df), 1)
    column_count = max(len(display_df.columns), 1)
    width = max(8.0, column_count * 1.4)
    height = max(3.0, row_count * 0.45 + (1.0 if title else 0.4))

    fig, ax = plt.subplots(figsize=(width, height))
    ax.axis("off")

    table_bbox = [0, 0, 1, 0.88] if title else [0, 0, 1, 1]
    table = ax.table(
        cellText=display_df.values,
        colLabels=display_df.columns,
        cellLoc="center",
        bbox=table_bbox,
    )
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 1.35)

    for (row, _column), cell in table.get_celld().items():
        cell.set_edgecolor("#D0D7DE")
        if row == 0:
            cell.set_facecolor("#1F6FEB")
            cell.set_text_props(color="white", weight="bold")
        elif row % 2 == 0:
            cell.set_facecolor("#F6F8FA")
        else:
            cell.set_facecolor("white")

    if title:
        ax.set_title(title, fontsize=14, fontweight="bold", pad=8)

    output.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout(pad=0.5)
    fig.savefig(output, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def setup_japanese_font() -> None:
    candidates = [
        "Yu Gothic",
        "Yu Gothic UI",
        "Meiryo",
        "MS Gothic",
        "Noto Sans CJK JP",
        "Noto Sans JP",
    ]
    available_fonts = {font.name for font in font_manager.fontManager.ttflist}
    for font_name in candidates:
        if font_name in available_fonts:
            plt.rcParams["font.family"] = font_name
            break
    plt.rcParams["axes.unicode_minus"] = False


def main() -> int:
    args = build_parser().parse_args()
    render_csv_to_image(
        args.input,
        args.output,
        title=args.title,
        max_rows=args.max_rows,
    )
    print(f"CSV画像を出力しました: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
