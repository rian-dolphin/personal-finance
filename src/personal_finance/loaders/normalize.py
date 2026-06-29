import polars as pl

# Columns shared by every normalized transaction frame, in canonical order.
NORMALIZED_COLUMNS = [
    "date",
    "description",
    "amount",
    "fee",
    "currency",
    "balance",
    "transaction_type",
    "state",
    "account",
    "source",
]


def normalize_aib(df: pl.DataFrame, account: str) -> pl.DataFrame:
    """Map a typed AIB frame (from ``load_aib``) onto the common schema.

    AIB splits the value into ``debit_amount`` / ``credit_amount``; here it
    becomes a single signed ``amount`` (credit positive, debit negative).
    """
    return df.select(
        pl.col("transaction_date").alias("date"),
        pl.concat_str(
            ["description_1", "description_2", "description_3"],
            separator=" ",
            ignore_nulls=True,
        )
        .str.strip_chars()
        .alias("description"),
        (pl.col("credit_amount").fill_null(0.0) - pl.col("debit_amount").fill_null(0.0)).alias("amount"),
        pl.lit(0.0).alias("fee"),
        pl.col("currency"),
        pl.col("balance"),
        pl.col("transaction_type"),
        pl.lit("COMPLETED").alias("state"),
        pl.lit(account).alias("account"),
        pl.lit("aib").alias("source"),
    )


def normalize_revolut(df: pl.DataFrame, account: str) -> pl.DataFrame:
    """Map a typed Revolut frame (from ``load_revolut``) onto the common schema.

    Revolut's ``amount`` is the transaction value and ``fee`` is charged on top,
    so the signed balance impact is ``amount - fee``.
    """
    return df.select(
        pl.col("started_date").dt.date().alias("date"),
        pl.col("description"),
        (pl.col("amount") - pl.col("fee")).alias("amount"),
        pl.col("fee"),
        pl.col("currency"),
        pl.col("balance"),
        pl.col("type").alias("transaction_type"),
        pl.col("state"),
        pl.lit(account).alias("account"),
        pl.lit("revolut").alias("source"),
    )
