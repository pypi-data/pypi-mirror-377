from __future__ import annotations

from typing import Iterable, Optional

import polars as pl


def _first_match(cols: Iterable[str], candidates: list[str]) -> Optional[str]:
    lower = {c.lower(): c for c in cols}
    for cand in candidates:
        if cand.lower() in lower:
            return lower[cand.lower()]
    return None


def infer_event_study_columns(df: pl.DataFrame) -> dict[str, Optional[str]]:
    """Infer common column names for event study CSVs.

    Returns a dict with keys: time, estimate, lower, upper, se
    Some values may be None if not found.
    """
    cols = df.columns
    time_col = _first_match(
        cols,
        [
            "event_time",
            "k",
            "tau",
            "relative_year",
            "rel_year",
            "period",
            "year_rel",
        ],
    )
    est_col = _first_match(
        cols,
        [
            "estimate",
            "att",
            "att_hat",
            "coef",
            "effect",
            "beta",
            "value",
        ],
    )
    lower_col = _first_match(
        cols,
        [
            "ci_low",
            "ci_lower",
            "conf_low",
            "lower",
            "lwr",
            "lo",
            "lb",
        ],
    )
    upper_col = _first_match(
        cols,
        [
            "ci_high",
            "ci_upper",
            "conf_high",
            "upper",
            "upr",
            "hi",
            "ub",
        ],
    )
    se_col = _first_match(
        cols,
        [
            "se",
            "std_err",
            "std_error",
            "stderr",
            "std",
            "sd",
        ],
    )
    return {
        "time": time_col,
        "estimate": est_col,
        "lower": lower_col,
        "upper": upper_col,
        "se": se_col,
    }


def plot_event_study(
    df: pl.DataFrame,
    *,
    time_col: Optional[str] = None,
    estimate_col: Optional[str] = None,
    lower_col: Optional[str] = None,
    upper_col: Optional[str] = None,
    se_col: Optional[str] = None,
    title: str = "Event Study",
    xlabel: str = "Event time",
    ylabel: str = "Effect",
    ci_level: float = 0.95,
    figsize: tuple[float, float] = (8, 5),
    style: str = "seaborn-v0_8-whitegrid",
    output_path: Optional[str] = None,
) -> None:
    """Render an event-study plot from a DataFrame.

    If lower/upper are missing but se is present, builds symmetric normal-based CIs.
    Requires matplotlib to be installed at runtime.
    """
    import math

    import matplotlib.pyplot as plt

    info = infer_event_study_columns(df)
    time_col = time_col or info["time"]
    estimate_col = estimate_col or info["estimate"]
    lower_col = lower_col or info["lower"]
    upper_col = upper_col or info["upper"]
    se_col = se_col or info["se"]

    if time_col is None or estimate_col is None:
        raise ValueError(
            "Could not infer required columns. Please specify time_col and estimate_col explicitly."
        )

    # Ensure types
    work = df.select(
        pl.col(time_col).cast(pl.Int64).alias("__time__"),
        pl.col(estimate_col).cast(pl.Float64).alias("__est__"),
        *([pl.col(lower_col).cast(pl.Float64).alias("__lo__")] if lower_col else []),
        *([pl.col(upper_col).cast(pl.Float64).alias("__hi__")] if upper_col else []),
        *([pl.col(se_col).cast(pl.Float64).alias("__se__")] if se_col else []),
    ).sort("__time__")

    # Build CIs if needed
    if "__lo__" not in work.columns or "__hi__" not in work.columns:
        if "__se__" in work.columns:
            # Normal-based CI
            # For 95%: z = 1.96, general: z = Phi^{-1}(1 - (1-ci)/2)

            def z_from_ci(ci: float) -> float:
                # Inverse error function approx via binary search on erf to avoid SciPy
                # But we can use a rational approximation for Phi^{-1}
                # Use Peter John Acklam's approximation constants
                # Implemented here for independence from external libs
                a1, a2, a3, a4, a5, a6 = (
                    -39.6968302866538,
                    220.946098424521,
                    -275.928510446969,
                    138.357751867269,
                    -30.6647980661472,
                    2.50662827745924,
                )
                b1, b2, b3, b4, b5 = (
                    -54.4760987982241,
                    161.585836858041,
                    -155.698979859887,
                    66.8013118877197,
                    -13.2806815528857,
                )
                c1, c2, c3, c4, c5, c6 = (
                    -0.00778489400243029,
                    -0.322396458041136,
                    -2.40075827716184,
                    -2.54973253934373,
                    4.37466414146497,
                    2.93816398269878,
                )
                d1, d2, d3, d4 = (
                    0.00778469570904146,
                    0.32246712907004,
                    2.445134137143,
                    3.75440866190742,
                )

                p = 0.5 + ci / 2.0
                if p <= 0 or p >= 1:
                    return float("inf")
                # Define break-points
                plow = 0.02425
                phigh = 1 - plow
                if p < plow:
                    q = math.sqrt(-2 * math.log(p))
                    x = (((((c1 * q + c2) * q + c3) * q + c4) * q + c5) * q + c6) / (
                        (((d1 * q + d2) * q + d3) * q + d4) * q + 1
                    )
                elif phigh < p:
                    q = math.sqrt(-2 * math.log(1 - p))
                    x = -(((((c1 * q + c2) * q + c3) * q + c4) * q + c5) * q + c6) / (
                        (((d1 * q + d2) * q + d3) * q + d4) * q + 1
                    )
                else:
                    q = p - 0.5
                    r = q * q
                    x = (
                        (((((a1 * r + a2) * r + a3) * r + a4) * r + a5) * r + a6)
                        * q
                        / (((((b1 * r + b2) * r + b3) * r + b4) * r + b5) * r + 1)
                    )
                return x

            z = z_from_ci(ci_level)
            work = work.with_columns(
                (pl.col("__est__") - z * pl.col("__se__")).alias("__lo__"),
                (pl.col("__est__") + z * pl.col("__se__")).alias("__hi__"),
            )
        else:
            # Fall back to no CI
            work = work.with_columns(
                pl.lit(None, dtype=pl.Float64).alias("__lo__"),
                pl.lit(None, dtype=pl.Float64).alias("__hi__"),
            )

    x = work["__time__"].to_list()
    y = work["__est__"].to_list()
    lo = work["__lo__"].to_list()
    hi = work["__hi__"].to_list()

    plt.style.use(style)
    fig, ax = plt.subplots(figsize=figsize)
    ax.plot(x, y, marker="o", color="#1f77b4", label="Estimate")
    # CI band when available
    if not all(v is None for v in lo) and not all(v is None for v in hi):
        ax.fill_between(
            x, lo, hi, color="#1f77b4", alpha=0.15, label=f"{int(ci_level * 100)}% CI"
        )

    # Reference lines
    ax.axhline(0, color="black", linewidth=1, alpha=0.6)
    try:
        ax.axvline(0, color="black", linewidth=1, alpha=0.6, linestyle="--")
    except Exception:
        pass

    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.legend(loc="best")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    if output_path:
        fig.tight_layout()
        fig.savefig(output_path, dpi=200)
        plt.close(fig)
    else:
        fig.tight_layout()
        plt.show()


__all__ = ["plot_event_study", "infer_event_study_columns"]
