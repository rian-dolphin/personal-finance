# AIB CSV notes

## Schema
- Cols: Posted Account, Posted Transactions Date, Description1, Description2, Description3, Debit Amount, Credit Amount, Balance, Posted Currency, Transaction Type, Local Currency Amount, Local Currency
- Same schema for current + joint exports
- Header has LEADING SPACE on every col except `Posted Account` and `Balance` (e.g. ` Credit Amount`) -> match exactly when renaming

## Parsing gotchas
- Amounts have thousands separators in quoted fields, e.g. `"2,500.00"` -> polars infers f64 from early rows then fails midway
- Fix: read everything as str (`infer_schema_length=0`), strip `,`, strip whitespace, "" -> null, cast f64
- Amount cols: Debit Amount, Credit Amount, Balance, Local Currency Amount
- Local Currency Amount values have leading space e.g. ` 20.00` -> strip
- Dates `DD/MM/YYYY` (Irish day-first) -> Date
- Empty Debit/Credit when not applicable -> null

## Amount
- Split debit/credit cols, not signed
- Normalized `amount` = credit.fill_null(0) - debit.fill_null(0) (credit +, debit -)
- 3 description cols -> join with space, ignore_nulls, strip
- No fee concept -> normalized fee = 0.0
- No state col -> normalized state = "COMPLETED" (exports all posted)

## Reconciliation
- Check: row.balance == prev.balance + signed_amount (file order)
- current: 0/232 mismatches, clean. file order = chronological (unlike Revolut)
