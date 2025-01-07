#!/usr/bin/env python3

import pathlib
import os
from pathlib import Path
from pydantic_xml import BaseXmlModel, element, attr
import tifffile
import numpy as np
import zarr
import typer
from typing_extensions import Annotated


def _normalise_path(path: Path) -> Path:
    Data_dir = path / "Data"
    if Data_dir.exists() and Data_dir.is_dir():
        path = Data_dir
    bse_dir = path / "BSE"
    if bse_dir.exists() and bse_dir.is_dir():
        path = bse_dir
    data_dir = path / "data"
    if data_dir.exists() and data_dir.is_dir():
        path = data_dir
    return path


class ImageSet(BaseXmlModel, tag="imageset"):  # type: ignore
    url: str = attr()
    levels: int = attr()
    width: int = attr()
    height: int = attr()
    tileWidth: int = attr()
    tileHeight: int = attr()
    tileOverlap: int = attr()


class Size(BaseXmlModel):
    x: float = element()
    y: float = element()


class Metadata(BaseXmlModel, tag="metadata"):  # type: ignore
    physicalsize: Size = element()
    pixelsize: Size = element()


class Pyramid(BaseXmlModel, tag="root"):  # type: ignore
    imageset: ImageSet = element()
    metadata: Metadata | None = element(default=None)


def _parse_pyramid(path: Path) -> Pyramid:
    pyramid_path = path / "pyramid.xml"
    pyramid_xml = pathlib.Path(pyramid_path).read_text()
    pyramid: Pyramid = Pyramid.from_xml(pyramid_xml)
    return pyramid


def _find_first_tif(directory) -> str | None:
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.lower().endswith(".tif"):
                return str(os.path.join(root, file))
    return None


def _get_dtype(input: Path) -> np.dtype:
    tif_path = _find_first_tif(input)
    if tif_path is not None:
        with tifffile.TiffFile(tif_path) as tiff:
            return tiff.pages[0].dtype
    return None


def _write_level(
    input: Path,
    output: Path,
    pyramid: Pyramid,
    level: int,
    dtype: np.dtype,
    *,
    debug: bool,
) -> None:
    mip_level = pyramid.imageset.levels - 1 - level
    width = max(pyramid.imageset.width // (2**mip_level), pyramid.imageset.tileWidth)
    height = max(pyramid.imageset.height // (2**mip_level), pyramid.imageset.tileHeight)

    array = zarr.create_array(
        store=str(output / str(mip_level)),
        shape=(height, width),
        chunks=(pyramid.imageset.tileHeight, pyramid.imageset.tileWidth),
        dtype=dtype,
        overwrite=True,
        dimension_names=["y", "x"],
    )

    for c in range(
        (width + pyramid.imageset.tileWidth - 1) // pyramid.imageset.tileWidth,
    ):
        for r in range(
            (height + pyramid.imageset.tileHeight - 1) // pyramid.imageset.tileHeight,
        ):
            tile = eval(f"f'{pyramid.imageset.url}'", {}, {"l": level, "c": c, "r": r})
            if debug:
                print(f"Level {level}, Column {c}, Row {r} -> {tile}")

            # Read the tiff file
            tile = input / tile
            try:
                tile = tifffile.imread(tile)
                array[
                    r * pyramid.imageset.tileHeight : (r + 1)
                    * pyramid.imageset.tileHeight,
                    c * pyramid.imageset.tileWidth : (c + 1)
                    * pyramid.imageset.tileWidth,
                ] = tile
                if debug:
                    print(tile.shape, tile.dtype)
            except FileNotFoundError:
                if debug:
                    print(tile, "not found, empty?")


def qemscan_bse_to_zarr3(
    input: Annotated[Path, typer.Argument(help="Input QEMSCAN data directory")],
    output: Annotated[Path, typer.Argument(help="Input Zarr V3 directory")],
    debug: Annotated[bool, typer.Option(help="Print debug information")] = False,
) -> Pyramid:
    """Convert QEMSCAN data to a Zarr V3 image pyramid with OME-Zarr metadata.

    By default, outputs the BSE image.
    Specify a path in Data/classification-results to output that data.
    """
    input = _normalise_path(input)
    pyramid = _parse_pyramid(input)
    dtype = _get_dtype(input)
    if debug:
        print(pyramid)

    # Create the group with minimal OME-Zarr 0.5 metadata
    ome_zarr_datasets = [
        {
            "path": str(level),
            "coordinateTransformations": [
                {"type": "scale", "scale": [2.0**level, 2.0**level]},
                {
                    "type": "translation",
                    "translation": [(2.0**level - 1.0) * 0.5, (2.0**level - 1.0) * 0.5],
                },
            ],
        }
        for level in range(pyramid.imageset.levels)
    ]
    if pyramid.metadata:
        scale = [
            pyramid.metadata.pixelsize.y,
            pyramid.metadata.pixelsize.x,
        ]
    else:
        scale = [1.0, 1.0]
    ome_zarr_metadata = {
        "ome": {
            "version": "0.5",
            "multiscales": [
                {
                    "axes": [
                        {"name": "y", "type": "space", "unit": "meter"},
                        {"name": "x", "type": "space", "unit": "meter"},
                    ],
                    "datasets": ome_zarr_datasets,
                    "coordinateTransformations": [
                        {
                            "type": "scale",
                            "scale": scale,
                        }
                    ],
                }
            ],
        }
    }
    zarr.create_group(output, overwrite=True, attributes=ome_zarr_metadata)

    for level in range(pyramid.imageset.levels):
        _write_level(
            input=input,
            output=output,
            pyramid=pyramid,
            dtype=dtype,
            level=level,
            debug=debug,
        )

    return pyramid


__all__ = ["qemscan_bse_to_zarr3"]


def main() -> None:
    typer.run(qemscan_bse_to_zarr3)


if __name__ == "__main__":
    main()
