import math
from pathlib import Path
from typing import Literal

import matplotlib.pyplot as plt
import numpy as np
import polars as pl


def analyze_and_plot_income(
    df: pl.DataFrame,
    income_col: str,
    *,
    year_col: str | None = "year",
    id_col: str | None = None,
    longitudinal_mode: Literal["pooled", "person_median", "person_mean"] = "pooled",
    filter_mode: Literal["none", "non_negative", "central_98"] = "none",
    central_pct: float = 0.98,
    clamp_years: tuple[int, int] | None = None,
    drop_nulls: bool = True,
    log_hist: bool = True,
    outdir: str | None = None,
    title: str | None = None,
) -> dict:
    """
    1. Handles longitudinal data via `longitudinal_mode`:
       - "pooled": each person-year counts as an observation (default).
       - "person_median": collapse to one value per person using median.
       - "person_mean": collapse to one value per person using mean.
    2. Optional filtering via `filter_mode` ("none", "non_negative", or central 98%).
    3. Plots histogram (optionally log-x) for `income_col` after preprocessing.
    4. Computes outlier stats using Tukey fences and robust MAD z-scores.
    5. Returns a dict with thresholds and counts.
    """
    d = df
    if clamp_years and year_col is not None and year_col in d.columns:
        y0, y1 = clamp_years
        d = d.filter(pl.col(year_col).is_between(y0, y1, closed="both"))

    # Optionally collapse to one value per person to avoid overweighting
    if longitudinal_mode in ("person_median", "person_mean"):
        if id_col is None:
            raise ValueError(
                "id_col must be provided when using a person-level longitudinal_mode"
            )
        if longitudinal_mode == "person_median":
            d = d.group_by(id_col).agg(pl.col(income_col).median().alias(income_col))
        else:  # person_mean
            d = d.group_by(id_col).agg(pl.col(income_col).mean().alias(income_col))

    # Optional filtering of the income values
    if filter_mode != "none":
        d = filter_income_values(
            d,
            income_col,
            mode=("central_98" if filter_mode == "central_98" else "non_negative"),
            central_pct=central_pct,
        )

    # Extract the income column as a Series
    s = d.get_column(income_col)

    # Keep finite values only
    vals = pl.Series(
        income_col,
        [v for v in s.to_list() if isinstance(v, (int, float)) and math.isfinite(v)],
    ).cast(pl.Float64)
    if drop_nulls:
        vals = vals.drop_nulls()
    if vals.len() == 0:
        raise ValueError("No valid values to analyze after filtering.")

    # Basic stats
    q1 = vals.quantile(0.25)
    q2 = vals.quantile(0.5)
    q3 = vals.quantile(0.75)
    iqr = q3 - q1 if q3 is not None and q1 is not None else None
    p99 = vals.quantile(0.99)
    p999 = vals.quantile(0.999)
    # Given vals.len() > 0, these statistics should be non-null; assert for mypy
    _mean = vals.mean()
    assert _mean is not None
    mean = _mean
    _std = vals.std()
    assert _std is not None
    std = _std
    _min = vals.min()
    _max = vals.max()
    assert _min is not None and _max is not None
    vmin, vmax = _min, _max

    # Tukey fences
    def _fence(mult: float):
        if iqr is None or q1 is None or q3 is None:
            return (None, None)
        return (q1 - mult * iqr, q3 + mult * iqr)

    lf_15, uf_15 = _fence(1.5)
    lf_30, uf_30 = _fence(3.0)

    # Robust z via MAD
    med = q2
    # Use arithmetic on Series instead of a non-typed subtract()
    mad = (vals - (med if med is not None else 0.0)).abs().median()
    # consistent MAD scale factor for normal
    if mad is not None and mad != 0:
        # narrow type for mypy; median of Float64 series is numeric
        from typing import cast as _cast

        mad_sigma: float | None = 1.4826 * _cast(float, mad)
    else:
        mad_sigma = None

    def robust_z(x: float):
        ms = mad_sigma
        if ms is None or ms == 0:
            return None
        # med is Optional[float], but if it's None, treat as 0 baseline
        m = med if med is not None else 0.0
        return abs((x - m) / ms)

    rz_list = [robust_z(float(x)) for x in vals]
    rz: np.ndarray = np.array([z for z in rz_list if z is not None], dtype=float)
    rz_max = float(rz.max()) if rz.size else None

    # Outlier counts
    def _count_upper(th: float | None) -> int | None:
        if th is None:
            return None
        return int(vals.filter(vals > th).len())

    # Precompute top-tail count size as int for typing clarity
    k = int(max(1, round(vals.len() * 0.001)))

    counts = {
        "n": int(vals.len()),
        "vmin": vmin,
        "q1": (q1 if q1 is not None else None),
        "median": (q2 if q2 is not None else None),
        "q3": (q3 if q3 is not None else None),
        "mean": mean,
        "std": std,
        "p99": (p99 if p99 is not None else None),
        "p999": (p999 if p999 is not None else None),
        "vmax": vmax,
        "upper_fence_1p5iqr": float(uf_15) if uf_15 is not None else None,
        "upper_fence_3iqr": float(uf_30) if uf_30 is not None else None,
        "n_above_1p5iqr": _count_upper(uf_15),
        "n_above_3iqr": _count_upper(uf_30),
        "robust_max_z": rz_max,
        "n_robust_z_gt_5": int((rz > 5).sum()) if rz.size else None,
        "n_top_0p1pct": k,
    }

    # Plot
    if outdir:
        Path(outdir).mkdir(parents=True, exist_ok=True)

    data_for_hist = vals.to_list()
    if log_hist:
        # Keep positive values for log-x plot
        data_for_hist = [x for x in data_for_hist if x > 0]

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.hist(data_for_hist, bins=200, color="#4C78A8", alpha=0.8)
    ax.set_xlabel(income_col + (" (log scale)" if log_hist else ""))
    ax.set_ylabel("Count")
    ax.set_title(title or f"Distribution of {income_col}")
    if log_hist:
        ax.set_xscale("log")

    # Annotate thresholds
    def _vline(x, label, color):
        if x is not None and np.isfinite(x) and x > 0:
            ax.axvline(x, color=color, linestyle="--", linewidth=1.2, label=label)

    _vline(uf_15, "Upper 1.5*IQR", "#E45756")
    _vline(uf_30, "Upper 3*IQR", "#F58518")
    _vline(p99, "99th pct", "#54A24B")
    _vline(p999, "99.9th pct", "#B279A2")
    ax.legend(loc="best", fontsize=8)
    plt.tight_layout()

    if outdir:
        fp = Path(outdir) / f"{income_col}_hist.png"
        fig.savefig(fp, dpi=160)
    else:
        plt.show()
    plt.close(fig)

    # Optional: return a small summary table of the top tail
    top_tail = (
        pl.DataFrame({income_col: vals}).sort(income_col, descending=True).head(k)
    )

    return {"summary": counts, "top_tail": top_tail}


def filter_income_values(
    df: pl.DataFrame,
    income_col: str,
    *,
    mode: Literal["non_negative", "central_98"] = "non_negative",
    central_pct: float = 0.98,
) -> pl.DataFrame:
    """
    Filter a DataFrame by `income_col` using one of two strategies:

    - mode="non_negative": keep rows with non-negative reported income (>= 0).
    - mode="central_98": keep the central `central_pct` fraction (default 98%),
      i.e. drop symmetric tails: [(1-p)/2, 1 - (1-p)/2].

    Returns a new filtered DataFrame.
    """
    if mode == "non_negative":
        return df.filter(pl.col(income_col) >= 0)

    if mode == "central_98":
        if not (0.0 < central_pct < 1.0):
            raise ValueError("central_pct must be in (0, 1)")
        lower = (1.0 - central_pct) / 2.0
        upper = 1.0 - lower

        # Compute quantiles on a clean float Series to get numeric thresholds
        s = df.get_column(income_col).cast(pl.Float64).drop_nulls()
        vals = pl.Series(
            income_col,
            [v for v in s.to_list() if v is not None and math.isfinite(float(v))],
        ).cast(pl.Float64)
        if vals.len() == 0:
            # Nothing to filter; return original
            return df

        ql_opt = vals.quantile(lower)
        qh_opt = vals.quantile(upper)
        if ql_opt is None or qh_opt is None:
            # If quantiles unavailable, leave df unchanged
            return df
        ql: float = ql_opt
        qh: float = qh_opt

        # Filter using ephemeral cast to float for safe comparison
        return df.filter(
            (pl.col(income_col).cast(pl.Float64) >= ql)
            & (pl.col(income_col).cast(pl.Float64) <= qh)
        )

    raise ValueError(f"Unknown mode: {mode}")


def add_log_income(
    df: pl.DataFrame,
    income_col: str,
    *,
    out_col: str | None = None,
) -> pl.DataFrame:
    """
    Add a natural log of income where income > 0; otherwise null.
    Uses Float64 and is safe for zeros/negatives (left as null).
    """
    out = out_col or f"{income_col}_log"
    x = pl.col(income_col).cast(pl.Float64)
    return df.with_columns(pl.when(x > 0).then(x.log()).otherwise(None).alias(out))


def add_ihs_income(
    df: pl.DataFrame,
    income_col: str,
    *,
    out_col: str | None = None,
) -> pl.DataFrame:
    """
    Add the inverse hyperbolic sine transform of income: asinh(y) = ln(y + sqrt(y^2+1)).
    Works for zeros and negatives, using Float64.
    """
    out = out_col or f"{income_col}_ihs"
    x = pl.col(income_col).cast(pl.Float64)
    ihs = (x + (x * x + 1.0).sqrt()).log()
    return df.with_columns(ihs.alias(out))


def assign_baseline_quintiles(
    df: pl.DataFrame,
    *,
    id_col: str,
    income_col: str,
    relative_year_col: str = "RELATIVE_YEAR",
    baseline_year: int = -1,
    out_col: str = "baseline_quintile",
    add_baseline_col: bool = True,
) -> pl.DataFrame:
    """
    Assign each person to a quintile based on their baseline (e.g., t = -1) income.

    - Computes baseline_income per `id_col` at `relative_year_col == baseline_year`.
    - Ranks baseline incomes ascending and assigns quintiles 1..5 with (roughly) equal counts.
    - Joins quintile back to the full DataFrame on `id_col`.
    """
    base = (
        df.filter(pl.col(relative_year_col) == baseline_year)
        .select(
            [pl.col(id_col), pl.col(income_col).cast(pl.Float64).alias("_base_inc")]
        )
        .drop_nulls(["_base_inc"])  # drop missing baseline income
    )
    n = base.height
    if n == 0:
        # No baseline info; return df unchanged
        return df

    ranked = (
        base.with_columns(
            [
                pl.col("_base_inc").rank(method="ordinal").cast(pl.Float64).alias("_r"),
            ]
        )
        .with_columns(
            [
                ((pl.col("_r") - 1.0) * 5.0 / float(n))
                .floor()
                .cast(pl.Int64)
                .alias("_q0"),
            ]
        )
        .with_columns(
            [
                pl.when(pl.col("_q0") < 0)
                .then(0)
                .when(pl.col("_q0") > 4)
                .then(4)
                .otherwise(pl.col("_q0"))
                .cast(pl.Int64)
                .alias("_q0"),
                (pl.col("_base_inc")).alias("baseline_income"),
            ]
        )
        .with_columns([(pl.col("_q0") + 1).alias(out_col)])
    )

    cols_to_keep = [id_col, out_col] + (["baseline_income"] if add_baseline_col else [])
    quint = ranked.select(cols_to_keep)
    return df.join(quint, on=id_col, how="left")


def add_relative_poverty_indicator(
    df: pl.DataFrame,
    *,
    income_col: str,
    year_col: str,
    threshold: float = 0.6,
    out_col: str = "relative_poverty",
) -> pl.DataFrame:
    """
    Add a binary indicator for relative poverty (< threshold × year-median).

    - Computes per-year median of `income_col` and flags rows below `threshold` × median.
    - Default threshold is 0.6, matching the common OECD definition.
    """
    med = df.group_by(year_col).agg(
        pl.col(income_col).median().cast(pl.Float64).alias("_year_median")
    )
    out = df.join(med, on=year_col, how="left").with_columns(
        (
            (pl.col(income_col).cast(pl.Float64) < (threshold * pl.col("_year_median")))
            .cast(pl.Int8)
            .alias(out_col)
        )
    )
    return out.drop("_year_median")
