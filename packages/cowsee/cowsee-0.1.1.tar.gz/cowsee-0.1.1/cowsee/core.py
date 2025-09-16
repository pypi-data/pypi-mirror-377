import geopandas as gpd

from cowsee.drawing import Drawing
from cowsee.geometry import calculate_cell_symbols
from cowsee.grid import Grid


def display(file: str, map_row_width: int, has_cow: bool, simplify_ratio: float) -> None:
    """Process an input file and display the geometry on the command line as text symbols.

    Args:
        file (str): Filepath or URL to geometry file to be read with geopandas.read_file().
        map_row_width (int): Resulting width of printed text (number of characters.)
        has_cow (bool): If true, prints the cow "looking" at the map.
        simplify_ratio (float): Ratio to simplify geometries found in `file`.
    """
    # read in source data
    source_data_gdf = gpd.read_file(file)
    # explode to remove complex geometry types
    source_data_gdf = source_data_gdf.explode()
    # only retain geometry data
    source_data_gdf = source_data_gdf[["geometry"]]
    # reset index to ensure unique index values
    source_data_gdf = source_data_gdf.reset_index(drop=True)

    # define grid based on data and system character dimensions
    grid = Grid(source_data_gdf, map_row_width)

    # spatial join grid with input geometries to determine symbology
    cell_symbols = calculate_cell_symbols(source_data_gdf, grid, simplify_ratio)

    # populate a frame with symbology and cow
    drawing = Drawing(grid, cell_symbols, has_cow=has_cow)
    # draw symbology on console
    drawing.show()
