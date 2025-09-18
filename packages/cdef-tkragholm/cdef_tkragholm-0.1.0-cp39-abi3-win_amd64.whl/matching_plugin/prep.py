from __future__ import annotations

import polars as pl


def _find_alias(df: pl.DataFrame, candidates: list[str]) -> str | None:
    cols_lower = {c.lower(): c for c in df.columns}
    for name in candidates:
        if name in df.columns:
            return name
        if name.lower() in cols_lower:
            return cols_lower[name.lower()]
    return None


def prepare_matching_input(mfr_df: pl.DataFrame, lpr_df: pl.DataFrame) -> pl.DataFrame:
    """
    Prepare a matching input DataFrame that includes SCD_STATUS and SCD_DATE.

    Accepts common aliases for identifiers and index/date columns, normalizes to:
    - PNR (child identifier)
    - SCD_STATUS ("SCD" or "NO_SCD")
    - SCD_DATE (pl.Date)

    Parameters
    ----------
    mfr_df : pl.DataFrame
        Population DataFrame (e.g., MFR) with at least a child identifier column
    lpr_df : pl.DataFrame
        Diagnoses DataFrame (e.g., LPR) containing SCD status and/or diagnosis dates

    Returns
    -------
    pl.DataFrame
        mfr_df joined with LPR-derived SCD_STATUS and SCD_DATE; missing SCD is filled as NO_SCD
    """
    # Identify columns (accept common aliases)
    pnr_mfr = _find_alias(mfr_df, ["PNR", "CPR", "id", "child_pnr"]) or "PNR"
    pnr_lpr = _find_alias(lpr_df, ["PNR", "CPR", "id", "child_pnr"]) or "PNR"
    scd_date = _find_alias(
        lpr_df, ["SCD_DATE", "INDEX_DATE", "diagnosis_date", "scd_date", "index_date"]
    )
    scd_status = _find_alias(lpr_df, ["SCD_STATUS", "scd_status"])

    if scd_date is None and scd_status is None:
        raise ValueError("LPR missing SCD columns (need SCD_DATE and/or SCD_STATUS)")

    # Build normalized LPR view
    lpr_cols: list[pl.Expr] = [pl.col(pnr_lpr).alias("PNR")]
    if scd_status is not None:
        lpr_cols.append(pl.col(scd_status).alias("SCD_STATUS"))
    if scd_date is not None:
        lpr_cols.append(pl.col(scd_date).alias("SCD_DATE"))

    lpr_view = lpr_df.select(lpr_cols)

    # If SCD_STATUS missing, derive from SCD_DATE
    if "SCD_STATUS" not in lpr_view.columns:
        lpr_view = lpr_view.with_columns(
            pl.when(pl.col("SCD_DATE").is_not_null())
            .then(pl.lit("SCD"))
            .otherwise(pl.lit("NO_SCD"))
            .alias("SCD_STATUS")
        )

    # Ensure SCD_DATE type is Date (parse flexible strings)
    if "SCD_DATE" in lpr_view.columns and lpr_view.schema.get("SCD_DATE") not in (
        pl.Date,
        pl.Datetime,
    ):
        lpr_view = lpr_view.with_columns(
            pl.col("SCD_DATE").str.strptime(pl.Date, strict=False, exact=False)
        )

    # Normalize MFR PNR and join
    mfr_norm = mfr_df.rename({pnr_mfr: "PNR"}) if pnr_mfr != "PNR" else mfr_df
    combined = mfr_norm.join(lpr_view, on="PNR", how="left").with_columns(
        pl.col("SCD_STATUS").fill_null("NO_SCD")
    )
    return combined
