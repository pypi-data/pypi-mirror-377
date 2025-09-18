import os
import glob
from pathlib import Path
import rasterio
from rasterio.warp import calculate_default_transform, reproject, Resampling
from typing import Union

def reproject_images(
    input_folder: Union[str, Path],
    output_folder: Union[str, Path],
    dst_crs: str = "EPSG:4326",
    resampling: Resampling = Resampling.nearest,
) -> None:
    """
    Reproject all GeoTIFF images in a folder to a target CRS.

    Parameters
    ----------
    input_folder : str | Path
        Path to the folder containing input .tif files.
    output_folder : str | Path
        Path where reprojected images will be saved.
    dst_crs : str, default="EPSG:4326"
        Target coordinate reference system (CRS) in EPSG code or PROJ string.
    resampling : rasterio.warp.Resampling, default=Resampling.nearest
        Resampling method to use during reprojection.

    Returns
    -------
    None
    """
    input_folder = Path(input_folder)
    output_folder = Path(output_folder)
    output_folder.mkdir(parents=True, exist_ok=True)

    files_to_reproject = list(input_folder.glob("*.tif"))

    if not files_to_reproject:
        print(f"⚠️ No .tif files found in {input_folder}")
        return

    for fp in files_to_reproject:
        with rasterio.open(fp) as src:
            transform, width, height = calculate_default_transform(
                src.crs, dst_crs, src.width, src.height, *src.bounds
            )

            kwargs = src.meta.copy()
            kwargs.update({
                "crs": dst_crs,
                "transform": transform,
                "width": width,
                "height": height,
            })

            output_fp = output_folder / fp.name
            with rasterio.open(output_fp, "w", **kwargs) as dst:
                for i in range(1, src.count + 1):
                    reproject(
                        source=rasterio.band(src, i),
                        destination=rasterio.band(dst, i),
                        src_transform=src.transform,
                        src_crs=src.crs,
                        dst_transform=transform,
                        dst_crs=dst_crs,
                        resampling=resampling,
                    )

            print(f"✅ Reprojected and saved {output_fp}")
