from time import sleep
from copy import deepcopy


class GameOfLife:
    def __init__(self, field_size: int, start_state: list[list[int]] = None):
        self.field_size = field_size
        self.field = [[0 for i in range(field_size)] for j in range(field_size)]
        if start_state:
            assert len(start_state) == self.field_size
            for y in range(self.field_size):
                assert len(start_state[y]) == self.field_size
                for x in range(self.field_size):
                    if start_state[y][x] == 1:
                        self.activate_cell(x, y)


    def activate_cell(self, x: int, y: int) -> None:
        self.field[y][x] = 1

    def get_neighbours(self, x: int, y: int) -> list[int]:
        result = []
        left_exists = x > 0
        right_exists = x < self.field_size - 1
        up_exists = y > 0
        down_exists = y < self.field_size - 1
        if up_exists:
            if left_exists:
                result.append(self.field[y - 1][x - 1])
            result.append(self.field[y - 1][x])
            if right_exists:
                result.append(self.field[y - 1][x + 1])
        if right_exists:
            result.append(self.field[y][x + 1])
            if down_exists:
                result.append(self.field[y + 1][x + 1])
        if down_exists:
            result.append(self.field[y + 1][x])
            if left_exists:
                result.append(self.field[y + 1][x - 1])
        if left_exists:
            result.append(self.field[y][x - 1])
        return result

    def tick(self) -> None:
        new_field = [[0 for i in range(self.field_size)] for j in range(self.field_size)]
        for y in range(self.field_size):
            for x in range(self.field_size):
                neighbours = self.get_neighbours(x, y)
                alive_neighbours = neighbours.count(1)
                flag_stayin_alive = self.field[y][x] == 1 and 2 <= alive_neighbours <= 3
                flag_new_born = self.field[y][x] == 0 and alive_neighbours == 3
                if flag_stayin_alive or flag_new_born:
                    new_field[y][x] = 1
                    continue
                new_field[y][x] = 0
        self.field = deepcopy(new_field)


def beautify_array(arr: list[list[int]]) -> str:
    result = ''
    for row in arr:
        for item in row:
            result += ('█' if item == 1 else '_') + ' '
        result = result[:-1] + '\n'
    return result


if __name__ == "__main__":
    size = int(input("Size of field: "))
    start_flag = input("Set start field?: ") == 'y'
    start_field = None
    if start_flag:
        start_field = [[int(i) for i in input()] for j in range(size)]
    game = GameOfLife(size, start_field)

    for i in range(10):
        print(beautify_array(game.field))
        game.tick()
        sleep(1)
