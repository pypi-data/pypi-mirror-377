def cli():
    try:
        import click
    except ImportError as e:
        raise ImportError(
            "⚠️ click is required for the CLI. "
            "Install with: pip install rasterutils[cli]"
        ) from e

    from .reprojection import reproject_images

    @click.command()
    @click.argument("input_folder")
    @click.argument("output_folder")
    @click.option("--dst-crs", default="EPSG:4326", help="Target CRS")
    def _cli(input_folder, output_folder, dst_crs):
        """Reproject all GeoTIFFs in INPUT_FOLDER to OUTPUT_FOLDER."""
        reproject_images(input_folder, output_folder, dst_crs)

    _cli()
