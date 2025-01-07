# anu_ctlab_qemscan_bse_to_zarr3

Convert QEMSCAN data to the Zarr V3 storage format with OME-Zarr metadata.
Supports `BSE` and `classification-results` image pyramids.

Unlike the export functionality available in `nanomin`, this method retains the original data type (e.g. 16-bit).

## Installation

```shell
pip install anu-ctlab-qemscan-bse-to-zarr3
```

## Usage (CLI)

```text
 Usage: qemscan_bse_to_zarr3 [OPTIONS] INPUT OUTPUT

 Convert QEMSCAN data to a Zarr V3 image pyramid with OME-Zarr metadata.
 By default, outputs the BSE image. Specify a path in Data/classification-results to output that data.

╭─ Arguments ────────────────────────────────────────────────────────────────────╮
│ *    input       PATH  Input QEMSCAN data directory [default: None] [required] │
│ *    output      PATH  Input Zarr V3 directory [default: None] [required]      │
╰────────────────────────────────────────────────────────────────────────────────╯
╭─ Options ──────────────────────────────────────────────────────────────────────╮
│ --debug    --no-debug      Print debug information [default: no-debug]         │
│ --help                     Show this message and exit.                         │
╰────────────────────────────────────────────────────────────────────────────────╯
```

This tool expects input structured as follows:
```text
SAMPLE_NAME
├── BSE from Nanomin.tif
├── Data
│   ├── BSE
│   ├── classification-results
│   ├── XRayData.db
│   ├── XRayData.isdx
│   └── XRayData.isdx.idx
└── SAMPLE_NAME.MapsMinData
```

If given the `SAMPLE_NAME` path, the tool will automatically convert the data in the `BSE` directory.
For example:
```bash
qemscan_bse_to_zarr3 SAMPLE_NAME output.zarr
```

This tool can also convert images in `classification-results` if the full path is specified.
For example:
```bash
qemscan_bse_to_zarr3 "SAMPLE_NAME/Data/classification-results/Element\ 8" output.zarr
```

Multi-channel image pyramids are not currently supported, such as those in `SAMPLE_NAME/Data/Merged Results`.
