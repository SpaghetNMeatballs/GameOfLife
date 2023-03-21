import random
from math import log
from copy import deepcopy
from random import randint
import pyxel
import datetime
import matplotlib.pyplot as plt


class GameOfLife:
    def __init__(self, field_size: int, start_state: list[list[int]] = None, step=100):
        # Последний апдейт поля, нужен для отрисовки pyxel
        self.last_update = datetime.datetime.now()
        self.field_size = field_size
        self.t = 0
        # Максимальное количество эпох
        self.tmax = 10 * (self.field_size ** 2)
        self.field = [[0 for i in range(field_size)] for j in range(field_size)]
        self.last_point = 0
        # Если есть поле - запоминаем его, если нет - генерируем
        if start_state:
            assert len(start_state) == self.field_size
            for y in range(self.field_size):
                assert len(start_state[y]) == self.field_size
                for x in range(self.field_size):
                    if start_state[y][x] == 1:
                        self.activate_cell(x, y)
        else:
            self.field = gen_field(field_size)
        self.history = [self.count_alive_cells()]
        self.step = step

    def count_alive_cells(self) -> int:
        count = 0
        for row in self.field:
            count += row.count(1)
        return count

    def get_time_left(self) -> int:
        return 10 * (self.field_size ** 2) - self.t

    # Функция, оживляющая клетку в заданных координатах
    def activate_cell(self, x: int, y: int) -> None:
        self.field[y][x] = 1

    def get_neighbour_indexes(self, x: int, y: int) -> list[list[int]]:
        result = []
        index_left = x - 1 if x > 0 else self.field_size - 1
        index_right = x + 1 if x < self.field_size - 1 else 0
        index_up = y - 1 if y > 0 else self.field_size - 1
        index_down = y + 1 if y < self.field_size - 1 else 0
        indexes_horizontal = [index_left, x, index_right]
        indexes_vertical = [index_up, y, index_down]
        for i in indexes_vertical:
            for j in indexes_horizontal:
                if i == y and j == x:
                    continue
                result.append([i, j])
        return result

    # Периодичная функция для получения соседей
    def get_neighbours(self, x: int, y: int) -> list[int]:
        result = []
        for index in self.get_neighbour_indexes(x, y):
            result.append(self.field[index[0]][index[1]])
        return result

    # НЕ МЕТОД МОНТЕ КАРЛО
    # Функция, проходящая по всему полю и обновляющая ячейки в соответствии с требованиями
    def tick(self) -> None:
        self.t += 1
        self.last_update = datetime.datetime.now()
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
        self.t += 1

    def _find_free_space(self, x: int, y: int) -> list[int]:
        pool = []
        for pair in self.get_neighbour_indexes(x, y):
            if self.field[pair[0]][pair[1]] == 0:
                pool.append(pair)
        return pool[random.randint(0, len(pool) - 1)]

    # Метод, отвечающий за проверку и реализацию рождения новой клетки
    def _cell_birth(self, x: int, y: int) -> None:
        n = self.get_neighbours(x, y)
        if 2 <= n.count(1) <= 3:
            self.field[y][x] = 1

    def _stable_cell(self, x: int, y: int) -> None:
        if self.field[y][x] == 1 and 0 in self.get_neighbours(x, y):
            ny, nx = self._find_free_space(x, y)
            self.field[y][x] = 0
            self.field[ny][nx] = 1

    def _underpopulated_cell(self, x: int, y: int) -> None:
        if self.field[y][x] == 1 and self.get_neighbours(x, y).count(1) < 3:
            self.field[y][x] = 0

    def _kill_overpopulated_cell(self, x: int, y: int) -> None:
        if self.field[y][x] == 1 and self.get_neighbours(x, y).count(1) > 4:
            self.field[y][x] = 0

    def _escape_overpopulated_cell(self, x: int, y: int) -> None:
        n = self.get_neighbours(x, y)
        if self.field[y][x] == 1 and 4 < n.count(1) < 9:
            ny, nx = self._find_free_space(x, y)
            self.field[y][x] = 0
            self.field[ny][nx] = 1
        return

    # Функция обновления, линейно выбирающая метод и использующая метод Монте Карло со случайным выбором
    def tick_mk(self) -> None:
        if self.t < self.tmax:
            if self.last_point + self.step <= self.t:
                self.last_point += self.step
                self.history.append(self.count_alive_cells())
            v = [1, 0.5, 2, 3, 1]
            # Массив callable методов обработки клетки
            methods = [self._cell_birth, self._stable_cell, self._underpopulated_cell, self._kill_overpopulated_cell,
                       self._escape_overpopulated_cell]

            e1 = random.uniform(0, 1)
            dt = -log(e1) / (self.field_size * sum(v))
            e2 = random.randint(0, self.field_size ** 2 - 1)
            x = int(e2 % self.field_size)
            y = int(e2 // self.field_size)
            e3 = random.uniform(0, 1)
            p = 0
            while sum(v[:p + 1]) < e3 * sum(v):
                p += 1
            # Применяем линейно выбранный метод
            methods[p](x, y)
            self.t += dt


# Функция для вывода поля в консоль
def beautify_array(arr: list[list[int]]) -> str:
    result = ''
    for row in arr:
        for item in row:
            result += ('█' if item == 1 else '_') + ' '
        result = result[:-1] + '\n'
    return result


# Генератор поля
def gen_field(size: int) -> list[list[int]]:
    result = [[] for i in range(size)]
    for i in range(size):
        for j in range(size):
            result[i].append(randint(0, 1))
    return result


class App:
    def __init__(self):
        pyxel.init(122, 130)
        self.game = GameOfLife(20, gen_field(20))
        pyxel.run(self.update, self.draw)

    def update(self):
        t_set = self.game.t
        while self.game.t < t_set + 1:
            self.game.tick_mk()

    def draw(self):
        pyxel.cls(0)
        pyxel.rect(0, 0, 122, 130, 1)
        time_to_print = self.game.get_time_left()
        pyxel.text(2, 2, "Epochs left: %d" % time_to_print, 0)
        pyxel.text(1, 1, "Epochs left: %d" % time_to_print, 7)
        for i in range(self.game.field_size):
            for j in range(self.game.field_size):
                if self.game.field[i][j] == 0:
                    col = 0
                else:
                    col = 11
                pyxel.rect(2 + i * 6, 10 + j * 6, 4, 4, col)
                pyxel.rect(2 + (i * 6), 10 + j * 6, 1, 1, 7)


if __name__ == "__main__":
    flag_mode = None
    while not flag_mode:
        mode = input("Graphical mode or fast mode? Input 1 or 2: ")
        flag_mode = mode == '1' or mode == '2'

    if mode == '1':
        App()
    else:
        size = int(input("Size of field: "))
        start_flag = input("Set start field? (y/n): ") == 'y'
        start_field = None
        if start_flag:
            start_field = [[int(i) for i in input()] for j in range(size)]
        else:
            start_field = gen_field(size)
        pyxel.init(2 + 6 * size, 2 + 6 * size)
        game = GameOfLife(size, start_field, step=50)
        history = []
        while game.t < game.tmax:
            game.tick_mk()
            history.append(game.count_alive_cells())
            if game.count_alive_cells() == 0:
                break
        fig, ax = plt.subplots()
        ax.plot([game.step * i for i in range(len(game.history))], game.history, "r")
        print(game.t)
        plt.show()
