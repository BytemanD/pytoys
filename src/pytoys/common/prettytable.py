import inspect

import dataclasses
import prettytable

@dataclasses.dataclass
class TableStyle:
    horizontal_char: str
    vertical_char: str
    junction_char: str
    top_junction_char: str
    bottom_junction_char: str
    left_junction_char: str
    right_junction_char: str
    top_left_junction_char: str
    top_right_junction_char: str
    bottom_left_junction_char: str
    bottom_right_junction_char: str

# ┌─────────┬─────┬─────────────┐
# │ Name    │ Age │ City        │
# ├─────────┼─────┼─────────────┤
# │ Alice   │ 24  │ New York    │
# │ Bob     │ 19  │ Los Angeles │
# └─────────┴─────┴─────────────┘
STYLE_LIGHT = TableStyle(horizontal_char = "─",
                         vertical_char = "│",
                         junction_char = "┼",
                         top_junction_char = "┬",
                         bottom_junction_char = "┴",
                         left_junction_char = "├",
                         right_junction_char = "┤",
                         top_left_junction_char = "┌",
                         top_right_junction_char = "┐",
                         bottom_left_junction_char = "└",
                         bottom_right_junction_char = "┘")


class Table(prettytable.PrettyTable):

    def __init__(self, field_names, style: TableStyle=None, **kwargs):
        super().__init__(field_names, **kwargs)
        if style:
            self.set_style(style)

    def set_style(self, style: TableStyle):
        for name, value in inspect.getmembers(style):
            if name.startswith('_'):
                continue
            setattr(self, name, value)
