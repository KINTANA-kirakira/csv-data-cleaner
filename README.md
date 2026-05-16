# CSV Data Cleaner

CSVデータの重複削除、列整理、並び替えを自動化するPythonツールです。売上データ、顧客リスト、商品一覧などの事務作業を効率化する目的で制作しました。

## Features

- CSVファイルを読み込み、整理済みCSVとして出力
- 完全一致する重複行を削除
- 必要な列だけを指定して出力
- 日付、金額、テキストの並び替えに対応
- 実行前後のCSVをPNG画像として出力
- installable package構成とpytestによるテストを含む

## Files

```text
csv-data-cleaner/
├── README.md
├── pyproject.toml
├── requirements.txt
├── samples/
│   ├── sales_raw.csv
│   └── sales_cleaned.csv
├── docs/
│   └── images/
│       ├── before.png
│       └── after.png
├── src/
│   ├── clean_csv.py
│   ├── render_csv_image.py
│   └── csv_data_cleaner/
│       ├── __init__.py
│       ├── cli.py
│       ├── csv_cleaner.py
│       └── render_csv_image.py
└── tests/
    ├── test_cli.py
    ├── test_csv_cleaner.py
    └── test_render_csv_image.py
```

## Setup

Windows PowerShell:

```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

macOS / Linux:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

開発・テスト用にパッケージとしてインストールする場合:

```bash
pip install -e ".[dev]"
```

## Usage

サンプル売上データを整理します。

```bash
python src/clean_csv.py --input samples/sales_raw.csv --output samples/sales_cleaned.csv --columns "注文日,顧客名,商品名,数量,金額" --dedupe --sort-by "注文日" --sort-type date --sort-order asc
```

パッケージとしてインストールした場合は、次のコマンドでも実行できます。

```bash
csv-data-cleaner --input samples/sales_raw.csv --output samples/sales_cleaned.csv --columns "注文日,顧客名,商品名,数量,金額" --dedupe --sort-by "注文日" --sort-type date --sort-order asc
```

金額が高い順に並び替える場合:

```bash
python src/clean_csv.py --input samples/sales_raw.csv --output samples/sales_cleaned.csv --columns "注文日,顧客名,商品名,数量,金額" --dedupe --sort-by "金額" --sort-type number --sort-order desc
```

## Generate Evidence Images

```bash
python src/render_csv_image.py --input samples/sales_raw.csv --output docs/images/before.png --title "実行前CSV"
python src/render_csv_image.py --input samples/sales_cleaned.csv --output docs/images/after.png --title "実行後CSV"
```

## Before / After

![実行前CSV](docs/images/before.png)

![実行後CSV](docs/images/after.png)

## CLI Options

| Option | Required | Description |
| --- | --- | --- |
| `--input` | Yes | 入力CSVファイルのパス |
| `--output` | Yes | 出力CSVファイルのパス |
| `--columns` | No | 残す列名をカンマ区切りで指定 |
| `--dedupe` | No | 完全一致する重複行を削除 |
| `--sort-by` | No | 並び替え対象の列名 |
| `--sort-type` | No | `text`, `number`, `date` のいずれか |
| `--sort-order` | No | `asc` または `desc` |

## Sort Rules

- `text`: 文字列として並び替えます。
- `number`: カンマ、円記号、`JPY`、空白、全角数字を正規化して数値化します。空欄は欠損値として扱い、変換できない値がある場合はエラーにします。
- `date`: `pandas.to_datetime`で日付として解釈します。不正日付や解釈できない混在フォーマットがある場合はエラーにします。

## Test

```bash
pytest
```

テストでは、重複削除、列選択、日付ソート、金額ソート、存在しない列のエラー、CLIの正常系・異常系を確認しています。

## Portfolio Note

この作品は、CSV整理作業をPythonで自動化できることを示すためのポートフォリオです。README、Pythonコード、サンプルCSV、実行前後画像、テストコードを含めているため、GitHub上で成果物として確認しやすい構成にしています。
