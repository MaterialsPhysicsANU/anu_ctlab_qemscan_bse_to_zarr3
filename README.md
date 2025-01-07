# anu_ctlab_qemscan_bse_to_zarr3

Convert a QEMSCAN BSE pyramid to the Zarr V3 storage format with OME-Zarr metadata.

Unlike the export functionality available in `nanomin`, this method retains the original data type (e.g. 16-bit).

## Installation

```shell
pip install anu-ctlab-qemscan-bse-to-zarr3
```

## Usage (CLI)

```text
 Usage: qemscan_bse_to_zarr3 [OPTIONS] INPUT OUTPUT

 Convert QEMSCAN BSE data to a Zarr V3 image pyramid with OME-Zarr metadata

╭─ Arguments ───────────────────────────────────────────────────────────────────╮
│ *    input       PATH  Input QEMSCAN BSE directory [default: None] [required] │
│ *    output      PATH  Input Zarr V3 directory [default: None] [required]     │
╰───────────────────────────────────────────────────────────────────────────────╯
╭─ Options ─────────────────────────────────────────────────────────────────────╮
│ --debug    --no-debug      Print debug information [default: no-debug]        │
│ --help                     Show this message and exit.                        │
╰───────────────────────────────────────────────────────────────────────────────╯
```
