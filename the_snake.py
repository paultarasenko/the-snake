"""Игра «Змейка» на pygame.

Классическая аркадная игра: змейка ползает по полю, ест яблоки
и растёт, а при столкновении с собой сбрасывается в начальное
состояние.
"""

from random import choice, randint

import pygame as pg
# pylint: disable=no-member

# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Направления движения:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Цвет фона - черный:
BOARD_BACKGROUND_COLOR = (0, 0, 0)

# Цвет границы ячейки
BORDER_COLOR = (93, 216, 228)

# Цвет яблока
APPLE_COLOR = (255, 0, 0)

# Цвет змейки
SNAKE_COLOR = (0, 255, 0)

# Скорость движения змейки:
SPEED = 20

# Настройка игрового окна:
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Заголовок окна игрового поля:
pg.display.set_caption('Змейка')

# Настройка времени:
clock = pg.time.Clock()


class GameObject:  # pylint: disable=too-few-public-methods
    """Базовый класс для игровых объектов на поле."""

    def __init__(self, body_color=None):
        """Инициализирует объект в центре игрового поля."""
        self.position = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.body_color = body_color

    def draw_cell(self, position, color=None):
        """Отрисовывает одну ячейку объекта на игровом поле."""
        rect = pg.Rect(position, (GRID_SIZE, GRID_SIZE))
        pg.draw.rect(screen, color or self.body_color, rect)
        pg.draw.rect(screen, BORDER_COLOR, rect, 1)

    def draw(self):
        """Отрисовывает объект на экране. Переопределяется в наследниках."""


class Apple(GameObject):
    """Яблоко — объект, который змейка съедает, чтобы вырасти."""

    def __init__(self, body_color=APPLE_COLOR, occupied_cells=None):
        """Создаёт яблоко и задаёт ему случайную позицию."""
        super().__init__(body_color)
        self.randomize_position(occupied_cells)

    def randomize_position(self, occupied_cells=None):
        """Устанавливает случайную позицию яблока на игровом поле,
        не попадая в переданные занятые ячейки.
        """
        occupied_cells = occupied_cells or ()
        while True:
            self.position = (
                randint(0, GRID_WIDTH - 1) * GRID_SIZE,
                randint(0, GRID_HEIGHT - 1) * GRID_SIZE
            )
            if self.position not in occupied_cells:
                break

    def draw(self):
        """Отрисовывает яблоко на игровом поле."""
        self.draw_cell(self.position)


class Snake(GameObject):
    """Змейка — управляемый игроком объект, растущий при еде яблок."""

    def __init__(self, body_color=SNAKE_COLOR):
        """Инициализирует змейку в начальном состоянии."""
        super().__init__(body_color)
        self.length = 1
        self.positions = [self.position]
        self.direction = RIGHT
        self.last = None
        self.reset()

    def update_direction(self, next_direction):
        """Обновляет направление движения змейки."""
        if next_direction:
            self.direction = next_direction

    def get_head_position(self):
        """Возвращает координаты головы змейки."""
        return self.positions[0]

    def move(self):
        """Двигает змейку на один шаг в текущем направлении."""
        head_x, head_y = self.get_head_position()
        dx, dy = self.direction
        new_head = (
            (head_x + dx * GRID_SIZE) % SCREEN_WIDTH,
            (head_y + dy * GRID_SIZE) % SCREEN_HEIGHT
        )
        self.positions.insert(0, new_head)
        if len(self.positions) > self.length:
            self.last = self.positions.pop()
        else:
            self.last = None

    def draw(self):
        """Отрисовывает змейку на игровом поле."""
        self.draw_cell(self.get_head_position())

        if self.last:
            last_rect = pg.Rect(self.last, (GRID_SIZE, GRID_SIZE))
            pg.draw.rect(screen, BOARD_BACKGROUND_COLOR, last_rect)

    def reset(self):
        """Сбрасывает змейку в начальное состояние после столкновения."""
        self.length = 1
        self.positions = [(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)]
        self.direction = choice([UP, DOWN, LEFT, RIGHT])
        self.last = None


def handle_keys(game_object):
    """Обрабатывает нажатия клавиш пользователя и события pygame.

    Возвращает новое направление движения змейки, если пользователь
    нажал допустимую клавишу поворота, иначе — None.
    """
    turns = {
        (pg.K_UP, LEFT): UP,
        (pg.K_UP, RIGHT): UP,
        (pg.K_DOWN, LEFT): DOWN,
        (pg.K_DOWN, RIGHT): DOWN,
        (pg.K_LEFT, UP): LEFT,
        (pg.K_LEFT, DOWN): LEFT,
        (pg.K_RIGHT, UP): RIGHT,
        (pg.K_RIGHT, DOWN): RIGHT,
    }
    next_direction = None
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            raise SystemExit

        if event.type != pg.KEYDOWN:
            continue

        if event.key == pg.K_ESCAPE:
            pg.quit()
            raise SystemExit

        next_direction = turns.get(
            (event.key, game_object.direction), next_direction
        )

    return next_direction


def main():
    """Запускает основной игровой цикл."""
    pg.init()
    snake = Snake()
    apple = Apple(occupied_cells=snake.positions)

    while True:
        clock.tick(SPEED)
        next_direction = handle_keys(snake)
        snake.update_direction(next_direction)
        snake.move()

        if snake.get_head_position() == apple.position:
            snake.length += 1
            apple.randomize_position(snake.positions)
        elif snake.get_head_position() in snake.positions[1:]:
            screen.fill(BOARD_BACKGROUND_COLOR)
            snake.reset()

        apple.draw()
        snake.draw()
        pg.display.update()


if __name__ == '__main__':
    main()
