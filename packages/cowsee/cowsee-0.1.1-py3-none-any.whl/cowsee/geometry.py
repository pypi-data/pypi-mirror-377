import dask_geopandas
import geopandas as gpd

from cowsee.grid import Grid


def calculate_cell_symbols(
    data_gdf: gpd.GeoDataFrame, grid: Grid, simplify_ratio: float
) -> dict[tuple, frozenset[str] | None]:
    """Determines which subsections of each Grid cell intersect with the input geometries, and
    assigns each cell a symbol.

    1. Splits the input geometries into Polygons, Lines, and Point data.
    2. Initializes an empty dictionary, with the Grid cell index as keys.
    3. Spatially intersects the geometries with the subdivided Grid cells, overwriting cell_symbols
    wherever data intersects with aggregated symbol keys.

    Polygon cell symbols are overwritten by Line symbols, which are then overwritten by Point
    symbols.

    Args:
        data_gdf (gpd.GeoDataFrame): GeoDataframe containing geometry data to intersect with Grid.
        grid (Grid): Defines cells to intersect with data_gdf to determine cell symbol.
        simplify_ratio (float): Amount of simplify input geometries.

    Returns:
        dict[tuple, frozenset[str] | None]: Maps each Grid cell index to a frozenset for that cell
        symbol's keys.
    """
    # separate geometry types for different processing pipelines
    polygon_gdf = data_gdf[data_gdf.geometry.geom_type == "Polygon"]
    line_gdf = data_gdf[data_gdf.geometry.geom_type == "LineString"]
    point_gdf = data_gdf[data_gdf.geometry.geom_type == "Point"]

    # initialize empty dictionary for grid cell symbology
    cell_symbols = {i: None for i in grid.indices}

    if len(polygon_gdf) > 0:
        cell_symbols = intersect_grid(
            polygon_gdf,
            grid.grid_polygons_gdf,
            cell_symbols,
            simplify_tolerance=grid.cell_width * simplify_ratio,
        )

    if len(line_gdf) > 0:
        # cell_symbols = intersect_lines(grid, line_gdf, cell_symbols)
        cell_symbols = intersect_grid(
            line_gdf,
            grid.grid_lines_gdf,
            cell_symbols,
            simplify_tolerance=grid.cell_width * simplify_ratio,
        )

    if len(point_gdf) > 0:
        cell_symbols = intersect_grid(
            point_gdf,
            grid.grid_points_gdf,
            cell_symbols,
        )

    return cell_symbols


def intersect_grid(
    gdf: gpd.GeoDataFrame,
    grid_gdf: gpd.GeoDataFrame,
    cell_symbols: dict[tuple, frozenset[str] | None],
    simplify_tolerance: float = 0,
) -> dict[tuple, frozenset[str] | None]:
    """Intersect geometries with a Grid, aggregating the keys in the column "section" for each cell.

    Optionally pre-simplify the geometry before intersecting.

    Args:
        gdf (gpd.GeoDataFrame): GeoDataframe containing geometry to intersect with Grid.
        grid_gdf (gpd.GeoDataFrame): GeoDataframe of subsections of Grid cells.
        cell_symbols (dict[tuple, frozenset[str]  |  None]): Maps each Grid cell index to a
        frozenset for that cell symbol's keys.
        simplify_tolerance (float, optional): Ratio of simplification to apply to gdf geometries.
        Defaults to 0.

    Returns:
        _type_: _description_
    """
    if simplify_tolerance:
        # dask is leveraged here to speed up the potentially slow simplification step
        ddf = dask_geopandas.from_geopandas(gdf.geometry, npartitions=10)
        gdf.geometry = ddf.simplify(tolerance=simplify_tolerance).compute()

    intersect_gdf = gpd.sjoin(grid_gdf, gdf)
    cells = intersect_gdf.groupby(level=0)["section"].agg(frozenset).to_dict()
    cell_symbols.update(cells)

    return cell_symbols
