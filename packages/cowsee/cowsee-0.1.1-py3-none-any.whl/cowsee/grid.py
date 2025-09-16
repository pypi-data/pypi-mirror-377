import math

import geopandas as gpd
from PIL import Image, ImageDraw, ImageFont
from shapely import LineString, Polygon


class Grid:
    """The Grid defines the relationship between the geospatial data and console."""

    def __init__(self, source_data_gdf: gpd.GeoDataFrame, max_columns: int) -> None:
        """Initializes a Grid object.

        1. Finds the bounds and x/y width of the geometry inputs.
        2. Using Pillow, calculates the width/height ratio of the current CLI font.
        3. Using max_columns and the above, calculates the required number of output rows.
        4. Determines the x/y dimensions of each "cell" that a single character takes up in the
        geometry

        Also offers three property methods (for Points, Lines, and Polygons) that calculate which
        symbols to populate
        in each output cell of the Grid.

        Args:
            source_data_gdf (gpd.GeoDataFrame): Contains geometry data to relate to CLI.
            max_columns (int): Maximum number of columns to subdivide input geometry into.
        """
        self.source_data_gdf = source_data_gdf  # todo make into series
        self.max_columns = max_columns
        self.crs = source_data_gdf.crs

        # find the bounds of the data
        self.min_x, self.min_y, self.max_x, self.max_y = self.source_data_gdf.total_bounds
        # find geometric width and height of data
        self.x_diff, self.y_diff = self.geometric_dimensions()
        # calculate number of rows and columns as floats
        # used for calculating exact cell dimensions
        self.n_columns_float, self.n_rows_float = self.map_width_and_height()
        self.cell_width, self.cell_height = self.cell_dimensions()
        # round up to get actual number of rows and columns
        self.n_columns = math.ceil(self.n_columns_float)
        self.n_rows = math.ceil(self.n_rows_float)
        # pre-defined index values
        self.indices = [(i, j) for i in range(self.n_columns) for j in range(self.n_rows)]

    @classmethod
    def text_width_height_ratio(cls) -> float:
        """Calculates the width/height ratio for the current loaded CLI font.

        Returns:
            float: Ratio of width to height for current CLI font.
        """
        image = Image.new(mode="RGB", size=(50, 50))
        draw = ImageDraw.Draw(image)
        bbox = draw.textbbox(xy=(0, 0), text="█", font=ImageFont.load_default())
        width = bbox[2] - bbox[0]
        height = bbox[3] - bbox[1]
        text_ratio = width / height
        return text_ratio

    def geometric_dimensions(self) -> tuple[float, float]:
        """Calculates the x and y dimensions of the Grid's input geometry.

        Returns:
            tuple[float, float]: X and Y dimensions, respectively.
        """
        x_diff = self.max_x - self.min_x
        y_diff = self.max_y - self.min_y
        return x_diff, y_diff

    def map_width_and_height(self) -> tuple[float, float]:
        """Calculates the number of columns and rows of cells to generate in the Grid.

        Initializes width (characters per row) and height (total rows) as if outputting square.
        Maximum height is
        scaled to account for text character dimensions. Then, the maximum size of the smaller
        dimension is overwritten.

        Returns:
            tuple[float, float]: Number of columns, number of rows to output in Grid.
        """
        n_columns = self.max_columns
        n_rows = self.max_columns * self.text_width_height_ratio()

        if self.x_diff > self.y_diff:
            n_rows = (self.y_diff / self.x_diff) * self.max_columns * self.text_width_height_ratio()
        elif self.y_diff > self.x_diff:
            n_columns = (self.x_diff / self.y_diff) * self.max_columns

        return n_columns, n_rows

    def cell_dimensions(self) -> tuple[float, float]:
        """Calculates the geometric xy dimensions of each output Grid cell rectangle.

        Returns:
            tuple[float, float]: Width, height of the Grid's cells.
        """
        cell_width = self.x_diff / self.n_columns_float
        cell_height = self.y_diff / self.n_rows_float
        return cell_width, cell_height

    def cell_corners(self, i: int, j: int) -> tuple[float, float, float, float]:
        """Based on any Grid cell index (i, j), outputs the xy of each corner.

        Args:
            i (int): Column index of the Grid cell.
            j (int): Row index of the Grid cell.

        Returns:
            tuple[float, float, float, float]: Minimum x, Minimum u, Maximum x, Maximum y
        """
        min_x = self.min_x + (self.cell_width * i)
        min_y = self.min_y + (self.cell_height * j)
        max_x = self.min_x + (self.cell_width * (i + 1))
        max_y = self.min_y + (self.cell_height * (j + 1))

        return min_x, min_y, max_x, max_y

    def grid_sections(self, min_x: float, min_y: float, rows: int, cols: int) -> list[Polygon]:
        """Subdivides each Grid cell into sub-cell Shapely Polygons.

        Args:
            min_x (float): The smallest x value of the cell to subdivide.
            min_y (float): The smallest y value of the cell to subdivide.
            rows (int): The number of rows to subdivide the cell into.
            cols (int): The number of columns to subdivide the cell into.

        Returns:
            list[Polygon]: List of sub-cell geometries, in order of lower-left to upper-right
            (left-to-right, bottom-to-top.)
        """
        w = self.cell_width / cols
        h = self.cell_height / rows

        return [
            Polygon(
                [
                    (min_x + c * w, min_y + r * h),
                    (min_x + c * w, min_y + (r + 1) * h),
                    (min_x + (c + 1) * w, min_y + (r + 1) * h),
                    (min_x + (c + 1) * w, min_y + r * h),
                ]
            )
            for r in range(rows)
            for c in range(cols)
        ]

    @property
    def grid_points_gdf(self) -> gpd.GeoDataFrame:
        """Generates a GeoDataFrame of the Grid's sub-cell sections with a Point value key.

        The value key is generated for each sub-cell based on the following 8-dot braille pattern:

        +---+---+
        | 1 | 4 |
        +---+---+
        | 2 | 5 |
        +---+---+
        | 3 | 6 |
        +---+---+
        | 7 | 8 |
        +---+---+

        Returns:
            gpd.GeoDataFrame: Geometry of each sub-cell section plus associated section "key".
        """
        index, data = [], []

        # build each individual grid cell and track cell location in index
        for i in range(self.n_columns):
            for j in range(self.n_rows):
                min_x, min_y, _, _ = self.cell_corners(i, j)
                (
                    braille_7,
                    braille_8,
                    braille_3,
                    braille_6,
                    braille_2,
                    braille_5,
                    braille_1,
                    braille_4,
                ) = self.grid_sections(min_x, min_y, 2, 4)
                data.extend(
                    [
                        ["braille_1", braille_1],
                        ["braille_2", braille_2],
                        ["braille_3", braille_3],
                        ["braille_4", braille_4],
                        ["braille_5", braille_5],
                        ["braille_6", braille_6],
                        ["braille_7", braille_7],
                        ["braille_8", braille_8],
                    ]
                )
                index.extend([(i, j)] * 8)

        grid_points_gdf = gpd.GeoDataFrame(
            index=index, data=data, columns=["section", "geometry"], crs=self.crs
        )

        return grid_points_gdf

    @property
    def grid_polygons_gdf(self) -> gpd.GeoDataFrame:
        """Generates a GeoDataFrame of the Grid's sub-cell sections with a Polygon value key.

        Each sub-cell can be considered lower-left (ll), lower-right (lr), upper-left (ul), or
        upper-right (ur).

        Returns:
            gpd.GeoDataFrame: Geometry of each sub-cell section plus associated section "key".
        """
        index, data = [], []

        # build each individual grid cell and track cell location in index
        for i in range(self.n_columns):
            for j in range(self.n_rows):
                min_x, min_y, _, _ = self.cell_corners(i, j)
                ll, lr, ul, ur = self.grid_sections(min_x, min_y, 2, 2)
                data.extend([["ll", ll], ["lr", lr], ["ul", ul], ["ur", ur]])
                index.extend([(i, j)] * 4)

        grid_polygons_gdf = gpd.GeoDataFrame(
            index=index, data=data, columns=["section", "geometry"], crs=self.crs
        )

        return grid_polygons_gdf

    @property
    def grid_lines_gdf(self) -> gpd.GeoDataFrame:
        """Generates a GeoDataFrame of the Grid's cells with a Line value key.

        Each cell is divided into its component base, top, right, and left LineString.

        Returns:
            gpd.GeoDataFrame: Geometry of each sub-cell section plus associated section "key".
        """
        index, data = [], []

        for i in range(self.n_columns):
            for j in range(self.n_rows):
                min_x, min_y, max_x, max_y = self.cell_corners(i, j)

                base = LineString([[min_x, min_y], [max_x, min_y]])
                top = LineString([[min_x, max_y], [max_x, max_y]])
                right = LineString([[max_x, max_y], [max_x, min_y]])
                left = LineString([[min_x, min_y], [min_x, max_y]])

                data.extend([["base", base], ["top", top], ["right", right], ["left", left]])

                index.extend([(i, j)] * 4)

        grid_lines_gdf = gpd.GeoDataFrame(
            index=index, data=data, columns=["section", "geometry"], crs=self.crs
        )

        return grid_lines_gdf
