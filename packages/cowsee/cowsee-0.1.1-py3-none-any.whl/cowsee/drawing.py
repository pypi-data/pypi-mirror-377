import itertools

import numpy as np

from cowsee.grid import Grid


class Drawing:
    """Drawing supports printing each cell from the Grid into the console.

    Builds a numpy array containing the map (geometry data), frame (around the geometry data), and
    optionally, the cow.
    """

    def __init__(
        self, grid: Grid, cell_symbols: dict[tuple, frozenset[str] | None], has_cow: bool
    ) -> None:
        """Initializes the Drawing object.

        Args:
            grid (Grid): Contains the number of rows and columns of text to print to the console.
            cell_symbols (dict[tuple, frozenset[str]  |  None]): Maps each Grid cell index to a
            frozenset for that cell symbol's keys.
            has_cow (bool): If True, print a cow "looking" as the data.
        """
        self.cow = [
            "^__^            ",
            "(oo)\\_______    ",
            "(__)\\       )\\/\\",
            "    ||----w |   ",
            "    ||     ||   ",
        ]

        self.point_characters = self._point_characters

        self.line_characters = {
            frozenset(["left"]): "╴",
            frozenset(["right"]): "╶",
            frozenset(["top"]): "╵",
            frozenset(["base"]): "╷",
            frozenset(["base", "top"]): "|",
            frozenset(["left", "right"]): "─",
            frozenset(["left", "top"]): "/",
            frozenset(["base", "right"]): "/",
            frozenset(["right", "top"]): "\\",
            frozenset(["base", "left"]): "\\",
            frozenset(["base", "right", "top"]): "├",
            frozenset(["base", "left", "top"]): "┤",
            frozenset(["base", "left", "right"]): "┬",
            frozenset(["left", "right", "top"]): "┴",
            frozenset(["base", "left", "right", "top"]): "┼",
        }

        self.polygon_characters = {
            frozenset(["ll"]): "▖",
            frozenset(["lr"]): "▗",
            frozenset(["ul"]): "▘",
            frozenset(["ur"]): "▝",
            frozenset(["ll", "lr"]): "▄",
            frozenset(["ul", "ur"]): "▀",
            frozenset(["ul", "ll"]): "▌",
            frozenset(["ur", "lr"]): "▐",
            frozenset(["ul", "lr"]): "▚",
            frozenset(["ll", "ur"]): "▚",
            frozenset(["ll", "lr", "ur"]): "▟",
            frozenset(["ll", "lr", "ul"]): "▙",
            frozenset(["ul", "ur", "lr"]): "▜",
            frozenset(["ul", "ur", "ll"]): "▛",
            frozenset(["ul", "ur", "ll", "lr"]): "█",
        }

        self.frame_symbols = {
            "ul": "╔",
            "ur": "╗",
            "ll": "╚",
            "lr": "╝",
            "horizontal": "═",
            "vertical": "║",
        }

        self.symbol_characters = (
            self.point_characters | self.line_characters | self.polygon_characters
        )

        self.grid = grid
        self.cell_symbols = cell_symbols
        self.has_cow = has_cow
        self.cow_width = max([len(i) for i in self.cow])
        self.cow_array = np.array([list(line) for line in self.cow])

        self.map_symbols = self.create_map()
        self.display_array = self.build_frame()

        self.draw_map()

        if has_cow:
            self.draw_cow()

    def create_map(self) -> np.ndarray:
        """Generates an array of symbols based on the cell symbol dictionary and preset symbol
        characters.

        Returns:
            np.ndarray: Array of geometry symbols.
        """
        # initializes with blank array to populate with symbology
        symbol_array = np.full((self.grid.n_rows, self.grid.n_columns), " ")

        for (x, y), char in self.cell_symbols.items():
            if char:
                symbol = self.symbol_characters[char]
                # note: y-axis inverted here so largest y is printed first
                symbol_array[self.grid.n_rows - 1 - y, x] = symbol

        return symbol_array

    def build_frame(self) -> np.ndarray:
        """Generates an array of the "frame" that surrounds the geometry array.

        Returns:
            np.ndarray: Array of frame symbols.
        """
        # buffer map dimensions for pretty whitespace
        frame_width = self.grid.n_columns + 7
        frame_height = self.grid.n_rows + 4

        frame_array = np.full((frame_height, frame_width + self.cow_width + 5), " ")

        frame_array[0, 0] = self.frame_symbols["ul"]
        frame_array[0, frame_width] = self.frame_symbols["ur"]
        frame_array[-1, frame_width] = self.frame_symbols["lr"]
        frame_array[-1, 0] = self.frame_symbols["ll"]
        frame_array[0, 1:frame_width] = self.frame_symbols["horizontal"]
        frame_array[-1, 1:frame_width] = self.frame_symbols["horizontal"]
        frame_array[1:-1, 0] = self.frame_symbols["vertical"]
        frame_array[1:-1, frame_width] = self.frame_symbols["vertical"]

        return frame_array

    def draw_map(self) -> None:
        """Inserts the geometry map into the frame array."""
        self.display_array[2 : 2 + self.map_symbols.shape[0], 4 : 4 + self.map_symbols.shape[1]] = (
            self.map_symbols
        )

    def draw_cow(self) -> None:
        """Adds the cow next to the frame and geometry array data."""
        frame_height, frame_width = self.display_array.shape
        cow_height, cow_width = self.cow_array.shape

        self.display_array[
            frame_height - cow_height : frame_height,
            frame_width - cow_width - 1 : frame_width - 1,
        ] = self.cow_array

    def show(self) -> None:
        """Prints the constructed array of geometry, map, (and cow) to the console."""
        for row in self.display_array:
            print("".join(row))

    @property
    def _point_characters(self) -> dict[frozenset[str], chr]:
        """Programmatically generates a map for each combination of point cell keys into a
        character. (e.g. {braille_5, braille_7} -> "⡐").

        Leverages the fact that each braille character has a unique code based on the sum of powers
        of 2.

        Returns:
            dict[frozenset[str], chr]: Map from point cell key to braille character.
        """
        braille_values = {
            "braille_1": 1,
            "braille_2": 2,
            "braille_3": 4,
            "braille_4": 8,
            "braille_5": 16,
            "braille_6": 32,
            "braille_7": 64,
            "braille_8": 128,
        }

        return {
            frozenset(combo): chr(0x2800 + sum(braille_values[d] for d in combo))
            for r in range(1, len(braille_values) + 1)
            for combo in itertools.combinations(braille_values.keys(), r)
        }
