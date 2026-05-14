from __future__ import annotations

import re
import unicodedata
from typing import Literal, Sequence

import pandas as pd

SortOrder = Literal["asc", "desc"]
SortType = Literal["text", "number", "date"]


class MissingColumnsError(ValueError):
    """Raised when a requested CSV column is not present."""

    def __init__(self, missing_columns: Sequence[str]) -> None:
        self.missing_columns = list(missing_columns)
        names = ", ".join(self.missing_columns)
        super().__init__(f"指定された列がCSVにありません: {names}")


def parse_columns(value: str | None) -> list[str] | None:
    """Parse comma-separated column names from CLI input."""
    if value is None or value.strip() == "":
        return None

    columns = [column.strip() for column in value.split(",")]
    return [column for column in columns if column]


def clean_dataframe(
    df: pd.DataFrame,
    *,
    columns: Sequence[str] | None = None,
    dedupe: bool = False,
    sort_by: str | None = None,
    sort_type: SortType = "text",
    sort_order: SortOrder = "asc",
) -> pd.DataFrame:
    """Clean a CSV DataFrame by deduplicating, sorting, and selecting columns."""
    if sort_order not in ("asc", "desc"):
        raise ValueError("sort_order must be 'asc' or 'desc'")

    if sort_type not in ("text", "number", "date"):
        raise ValueError("sort_type must be 'text', 'number', or 'date'")

    work = df.copy()
    requested_columns = list(columns or [])
    if sort_by:
        requested_columns.append(sort_by)
    _validate_columns(work, requested_columns)

    if dedupe:
        work = work.drop_duplicates()

    if sort_by:
        work = _sort_dataframe(work, sort_by, sort_type, sort_order)

    if columns is not None:
        work = work.loc[:, list(columns)]

    return work.reset_index(drop=True)


def _validate_columns(df: pd.DataFrame, requested_columns: Sequence[str]) -> None:
    missing_columns = [
        column
        for column in dict.fromkeys(requested_columns)
        if column not in df.columns
    ]
    if missing_columns:
        raise MissingColumnsError(missing_columns)


def _sort_dataframe(
    df: pd.DataFrame,
    sort_by: str,
    sort_type: SortType,
    sort_order: SortOrder,
) -> pd.DataFrame:
    return df.sort_values(
        by=sort_by,
        ascending=sort_order == "asc",
        kind="mergesort",
        key=lambda series: _build_sort_key(series, sort_type),
    )


def _build_sort_key(series: pd.Series, sort_type: SortType) -> pd.Series:
    if sort_type == "number":
        return _build_number_sort_key(series)

    if sort_type == "date":
        return _build_date_sort_key(series)

    return series.astype(str)


def _build_number_sort_key(series: pd.Series) -> pd.Series:
    normalized = series.map(_normalize_number_text)
    converted = pd.to_numeric(normalized, errors="coerce")
    invalid_mask = normalized.notna() & converted.isna()

    if invalid_mask.any():
        examples = ", ".join(series[invalid_mask].astype(str).unique()[:5])
        raise ValueError(f"数値として変換できない値があります: {examples}")

    return converted


def _normalize_number_text(value: object) -> str | None:
    if pd.isna(value):
        return None

    text = unicodedata.normalize("NFKC", str(value)).strip()
    if text == "" or text.lower() in {"nan", "none", "null"}:
        return None

    text = re.sub(r"(?i)jpy", "", text)
    text = re.sub(r"[,\s¥￥円$]", "", text)
    return text or None


def _build_date_sort_key(series: pd.Series) -> pd.Series:
    converted = pd.to_datetime(series, errors="coerce")
    invalid_mask = series.notna() & (series.astype(str).str.strip() != "") & converted.isna()

    if invalid_mask.any():
        examples = ", ".join(series[invalid_mask].astype(str).unique()[:5])
        raise ValueError(f"日付として変換できない値があります: {examples}")

    return converted
