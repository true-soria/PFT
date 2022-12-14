
import json, sys, pprint
from collections import namedtuple
from typing import Self

Column = namedtuple('Column', ['start', 'end'])
spacing_char = ' '

class Cell(object):
    def __new__(cls: type[Self], entry_json) -> Self:
        try:
            entry_json['name'], entry_json['desc'], entry_json['row']
            entry_json['type'], entry_json['filename']
            col = entry_json['col']
            if isinstance(col, list):
                assert len(col) == 2, f'Expected exactly 2 numbers, got {len(col)}.'
                assert isinstance(col[0], int), f'\'{col[0]}\' is not a number!'
                assert col[0] > 0, f'column start can not be less than 1!'
                assert isinstance(col[1], int), f'\'{col[1]}\' is not a number!'
                assert col[0] < col[1], f'column end must be greater than column start'
            else:
                assert isinstance(col, int), f'{col} is not a number!'
            return super(Cell, cls).__new__(cls)
        except KeyError as e:
            print('The following attribute was missing from the json entry: %s' % str(e))
            return None
        except AssertionError as e:
            print('The column entry could not be properly read: %s' % str(e))
            return None

    def __init__(self, entry_json) -> None:
            self.name = entry_json['name']
            self.description = entry_json['desc']
            self.row = entry_json['row']
            self.col = Column(entry_json['col'][0], entry_json['col'][1])
            self.type = entry_json['type']
            self.filename = entry_json['filename']
            self.other_locations = {}

    def __str__(self) -> str:
        return 'name: %s\n' % self.name +\
                'description: %s\n' % self.description +\
                'line: %s\n' % self.row +\
                'column: %d-%d\n' % (self.col.start, self.col.end) +\
                'location(s): ' +\
                    ', '.join([self.filename] + sorted(self.other_locations))

    def add_locations(self, new_locations):
        self.other_locations.update(new_locations)

    def overlaps(self, other):
        if not isinstance(other, Cell):
            return False
        return self.col.start <= other.col.end and other.col.start <= self.col.end


def is_line_safe(cell_list):
    cell_list.sort(key=lambda cell: cell.col.start)
    previous_cell = cell_list[0]
    for cell in cell_list[1:]:
        if cell.overlaps(previous_cell):
            return False
    return True


def form_line(cells):
    ordered_cells = sorted(cells, key=lambda cell: cell.col.start)
    previous_stop = 0
    
    line = ''
    for cell in ordered_cells:
        spacing_distance = cell.col.start - previous_stop - 1
        line += spacing_char * spacing_distance
        previous_stop = cell.col.end
        # TODO Implement logical data placement
        cell_length = cell.col.end - cell.col.start + 1
        line += '0' * cell_length

    return line


if __name__ == '__main__':
    cells = []
    with open('resources/Grocery_List_Description_2.json', 'r') as f:
        try: data = json.load(f)
        except json.decoder.JSONDecodeError as e:
            print('While reading a JSON, an error was struck: %s' % str(e))
            sys.exit(1)
        for entry in data:
            cell = Cell(entry)
            if cell != None: cells.append(cell)

    if is_line_safe(cells):
        print(form_line(cells))
    else:
        for cell in cells:
            print(cell)
            print()
