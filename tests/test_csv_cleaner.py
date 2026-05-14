from __future__ import annotations

import pandas as pd
import pytest

from csv_data_cleaner import MissingColumnsError, clean_dataframe


def sample_sales_df() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "注文日": "2026-04-03",
                "顧客名": "田中商店",
                "商品名": "ノートPC",
                "数量": 1,
                "金額": "¥120,000",
                "社内メモ": "至急",
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
                "注文日": "2026-04-03",
                "顧客名": "田中商店",
                "商品名": "ノートPC",
                "数量": 1,
                "金額": "¥120,000",
                "社内メモ": "至急",
            },
            {
                "注文日": "2026-04-02",
                "顧客名": "北川物流",
                "商品名": "モニター",
                "数量": 3,
                "金額": "８１，０００",
                "社内メモ": "月末請求",
            },
        ]
    )


def test_removes_duplicate_rows() -> None:
    cleaned = clean_dataframe(sample_sales_df(), dedupe=True)

    assert len(cleaned) == 3


def test_keeps_only_selected_columns() -> None:
    cleaned = clean_dataframe(
        sample_sales_df(),
        columns=["注文日", "顧客名", "商品名", "金額"],
    )

    assert list(cleaned.columns) == ["注文日", "顧客名", "商品名", "金額"]


def test_sorts_by_date_ascending() -> None:
    cleaned = clean_dataframe(
        sample_sales_df(),
        dedupe=True,
        sort_by="注文日",
        sort_type="date",
        sort_order="asc",
    )

    assert list(cleaned["注文日"]) == [
        "2026-04-01",
        "2026-04-02",
        "2026-04-03",
    ]


def test_sorts_by_amount_descending_with_currency_and_full_width_numbers() -> None:
    cleaned = clean_dataframe(
        sample_sales_df(),
        dedupe=True,
        sort_by="金額",
        sort_type="number",
        sort_order="desc",
    )

    assert list(cleaned["金額"]) == ["¥120,000", "８１，０００", "54,000"]


def test_raises_error_for_missing_columns() -> None:
    with pytest.raises(MissingColumnsError) as exc_info:
        clean_dataframe(sample_sales_df(), columns=["注文日", "存在しない列"])

    assert "存在しない列" in str(exc_info.value)


def test_raises_error_for_invalid_number_sort_value() -> None:
    df = pd.DataFrame({"金額": ["100", "要確認"]})

    with pytest.raises(ValueError) as exc_info:
        clean_dataframe(df, sort_by="金額", sort_type="number")

    assert "数値として変換できない値" in str(exc_info.value)
