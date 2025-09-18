import tempfile
from pathlib import Path
import rasterio
from rasterutils.reprojection import reproject_images

def test_reproject_images(tmp_path: Path):
    input_folder = Path(r"C:\Users\LENOVO\Downloads\25")
    output_folder = tmp_path / "out"

    reproject_images(input_folder, output_folder, dst_crs="EPSG:4326")

    outputs = list(output_folder.glob("*.tif"))
    assert len(outputs) > 0

    # Check CRS of first output file
    with rasterio.open(outputs[0]) as src:
        assert src.crs.to_string() == "EPSG:4326"
