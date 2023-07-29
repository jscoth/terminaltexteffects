from dataclasses import dataclass


@dataclass
class Coord:
    """A coordinate with row and column values.

    Args:
        column (int): column value
        row (int): row value"""

    column: int
    row: int


@dataclass
class GraphicalModes:
    """A class for storing terminal graphical modes.

    Supported graphical modes:
    bold, dim, italic, underline, blink, inverse, hidden, strike

    Args:
        bold (bool): bold mode
        dim (bool): dim mode
        italic (bool): italic mode
        underline (bool): underline mode
        blink (bool): blink mode
        inverse (bool): inverse mode
        hidden (bool): hidden mode
        strike (bool): strike mode
    """

    bold: bool = False
    dim: bool = False
    italic: bool = False
    underline: bool = False
    blink: bool = False
    inverse: bool = False
    hidden: bool = False
    strike: bool = False


class EffectCharacter:
    """A single character from the input data. Contains the symbol and the state of the character.

    Args:
        symbol (str): the character symbol.
        final_coord (Coord): the final coordinate of the character.
        current_coord (Coord): the current coordinate of the character. If different from the final coordinate, the character is moving.
        last_coord (Coord): the last coordinate of the character. Used to clear the last position of the character.
        target_coord (Coord): the target coordinate of the character. Used to determine the next coordinate to move to.
        waypoints (list[Coord]): a list of coordinates to move to. Used to determine the next target coordinate to move to.
        graphical_modes: (GraphicalModes): a GraphicalModes object containing the graphical modes of the character."""

    def __init__(self, symbol: str, final_column: int, final_row: int):
        """Initializes the EffectCharacter class.

        Args:
            symbol (str): the character symbol.
            final_column (int): the final column position of the character.
            final_row (int): the final row position of the character.
        """
        self.symbol: str = symbol
        self.final_coord: Coord = Coord(final_column, final_row)
        "The coordinate of the character in the input data."
        self.current_coord: Coord = Coord(final_column, final_row)
        "The current coordinate of the character. If different from the final coordinate, the character is moving."
        self.last_coord: Coord = Coord(final_column, final_row)
        "The last coordinate of the character. Used to clear the last position of the character."
        self.target_coord: Coord = Coord(final_column, final_row)
        "The target coordinate of the character. Used to determine the next coordinate to move to."
        self.waypoints: list[Coord] = []
        "A list of coordinates to move to. Used to determine the next target coordinate to move to."
        self.graphical_modes: GraphicalModes = GraphicalModes()
        # move_delta is the floating point distance to move each step
        self.move_delta: float = 0
        # tweened_column and tweened_row are the floating point values for the current column and row positions
        self.tweened_column: float = 0
        self.tweened_row: float = 0

    def move(self) -> None:
        """Moves the character one step closer to the target position."""
        self.last_coord.column, self.last_coord.row = self.current_coord.column, self.current_coord.row

        # if the character has reached the target coordinate, pop the next coordinate from the waypoints list
        # and reset the move_delta for recalculation
        if self.current_coord == self.target_coord and self.waypoints:
            self.target_coord = self.waypoints.pop(0)
            self.move_delta = 0

        column_distance = abs(self.current_coord.column - self.target_coord.column)
        row_distance = abs(self.current_coord.row - self.target_coord.row)
        # on first call, calculate the column and row movement distance to approximate an angled line
        if not self.move_delta:
            self.tweened_column = self.current_coord.column
            self.tweened_row = self.current_coord.row
            self.move_delta = min(column_distance, row_distance) / max(column_distance, row_distance, 1)
            if self.move_delta == 0:
                self.move_delta = 1

            if column_distance < row_distance:
                self.column_delta = self.move_delta
                self.row_delta = 1
            elif row_distance < column_distance:
                self.row_delta = self.move_delta
                self.column_delta = 1
            else:
                self.column_delta = self.row_delta = 1
        # adjust the column and row positions by the calculated delta, round down to int
        if self.current_coord.column < self.target_coord.column:
            self.tweened_column += self.column_delta
            self.current_coord.column = int(self.tweened_column)
        elif self.current_coord.column > self.target_coord.column:
            self.tweened_column -= self.column_delta
            self.current_coord.column = int(self.tweened_column)
        if self.current_coord.row < self.target_coord.row:
            self.tweened_row += self.row_delta
            self.current_coord.row = int(self.tweened_row)
        elif self.current_coord.row > self.target_coord.row:
            self.tweened_row -= self.row_delta
            self.current_coord.row = int(self.tweened_row)

    def animation_completed(self) -> bool:
        """Returns True if the character has reached its final position."""
        return self.last_coord == self.final_coord
