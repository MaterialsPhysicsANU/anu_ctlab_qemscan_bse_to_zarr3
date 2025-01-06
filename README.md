# anu_ctlab_qemscan_bse_to_zarr3

Convert a QEMSCAN BSE pyramid to the Zarr V3 storage format.

Unlike the export functionality available in `nanomin`, this method retains the original data type (e.g. 16-bit).

## Usage (CLI)

```text
 Usage: qemscan_bse_to_zarr3 [OPTIONS] INPUT OUTPUT

 Convert QEMSCAN BSE data to a Zarr V3 image pyramid

╭─ Arguments ────────────────────────────────────────────────────────────────────────────╮
│ *    input       PATH  Input QEMSCAN BSE directory [default: None] [required]          │
│ *    output      PATH  Input Zarr V3 directory [default: None] [required]              │
╰────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Options ──────────────────────────────────────────────────────────────────────────────╮
│ --progress    --no-progress      Print progress [default: no-progress]                 │
│ --help                           Show this message and exit.                           │
╰────────────────────────────────────────────────────────────────────────────────────────╯
```

## TODO
- [ ] output OME-Zarr 0.5 metadata
