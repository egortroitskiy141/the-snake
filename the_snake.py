from random import randint

import pygame

SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE
SCREEN_CENTER = (
    SCREEN_WIDTH // 2,
    SCREEN_HEIGHT // 2,
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

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
pygame.display.set_caption('Змейка')
clock = pygame.time.Clock()


class GameObject:
    """Базовый класс для игровых объектов."""

    def __init__(self, body_color=None):
        """Инициализация игрового объекта."""
        self.position = SCREEN_CENTER
        self.body_color = body_color if body_color is not None else DEFAULT_COLOR

    def draw(self, surface):
        """Отрисовка объекта на поверхности."""
        raise NotImplementedError(
            'Метод draw() должен быть реализован в дочернем классе'
        )


class Apple(GameObject):
    """Класс яблока."""

    def __init__(self, body_color=APPLE_COLOR, occupied_positions=(SCREEN_CENTER,)):
        """Инициализация яблока."""
        super().__init__(body_color)
        self.position = self._get_random_position(occupied_positions)
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

    def randomize_position(self, occupied_positions):
        """Изменение позиции яблока."""
        self.position = self._get_random_position(occupied_positions)
        self.is_super = randint(1, 100) <= SUPER_APPLE_CHANCE
        if self.is_super:
            self.body_color = SUPER_APPLE_COLOR
        else:
            self.body_color = APPLE_COLOR

    def draw(self, surface):
        """Отрисовка яблока на поверхности."""
        rect = pygame.Rect(self.position, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(surface, self.body_color, rect)
        pygame.draw.rect(surface, BORDER_COLOR, rect, 1)


class Snake(GameObject):
    """Класс змейки."""

    def __init__(self, body_color=SNAKE_COLOR):
        """Инициализация змейки."""
        super().__init__(body_color)
        self.positions = [self.position]
        self.length = 1
        self.direction = RIGHT
        self.next_direction = None

    def draw(self, surface):
        """Отрисовка змейки на поверхности."""
        for position in self.positions[:-1]:
            rect = pygame.Rect(position, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(surface, self.body_color, rect)
            pygame.draw.rect(surface, BORDER_COLOR, rect, 1)

        head_rect = pygame.Rect(self.get_head_position(), (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(surface, SNAKE_HEAD_COLOR, head_rect)
        pygame.draw.rect(surface, BORDER_COLOR, head_rect, 1)

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

        self.positions.insert(0, new_head)

        if len(self.positions) > self.length:
            self.positions.pop()

        self.position = new_head

    def reset(self):
        """Сброс змейки в начальное состояние."""
        super().__init__()
        self.positions = [self.position]
        self.length = 1
        self.direction = RIGHT

    def update_direction(self):
        """Обновление направления после нажатия клавиши."""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None


def handle_keys(event, game_object):
    """Обработка действий пользователя."""
    if event.type == pygame.QUIT:
        raise SystemExit
    elif event.type == pygame.KEYDOWN:
        if event.key == pygame.K_ESCAPE:
            raise SystemExit
        elif event.key == pygame.K_UP and game_object.direction != DOWN:
            game_object.next_direction = UP
        elif event.key == pygame.K_DOWN and game_object.direction != UP:
            game_object.next_direction = DOWN
        elif event.key == pygame.K_LEFT and game_object.direction != RIGHT:
            game_object.next_direction = LEFT
        elif event.key == pygame.K_RIGHT and game_object.direction != LEFT:
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
    score_text = font.render(f'Счёт: {score}', True, SCORE_COLOR)
    surface.blit(score_text, (10, 10))


def draw_speed_indicator(surface, speed):
    """Отрисовка индикатора скорости."""
    font = pygame.font.Font(None, 24)
    speed_text = font.render(f'Скорость: {speed}', True, (150, 150, 150))
    surface.blit(speed_text, (SCREEN_WIDTH - 120, 10))


def check_apple_eaten(snake, apple):
    """Проверка, съела ли змейка яблоко."""
    return snake.get_head_position() == apple.position


def handle_apple_eaten(snake, apple):
    """Обработка поедания яблока."""
    if apple.is_super:
        snake.length += 2
        return 3, True
    else:
        snake.length += 1
        apple.randomize_position(snake.positions)
        return 1, False


def main():
    """Основная функция игры."""
    pygame.init()
    snake = Snake()
    apple = Apple(occupied_positions=snake.positions)

    score = 0
    current_speed = INITIAL_SPEED

    try:
        while True:
            clock.tick(current_speed)

            for event in pygame.event.get():
                handle_keys(event, snake)

            snake.update_direction()
            snake.move()

            if snake.get_head_position() in snake.positions[1:]:
                snake.reset()
                apple.randomize_position(snake.positions)
                score = 0
                current_speed = INITIAL_SPEED

            if check_apple_eaten(snake, apple):
                points, speed_up = handle_apple_eaten(snake, apple)
                score += points
                if speed_up and current_speed < MAX_SPEED:
                    current_speed += SPEED_INCREMENT
                elif not speed_up and score % 5 == 0 and current_speed < MAX_SPEED:
                    current_speed += SPEED_INCREMENT

            screen.fill(BOARD_BACKGROUND_COLOR)
            draw_grid(screen)
            apple.draw(screen)
            snake.draw(screen)
            draw_score(screen, score)
            draw_speed_indicator(screen, current_speed)

            pygame.display.update()

    except SystemExit:
        pygame.quit()


if __name__ == '__main__':
    main()
