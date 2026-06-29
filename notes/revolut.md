# Revolut CSV notes

## Schema
- Cols: Type, Product, Started Date, Completed Date, Description, Amount, Fee, Currency, State, Balance
- Same schema for EUR + USD exports
- Amounts clean floats, no thousands separators (unlike AIB)
- Dates ISO `YYYY-MM-DD HH:MM:SS` -> Datetime
- `Completed Date` empty for reverted/pending rows -> null
- `State`: COMPLETED | REVERTED

## Amount / fee
- `Amount` = transaction value (signed), `Fee` charged on top
- Balance impact = `Amount - Fee` (e.g. ATM -46.91, fee 0.47 -> balance moves -47.38)
- Normalized `amount` = Amount - Fee; keep `fee` separate

## Ordering (important)
- Running `Balance` continuous in FILE order, NOT date order
- File not chronological: ~875 rows dated earlier than predecessor
- Sorting by date breaks running balance (4667 mismatches vs 7 in file order)
- => never sort('date') before running-balance calcs; sort on file-position row index if needed

## Reconciliation
- Check: row.balance == prev.balance + signed_amount (file order)
- EUR: 7/10273 mismatches, all internal transfers:
  - "Balance migration to another region", "To pocket EUR ..."
  - interleaved out of position + balance reflects separate sub-ledger (migration rows show balance 0.0)
  - other side lives in a Revolut ledger we don't have CSV for -> not reconcilable, not a loader bug
- amount signs correct everywhere
