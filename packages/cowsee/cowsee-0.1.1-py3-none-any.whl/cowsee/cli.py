import argparse

from cowsee.core import display


def main() -> None:
    """Display geometry file data on the console."""
    parser = argparse.ArgumentParser()
    parser.add_argument("file", type=str, help="Geospatial vector file to view (e.g. shapefile)")
    parser.add_argument(
        "-w",
        "--width",
        type=int,
        default=90,
        help="Maximum number of text characters per row on map",
    )

    parser.add_argument("-n", "--no-cow", action="store_true", help="Don't show cow")

    # the simplify ratio can help results look cleaner, depending on their geometric complexity
    parser.add_argument(
        "-s",
        "--simplify-ratio",
        default=0.25,
        type=float,
        help="Ratio that defines the amount lines and polygons are simplified. "
        "Simplification threshold = {character width in GIS} * {simplify ratio}.",
    )

    args = parser.parse_args()

    display(
        file=args.file,
        map_row_width=args.width,
        has_cow=not args.no_cow,
        simplify_ratio=args.simplify_ratio,
    )
