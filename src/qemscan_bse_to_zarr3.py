#!/usr/bin/env python3

import pathlib
import os
from pathlib import Path
from pydantic_xml import BaseXmlModel, element, attr
import tifffile
import numpy as np
import zarr
import typer


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


class ImageSet(BaseXmlModel, tag="imageset"):
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


class Metadata(BaseXmlModel, tag="metadata"):
    physicalsize: Size = element()
    pixelsize: Size = element()


class Pyramid(BaseXmlModel, tag="root"):
    imageset: ImageSet = element()
    metadata: Metadata = element()


def _parse_pyramid(path: Path) -> Pyramid:
    pyramid = path / "pyramid.xml"
    pyramid = pathlib.Path(pyramid).read_text()
    pyramid = Pyramid.from_xml(pyramid)
    return pyramid


def _find_first_tif(directory) -> str | None:
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.lower().endswith(".tif"):
                return os.path.join(root, file)
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
    progress: bool,
):
    mip_level = pyramid.imageset.levels - 1 - level
    width = max(pyramid.imageset.width // (2**mip_level), 1)
    height = max(pyramid.imageset.height // (2**mip_level), 1)

    array = zarr.create_array(
        store=str(output / str(mip_level)),
        shape=(height, width),
        chunks=(pyramid.imageset.tileHeight, pyramid.imageset.tileWidth),
        dtype=dtype,
        overwrite=True,
    )

    for c in range(
        (width + pyramid.imageset.tileWidth - 1) // pyramid.imageset.tileWidth,
    ):
        for r in range(
            (height + pyramid.imageset.tileHeight - 1) // pyramid.imageset.tileHeight,
        ):
            tile = eval(f"f'{pyramid.imageset.url}'", {}, {"l": level, "c": c, "r": r})
            if progress:
                print(f"Level {level}, Column {c}, Row {r} -> {tile}")

            # Read the tiff file
            tile = input / tile
            tile = tifffile.imread(tile)
            array[
                r * pyramid.imageset.tileHeight : (r + 1) * pyramid.imageset.tileHeight,
                c * pyramid.imageset.tileWidth : (c + 1) * pyramid.imageset.tileWidth,
            ] = tile
            if progress:
                print(tile.shape, tile.dtype)


def qemscan_bse_to_zarr3(input: Path, output: Path, progress: bool = False):
    input = _normalise_path(input)
    pyramid = _parse_pyramid(input)
    dtype = _get_dtype(input)
    if progress:
        print(pyramid)

    # Create the group
    # TODO: OME-Zarr 0.5 with pixel size metadata https://github.com/ome-zarr-models/ome-zarr-models-py/issues/88
    zarr.create_group(output, overwrite=True)

    for level in range(pyramid.imageset.levels):
        _write_level(
            input=input,
            output=output,
            pyramid=pyramid,
            dtype=dtype,
            level=level,
            progress=progress,
        )


__all__ = ["qemscan_bse_to_zarr3"]


def main():
    typer.run(qemscan_bse_to_zarr3)


if __name__ == "__main__":
    main()
