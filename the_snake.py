from random import choice, randint

import pygame

SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE
SCREEN_CENTER = (
    (GRID_WIDTH // 2) * GRID_SIZE,
    (GRID_HEIGHT // 2) * GRID_SIZE,
)

UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

BOARD_BACKGROUND_COLOR = (10, 10, 20)
BORDER_COLOR = (70, 130, 180)
GRID_COLOR = (30, 30, 50)
APPLE_COLOR = (220, 20, 60)
SUPER_APPLE_COLOR = (255, 215, 0)
SNAKE_COLOR = (50, 205, 50)
SNAKE_HEAD_COLOR = (34, 139, 34)
SCORE_COLOR = (255, 255, 255)
DEFAULT_COLOR = (0, 255, 0)

INITIAL_SPEED = 10
SPEED_INCREMENT = 1
MAX_SPEED = 25
SUPER_APPLE_CHANCE = 30

screen = pygame.display.set_mode(
    (SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32
)
pygame.display.set_caption('Змейка')
clock = pygame.time.Clock()


class GameObject:
    """Базовый класс для игровых объектов."""

    def __init__(self, position=None, body_color=None):
        """Инициализация игрового объекта."""
        self.position = (
            position if position is not None else (0, 0)
        )
        self.body_color = (
            body_color if body_color is not None
            else DEFAULT_COLOR
        )

    def draw(self, surface):
        """Отрисовка объекта на поверхности."""
        raise NotImplementedError(
            'Метод draw() должен быть реализован'
            ' в дочернем классе'
        )


class Apple(GameObject):
    """Класс яблока."""

    def __init__(
        self,
        position=None,
        body_color=APPLE_COLOR,
        occupied_positions=None,
    ):
        """Инициализация яблока."""
        if occupied_positions is None:
            occupied_positions = []
        if position is None:
            position = self._get_random_position(
                occupied_positions
            )
        super().__init__(position, body_color)
        self.is_super = False

    def _get_random_position(self, occupied_positions):
        """Получение случайной позиции."""
        while True:
            new_position = (
                randint(0, GRID_WIDTH - 1) * GRID_SIZE,
                randint(0, GRID_HEIGHT - 1) * GRID_SIZE,
            )
            if new_position not in occupied_positions:
                return new_position

    def randomize_position(self, snake_positions):
        """Установка случайной позиции яблока."""
        self.position = self._get_random_position(
            snake_positions
        )
        self.is_super = (
            randint(1, 100) <= SUPER_APPLE_CHANCE
        )
        if self.is_super:
            self.body_color = SUPER_APPLE_COLOR
        else:
            self.body_color = APPLE_COLOR

    def draw(self, surface):
        """Отрисовка яблока на поверхности."""
        rect = pygame.Rect(
            self.position, (GRID_SIZE, GRID_SIZE)
        )
        pygame.draw.rect(surface, self.body_color, rect)
        pygame.draw.rect(surface, BORDER_COLOR, rect, 1)


class Snake(GameObject):
    """Класс змейки."""

    def __init__(self, position=None, body_color=SNAKE_COLOR):
        """Инициализация змейки."""
        if position is None:
            position = SCREEN_CENTER
        super().__init__(position, body_color)
        self.positions = [position]
        self.length = 1
        self.direction = choice([UP, DOWN, LEFT, RIGHT])
        self.next_direction = None

    def draw(self, surface):
        """Отрисовка змейки на поверхности."""
        for position in self.positions[:-1]:
            rect = pygame.Rect(
                position, (GRID_SIZE, GRID_SIZE)
            )
            pygame.draw.rect(
                surface, self.body_color, rect
            )
            pygame.draw.rect(
                surface, BORDER_COLOR, rect, 1
            )

        head_rect = pygame.Rect(
            self.positions[0], (GRID_SIZE, GRID_SIZE)
        )
        pygame.draw.rect(
            surface, SNAKE_HEAD_COLOR, head_rect
        )
        pygame.draw.rect(
            surface, BORDER_COLOR, head_rect, 1
        )

    def get_head_position(self):
        """Получение позиции головы змейки."""
        return self.positions[0]

    def move(self):
        """Перемещение змейки в текущем направлении."""
        head_x, head_y = self.get_head_position()
        dir_x, dir_y = self.direction
        new_head = (
            (head_x + dir_x * GRID_SIZE) % SCREEN_WIDTH,
            (head_y + dir_y * GRID_SIZE) % SCREEN_HEIGHT,
        )

        if new_head in self.positions[1:]:
            self.reset()
            return

        self.positions.insert(0, new_head)

        if len(self.positions) > self.length:
            self.positions.pop()

        self.position = new_head

    def reset(self):
        """Сброс змейки в начальное состояние."""
        self.positions = [SCREEN_CENTER]
        self.length = 1
        self.direction = choice([UP, DOWN, LEFT, RIGHT])
        self.next_direction = None
        self.position = SCREEN_CENTER

    def update_direction(self):
        """Обновление направления после нажатия клавиши."""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None


def handle_keys(event, game_object):
    """Обработка действий пользователя."""
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_UP and (
            game_object.direction != DOWN
        ):
            game_object.next_direction = UP
        elif event.key == pygame.K_DOWN and (
            game_object.direction != UP
        ):
            game_object.next_direction = DOWN
        elif event.key == pygame.K_LEFT and (
            game_object.direction != RIGHT
        ):
            game_object.next_direction = LEFT
        elif event.key == pygame.K_RIGHT and (
            game_object.direction != LEFT
        ):
            game_object.next_direction = RIGHT


def draw_grid(surface):
    """Отрисовка сетки игрового поля."""
    for x in range(0, SCREEN_WIDTH, GRID_SIZE):
        for y in range(0, SCREEN_HEIGHT, GRID_SIZE):
            rect = pygame.Rect(x, y, GRID_SIZE, GRID_SIZE)
            pygame.draw.rect(surface, GRID_COLOR, rect, 1)


def draw_score(surface, score):
    """Отрисовка счёта на экране."""
    font = pygame.font.Font(None, 36)
    score_text = font.render(
        f'Счёт: {score}', True, SCORE_COLOR
    )
    surface.blit(score_text, (10, 10))


def draw_speed_indicator(surface, speed):
    """Отрисовка индикатора скорости."""
    font = pygame.font.Font(None, 24)
    speed_text = font.render(
        f'Скорость: {speed}', True, (150, 150, 150)
    )
    surface.blit(
        speed_text, (SCREEN_WIDTH - 120, 10)
    )


def check_apple_eaten(snake, apple):
    """Проверка съедения яблока и обновление счёта."""
    if snake.get_head_position() == apple.position:
        if apple.is_super:
            snake.length += 2
            score = 3
            speed_bonus = True
        else:
            snake.length += 1
            score = 1
            speed_bonus = False
        apple.randomize_position(snake.positions)
        return score, speed_bonus
    return 0, False


def check_collision(snake, apple):
    """Проверка столкновения змейки с собой."""
    if snake.get_head_position() in snake.positions[1:]:
        snake.reset()
        apple.randomize_position(snake.positions)
        return True
    return False


def main():
    """Основная функция игры."""
    pygame.init()
    snake = Snake()
    apple = Apple(
        occupied_positions=snake.positions
    )

    score = 0
    current_speed = INITIAL_SPEED
    running = True

    while running:
        clock.tick(current_speed)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                else:
                    handle_keys(event, snake)

        snake.update_direction()
        snake.move()

        points, speed_up = check_apple_eaten(
            snake, apple
        )
        score += points
        if speed_up and current_speed < MAX_SPEED:
            current_speed += SPEED_INCREMENT
        if (
            not speed_up
            and score % 5 == 0
            and current_speed < MAX_SPEED
        ):
            current_speed += SPEED_INCREMENT

        check_collision(snake, apple)

        screen.fill(BOARD_BACKGROUND_COLOR)
        draw_grid(screen)
        apple.draw(screen)
        snake.draw(screen)
        draw_score(screen, score)
        draw_speed_indicator(screen, current_speed)

        pygame.display.update()

    pygame.quit()


if __name__ == '__main__':
    main()
