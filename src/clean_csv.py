from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

from csv_cleaner import MissingColumnsError, clean_dataframe, parse_columns


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="CSVの重複削除、列整理、並び替えを自動化します。"
    )
    parser.add_argument("--input", required=True, help="入力CSVファイルのパス")
    parser.add_argument("--output", required=True, help="出力CSVファイルのパス")
    parser.add_argument(
        "--columns",
        help="残す列名をカンマ区切りで指定します。未指定なら全列を残します。",
    )
    parser.add_argument(
        "--dedupe",
        action="store_true",
        help="完全一致する重複行を削除します。",
    )
    parser.add_argument("--sort-by", help="並び替えに使う列名")
    parser.add_argument(
        "--sort-type",
        choices=["text", "number", "date"],
        default="text",
        help="並び替え列の型",
    )
    parser.add_argument(
        "--sort-order",
        choices=["asc", "desc"],
        default="asc",
        help="並び替え順",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    input_path = Path(args.input)
    output_path = Path(args.output)

    try:
        source_df = pd.read_csv(input_path, encoding="utf-8-sig")
        cleaned_df = clean_dataframe(
            source_df,
            columns=parse_columns(args.columns),
            dedupe=args.dedupe,
            sort_by=args.sort_by,
            sort_type=args.sort_type,
            sort_order=args.sort_order,
        )
    except FileNotFoundError:
        print(f"入力CSVが見つかりません: {input_path}", file=sys.stderr)
        return 1
    except UnicodeDecodeError:
        print(
            f"CSVを読み込めませんでした。UTF-8形式か確認してください: {input_path}",
            file=sys.stderr,
        )
        return 1
    except MissingColumnsError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    except ValueError as exc:
        print(f"CSVの整理に失敗しました: {exc}", file=sys.stderr)
        return 1

    output_path.parent.mkdir(parents=True, exist_ok=True)
    cleaned_df.to_csv(output_path, index=False, encoding="utf-8-sig")

    print(f"整理済みCSVを出力しました: {output_path}")
    print(
        f"行数: {len(source_df)} -> {len(cleaned_df)} / "
        f"列数: {len(source_df.columns)} -> {len(cleaned_df.columns)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
