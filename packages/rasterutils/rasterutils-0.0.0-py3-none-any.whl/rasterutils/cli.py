import click
from .reprojection import reproject_images

@click.command()
@click.argument("input_folder")
@click.argument("output_folder")
@click.option("--dst-crs", default="EPSG:4326", help="Target CRS (default: EPSG:4326)")
def cli(input_folder: str, output_folder: str, dst_crs: str):
    """Reproject all GeoTIFFs in INPUT_FOLDER to OUTPUT_FOLDER."""
    reproject_images(input_folder, output_folder, dst_crs)

if __name__ == "__main__":
    cli()
