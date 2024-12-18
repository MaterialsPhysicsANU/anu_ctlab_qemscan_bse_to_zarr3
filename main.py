#!/usr/bin/env python3

import pathlib
from pathlib import Path
from pydantic_xml import BaseXmlModel, element, attr
import tifffile
import numpy as np
import zarr

path = "/home/ljd/Downloads/STD_HemGtQz_1"


def normalise_path(path: Path) -> Path:
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


def parse_pyramid(path: Path) -> Pyramid:
    pyramid = path / "pyramid.xml"
    pyramid = pathlib.Path(pyramid).read_text()
    pyramid = Pyramid.from_xml(pyramid)
    return pyramid


# FIXME: click arguments
def main(path: Path):
    path = normalise_path(path)
    pyramid = parse_pyramid(path)

    # Initialize a Zarr array
    zarr_array = zarr.open_array(
        store="output.zarr",
        mode="w",
        shape=(pyramid.imageset.height, pyramid.imageset.width),
        chunks=(pyramid.imageset.tileHeight, pyramid.imageset.tileWidth),
        dtype=np.uint16,
    )
    # FIXME: OME-Zarr with pixel size metadata

    level = pyramid.imageset.levels - 1
    for c in range(
        0,
        (pyramid.imageset.width + pyramid.imageset.tileWidth - 1)
        // pyramid.imageset.tileWidth,
    ):
        for r in range(
            0,
            (pyramid.imageset.height + pyramid.imageset.tileHeight - 1)
            // pyramid.imageset.tileHeight,
        ):
            tile = eval(f"f'{pyramid.imageset.url}'", {}, {"l": level, "c": c, "r": r})
            print(f"Level {level}, Column {c}, Row {r} -> {tile}")

            # Read the tiff file
            tile = path / tile
            tile = tifffile.imread(tile)
            zarr_array[
                r * pyramid.imageset.tileHeight : (r + 1) * pyramid.imageset.tileHeight,
                c * pyramid.imageset.tileWidth : (c + 1) * pyramid.imageset.tileWidth,
            ] = tile
            print(tile.shape, tile.dtype)

    print(pyramid)

    # largest_level_dir = find_largest_level_dir(path)
    # print(f"Largest directory: {largest_level_dir}")


if __name__ == "__main__":
    main(Path("STD_HemGtQz_1"))

