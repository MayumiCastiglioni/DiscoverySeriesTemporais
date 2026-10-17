"""Create a reproducible, descriptive profile of the five candidate target series.

The script only reads the structural outputs created by
``prepare_structural_data.py``. Its hourly variants for bases 2 and 4 are
explicitly exploratory candidates, not approved modelling datasets. It does
not impute missing values, create model features, tune parameters, or fit a
forecasting model.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import pandas as pd


def optional_float(value: float) -> float | None:
    """Convert a numeric value to a stable JSON value, keeping missing values null."""
    if pd.isna(value):
        return None
    return round(float(value), 6)


def descriptive_statistics(series: pd.Series) -> dict[str, int | float | None]:
    """Return descriptive statistics without changing the supplied series."""
    numeric = pd.to_numeric(series, errors="coerce")
    observed = numeric.dropna()
    lower_quartile, upper_quartile = observed.quantile([0.25, 0.75])
    interquartile_range = upper_quartile - lower_quartile
    tukey_outliers = (
        (observed < lower_quartile - 1.5 * interquartile_range)
        | (observed > upper_quartile + 1.5 * interquartile_range)
    )
    return {
        "non_null": int(observed.shape[0]),
        "missing": int(numeric.isna().sum()),
        "mean": optional_float(observed.mean()),
        "standard_deviation": optional_float(observed.std()),
        "minimum": optional_float(observed.min()),
        "p25": optional_float(lower_quartile),
        "median": optional_float(observed.median()),
        "p75": optional_float(upper_quartile),
        "maximum": optional_float(observed.max()),
        "tukey_outliers": int(tukey_outliers.sum()),
    }


def row_lag_correlations(series: pd.Series, periods: list[int]) -> dict[str, float | None]:
    """Calculate correlations with earlier rows; suitable for regular series."""
    numeric = pd.to_numeric(series, errors="coerce")
    return {str(period): optional_float(numeric.corr(numeric.shift(period))) for period in periods}


def clock_lag_correlations(
    frame: pd.DataFrame,
    value_column: str,
    periods: list[int],
    frequency: str,
) -> dict[str, float | None]:
    """Calculate calendar-aware lag correlations, avoiding accidental gap bridging."""
    indexed = frame.set_index("timestamp")[value_column].sort_index()
    offset = pd.tseries.frequencies.to_offset(frequency)
    correlations: dict[str, float | None] = {}
    for period in periods:
        lagged = indexed.copy()
        lagged.index = lagged.index + offset * period
        paired = pd.concat(
            [indexed.rename("current"), lagged.rename("lag")], axis=1, sort=True
        ).dropna()
        correlations[str(period)] = optional_float(paired["current"].corr(paired["lag"]))
    return correlations


def time_metadata(frame: pd.DataFrame, expected_frequency: str) -> dict[str, Any]:
    timestamps = pd.to_datetime(frame["timestamp"], errors="raise")
    return {
        "rows": int(len(frame)),
        "start": timestamps.min().isoformat(),
        "end": timestamps.max().isoformat(),
        "duplicate_timestamps": int(timestamps.duplicated().sum()),
        "expected_frequency": expected_frequency,
    }


def read_structural_inputs(input_dir: Path) -> dict[int, pd.DataFrame]:
    frames = {}
    for base_id in range(1, 6):
        source = input_dir / f"base{base_id}_structural.csv"
        if not source.exists():
            raise FileNotFoundError(
                f"Structural input not found: {source}. Run prepare_structural_data.py first."
            )
        frames[base_id] = pd.read_csv(source, parse_dates=["timestamp"])
    return frames


def build_profile(frames: dict[int, pd.DataFrame]) -> dict[str, Any]:
    """Profile target candidates while making exploratory aggregations explicit."""
    base_1, base_2, base_3, base_4, base_5 = (frames[index] for index in range(1, 6))

    # The target is identical within repeated Base 2 timestamps. This only creates
    # an exploratory target series; external-variable aggregation remains undecided.
    base_2_hourly_target = (
        base_2.groupby("timestamp", as_index=False)["traffic_volume"].first().sort_values("timestamp")
    )
    expected_base_2_timestamps = pd.date_range(
        base_2_hourly_target["timestamp"].min(),
        base_2_hourly_target["timestamp"].max(),
        freq="h",
    )

    # Base 4 remains stored at ten-minute cadence. The hourly mean is a candidate
    # for a later approval decision, calculated here only to describe the series.
    base_4_hourly_mean = base_4.set_index("timestamp")["T (degC)"].resample("h").mean()

    return {
        "scope": {
            "description": "Descriptive profile of structural data; no modelling or imputation.",
            "base_2_hourly": "Target-only exploratory de-duplication using first identical target per timestamp.",
            "base_4_hourly": "Exploratory mean of available ten-minute temperature readings per hour.",
        },
        "base1": {
            **time_metadata(base_1, "daily"),
            "candidate_target": "Close",
            "statistics": descriptive_statistics(base_1["Close"]),
            "row_lag_correlations": row_lag_correlations(base_1["Close"], [1, 7, 30, 365]),
        },
        "base2": {
            **time_metadata(base_2, "hourly (raw)"),
            "candidate_target": "traffic_volume",
            "duplicate_timestamp_groups": int(base_2.groupby("timestamp").size().gt(1).sum()),
            "exploratory_one_value_per_hour_rows": int(len(base_2_hourly_target)),
            "missing_calendar_hours_after_target_deduplication": int(
                len(expected_base_2_timestamps.difference(base_2_hourly_target["timestamp"]))
            ),
            "statistics_on_exploratory_target_series": descriptive_statistics(
                base_2_hourly_target["traffic_volume"]
            ),
            "clock_lag_correlations": clock_lag_correlations(
                base_2_hourly_target, "traffic_volume", [1, 24, 168], "h"
            ),
        },
        "base3": {
            **time_metadata(base_3, "hourly"),
            "candidate_target": "PM2.5",
            "statistics": descriptive_statistics(base_3["PM2.5"]),
            "clock_lag_correlations": clock_lag_correlations(
                base_3, "PM2.5", [1, 24, 168], "h"
            ),
        },
        "base4": {
            **time_metadata(base_4, "ten minutes (raw)"),
            "candidate_target": "T (degC)",
            "exploratory_hourly_mean_rows": int(len(base_4_hourly_mean)),
            "hours_without_observation": int(base_4_hourly_mean.isna().sum()),
            "statistics_on_exploratory_hourly_mean": descriptive_statistics(base_4_hourly_mean),
            "row_lag_correlations_on_exploratory_hourly_mean": row_lag_correlations(
                base_4_hourly_mean, [1, 24, 168]
            ),
        },
        "base5": {
            **time_metadata(base_5, "trading observations"),
            "candidate_target": "GOLD_PRICE",
            "statistics": descriptive_statistics(base_5["GOLD_PRICE"]),
            "row_lag_correlations": row_lag_correlations(base_5["GOLD_PRICE"], [1, 5, 20, 252]),
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir", type=Path, default=Path("data/processed"))
    parser.add_argument(
        "--output", type=Path, default=Path("reports/generated/initial_series_profile.json")
    )
    args = parser.parse_args()

    profile = build_profile(read_structural_inputs(args.input_dir))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(profile, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(profile, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
