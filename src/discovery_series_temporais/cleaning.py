"""Create traceable cleaned datasets and diagnostics for the five project bases.

The frozen raw CSVs are never modified. Structural inputs are read from
``data/processed`` and each cleaned output is written separately as
``base<N>_cleaned.csv``. No imputation is performed here.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd


TARGET_NAMES = {
    1: "Close",
    2: "traffic_volume",
    3: "PM2.5",
    4: "T (degC)",
    5: "GOLD_PRICE",
}
STEP_DELTAS = {
    1: pd.Timedelta(days=1),
    2: pd.Timedelta(hours=1),
    3: pd.Timedelta(hours=1),
    4: pd.Timedelta(hours=1),
    5: pd.Timedelta(days=7),
}
STL_PERIODS = {1: 7, 2: 24, 3: 24, 4: 24, 5: 52}
ACF_LAGS = {1: 60, 2: 336, 3: 336, 4: 336, 5: 104}


@dataclass(frozen=True)
class CleaningSummary:
    """Audit information returned after a cleaned dataset is built."""

    base_id: int
    target_name: str
    rows: int
    columns: int
    missing_target: int
    output_path: Path
    actions: tuple[str, ...]


@dataclass(frozen=True)
class DiagnosticSegment:
    """A complete regular segment used for ACF and STL diagnostics."""

    base_id: int
    data: pd.DataFrame
    seasonal_period: int
    acf_lags: int
    diagnostic_interpolated_values: int


def _deterministic_mode(values: pd.Series) -> object:
    """Return the lexicographically first mode without inventing missing data."""
    observed = values.dropna()
    if observed.empty:
        return np.nan
    counts = observed.astype(str).value_counts()
    return sorted(counts[counts.eq(counts.max())].index)[0]


def _clean_base_1(frame: pd.DataFrame) -> tuple[pd.DataFrame, tuple[str, ...]]:
    columns = ["timestamp", "Close", "Open", "High", "Low", "Volume"]
    cleaned = frame.loc[:, columns].rename(columns={"Close": "target"}).copy()
    return cleaned, (
        "retained daily OHLCV values",
        "renamed Close to the standard target column",
        "excluded Adj Close because it duplicates Close in the supplied data",
    )


def _clean_base_2(frame: pd.DataFrame) -> tuple[pd.DataFrame, tuple[str, ...]]:
    target_counts = frame.groupby("timestamp")["traffic_volume"].nunique(dropna=False)
    if (target_counts > 1).any():
        raise ValueError("Base 2 has repeated timestamps with divergent traffic_volume values.")

    numeric_columns = ["temp", "rain_1h", "snow_1h", "clouds_all"]
    categorical_columns = ["holiday", "weather_main", "weather_description"]
    grouped = frame.groupby("timestamp", sort=True)
    cleaned = grouped[numeric_columns].mean()
    for column in categorical_columns:
        cleaned[column] = grouped[column].agg(_deterministic_mode)
    cleaned["target"] = grouped["traffic_volume"].first()
    cleaned = cleaned.reset_index()
    cleaned = cleaned.loc[:, ["timestamp", "target", *numeric_columns, *categorical_columns]]
    return cleaned, (
        "verified that repeated traffic_volume values agree within each timestamp",
        "consolidated continuous external variables by arithmetic mean",
        "consolidated categorical external variables by deterministic mode with lexicographic tie-break",
    )


def _clean_base_3(frame: pd.DataFrame) -> tuple[pd.DataFrame, tuple[str, ...]]:
    excluded = {"timestamp", "No", "year", "month", "day", "hour", "PM2.5", "station"}
    external_columns = [column for column in frame.columns if column not in excluded]
    cleaned = frame.loc[:, ["timestamp", "PM2.5", *external_columns]].rename(
        columns={"PM2.5": "target"}
    )
    return cleaned, (
        "retained the hourly target and observed external variables",
        "preserved target and external missing values for fold-safe treatment later",
        "excluded row identifier, timestamp components, and constant station label",
    )


def _clean_base_4(frame: pd.DataFrame) -> tuple[pd.DataFrame, tuple[str, ...]]:
    numeric_columns = [column for column in frame.columns if column not in {"timestamp", "wd (deg)"}]
    prepared = frame.loc[:, ["timestamp", *numeric_columns, "wd (deg)"]].copy()
    direction_radians = np.deg2rad(prepared.pop("wd (deg)"))
    prepared["wind_direction_sin"] = np.sin(direction_radians)
    prepared["wind_direction_cos"] = np.cos(direction_radians)
    hourly = prepared.set_index("timestamp").resample("h").mean().reset_index()
    hourly = hourly.rename(columns={"T (degC)": "target"})
    ordered = ["timestamp", "target", *[column for column in hourly.columns if column not in {"timestamp", "target"}]]
    return hourly.loc[:, ordered], (
        "aggregated valid ten-minute numeric readings by hourly arithmetic mean",
        "encoded wind direction as sine and cosine before aggregation to avoid an invalid arithmetic angle mean",
        "preserved hours without valid readings as missing values",
    )


def _clean_base_5(frame: pd.DataFrame) -> tuple[pd.DataFrame, tuple[str, ...]]:
    columns = ["GOLD_PRICE", "TREASURY_10Y", "FED_FUNDS_RATE"]
    weekly = frame.set_index("timestamp")[columns].resample("W-FRI").last().reset_index()
    weekly = weekly.rename(columns={"GOLD_PRICE": "target"})
    return weekly, (
        "resampled to Friday-ended weeks using the final observed value in each week",
        "preserved weeks without an observed price as missing",
        "excluded all supplied precomputed calendar, lag, rolling, and TARGET columns",
    )


CLEANERS = {
    1: _clean_base_1,
    2: _clean_base_2,
    3: _clean_base_3,
    4: _clean_base_4,
    5: _clean_base_5,
}


def build_cleaned_dataset(
    base_id: int,
    processed_dir: Path = Path("data/processed"),
    output_dir: Path | None = None,
) -> tuple[pd.DataFrame, CleaningSummary]:
    """Build and persist one cleaned dataset from its structural input."""
    if base_id not in CLEANERS:
        raise ValueError("base_id must be an integer from 1 to 5.")
    source = processed_dir / f"base{base_id}_structural.csv"
    if not source.exists():
        raise FileNotFoundError(f"Structural input not found: {source}")
    frame = pd.read_csv(source, parse_dates=["timestamp"])
    cleaned, actions = CLEANERS[base_id](frame)
    cleaned = cleaned.sort_values("timestamp", kind="stable").reset_index(drop=True)
    if cleaned["timestamp"].duplicated().any():
        raise ValueError(f"Base {base_id}: cleaned timestamps must be unique.")
    if output_dir is None:
        output_dir = processed_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    destination = output_dir / f"base{base_id}_cleaned.csv"
    cleaned.to_csv(destination, index=False)
    return cleaned, CleaningSummary(
        base_id=base_id,
        target_name=TARGET_NAMES[base_id],
        rows=len(cleaned),
        columns=cleaned.shape[1],
        missing_target=int(cleaned["target"].isna().sum()),
        output_path=destination,
        actions=actions,
    )


def build_all_cleaned_datasets(
    processed_dir: Path = Path("data/processed"), output_dir: Path | None = None
) -> list[CleaningSummary]:
    """Build all five cleaned datasets in a deterministic order."""
    return [build_cleaned_dataset(base_id, processed_dir, output_dir)[1] for base_id in range(1, 6)]


def load_cleaned_dataset(base_id: int, processed_dir: Path = Path("data/processed")) -> pd.DataFrame:
    """Load a previously generated cleaned dataset without altering it."""
    source = processed_dir / f"base{base_id}_cleaned.csv"
    if not source.exists():
        raise FileNotFoundError(
            f"Cleaned input not found: {source}. Run the base exploration notebook first."
        )
    frame = pd.read_csv(source, parse_dates=["timestamp"])
    required = {"timestamp", "target"}
    if not required.issubset(frame.columns):
        raise ValueError(f"Base {base_id}: cleaned input must include {sorted(required)}.")
    return frame.sort_values("timestamp", kind="stable").reset_index(drop=True)


def select_diagnostic_segment(cleaned: pd.DataFrame, base_id: int) -> DiagnosticSegment:
    """Select the longest complete, regular target segment for ACF and STL.

    This avoids filling a target merely to make a diagnostic plot possible.
    """
    frame = cleaned.loc[:, ["timestamp", "target"]].sort_values("timestamp", kind="stable").reset_index(drop=True)
    if frame["timestamp"].duplicated().any():
        raise ValueError("Diagnostic input must have unique timestamps.")
    expected_delta = STEP_DELTAS[base_id]
    complete = frame["target"].notna()
    previous_complete = complete.shift(fill_value=False)
    contiguous = frame["timestamp"].diff().eq(expected_delta)
    starts_new_segment = ~(complete & previous_complete & contiguous)
    starts_new_segment.iloc[0] = not bool(complete.iloc[0])
    segment_id = starts_new_segment.cumsum()
    candidate_segments = []
    for _, segment in frame.loc[complete].groupby(segment_id.loc[complete]):
        if len(segment) > 1:
            candidate_segments.append(segment)
    if not candidate_segments:
        raise ValueError(f"Base {base_id}: no complete regular target segment is available.")
    selected = max(candidate_segments, key=len).reset_index(drop=True)
    period = STL_PERIODS[base_id]
    interpolated_values = 0
    if len(selected) < 2 * period:
        # Base 5 has many scattered empty weekly bins. A separate, descriptive
        # copy is interpolated only when no complete segment can support STL.
        # The cleaned dataset retains all missing values and is the only input
        # allowed for models and validation.
        diagnostic_copy = frame.set_index("timestamp")["target"].interpolate(
            method="time", limit_area="inside"
        )
        if diagnostic_copy.isna().any() or len(diagnostic_copy) < 2 * period:
            raise ValueError(
                f"Base {base_id}: no complete segment can support STL period {period}, "
                "and a diagnostic-only interpolation could not form a complete series."
            )
        interpolated_values = int(frame["target"].isna().sum())
        selected = diagnostic_copy.rename("target").reset_index()
    return DiagnosticSegment(
        base_id=base_id,
        data=selected,
        seasonal_period=period,
        acf_lags=min(ACF_LAGS[base_id], len(selected) // 2 - 1),
        diagnostic_interpolated_values=interpolated_values,
    )


def plot_cleaned_diagnostics(cleaned: pd.DataFrame, base_id: int, output_dir: Path) -> DiagnosticSegment:
    """Save target, ACF, and STL plots for one cleaned dataset."""
    import matplotlib.pyplot as plt
    from statsmodels.graphics.tsaplots import plot_acf
    from statsmodels.tsa.seasonal import STL

    output_dir.mkdir(parents=True, exist_ok=True)
    segment = select_diagnostic_segment(cleaned, base_id)
    series = segment.data.set_index("timestamp")["target"].astype(float)

    figure, axis = plt.subplots(figsize=(12, 4))
    axis.plot(series.index, series.values, linewidth=0.8)
    axis.set(title=f"Base {base_id}: segmento usado nos diagnósticos", xlabel="Tempo", ylabel="Alvo")
    figure.tight_layout()
    figure.savefig(output_dir / "serie_alvo_segmento.png", dpi=150)

    acf_figure, acf_axis = plt.subplots(figsize=(12, 4))
    plot_acf(series, lags=segment.acf_lags, ax=acf_axis)
    acf_axis.set_title(f"Base {base_id}: ACF do segmento completo")
    acf_figure.tight_layout()
    acf_figure.savefig(output_dir / "acf.png", dpi=150)

    result = STL(series, period=segment.seasonal_period, robust=True).fit()
    stl_figure = result.plot()
    stl_figure.set_size_inches(12, 8)
    note = ""
    if segment.diagnostic_interpolated_values:
        note = f"; cópia diagnóstica com {segment.diagnostic_interpolated_values} lacunas interpoladas"
    stl_figure.suptitle(
        f"Base {base_id}: STL (período sazonal = {segment.seasonal_period}{note})", y=1.01
    )
    stl_figure.tight_layout()
    stl_figure.savefig(output_dir / "stl.png", dpi=150, bbox_inches="tight")
    plt.show()
    return segment
