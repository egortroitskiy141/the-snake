from random import choice, randint

import pygame

SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

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

    def __init__(self, position=None, body_color=None):
        self.position = position if position is not None else (0, 0)
        self.body_color = body_color if body_color is not None else (
            0, 255, 0
        )

    def draw(self, surface):
        rect = pygame.Rect(self.position, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(surface, self.body_color, rect)
        pygame.draw.rect(surface, BORDER_COLOR, rect, 1)


class Apple(GameObject):

    def __init__(self, position=None, body_color=APPLE_COLOR):
        if position is None:
            position = (
                randint(0, GRID_WIDTH - 1) * GRID_SIZE,
                randint(0, GRID_HEIGHT - 1) * GRID_SIZE,
            )
        super().__init__(position, body_color)
        self.is_super = False

    def randomize_position(self, snake_positions):
        while True:
            new_position = (
                randint(0, GRID_WIDTH - 1) * GRID_SIZE,
                randint(0, GRID_HEIGHT - 1) * GRID_SIZE,
            )
            if new_position not in snake_positions:
                self.position = new_position
                self.is_super = (
                    randint(1, 100) <= SUPER_APPLE_CHANCE
                )
                if self.is_super:
                    self.body_color = SUPER_APPLE_COLOR
                else:
                    self.body_color = APPLE_COLOR
                break

    def set_random_position(self, snake_positions):
        self.randomize_position(snake_positions)


class Snake(GameObject):

    def __init__(self, position=None, body_color=SNAKE_COLOR):
        if position is None:
            position = (
                (GRID_WIDTH // 2) * GRID_SIZE,
                (GRID_HEIGHT // 2) * GRID_SIZE,
            )
        super().__init__(position, body_color)
        self.positions = [position]
        self.length = 1
        self.direction = choice([UP, DOWN, LEFT, RIGHT])
        self.next_direction = None
        self.last = None

    def draw(self, surface):
        for position in self.positions[:-1]:
            rect = pygame.Rect(position, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(surface, self.body_color, rect)
            pygame.draw.rect(surface, BORDER_COLOR, rect, 1)

        head_rect = pygame.Rect(
            self.positions[0], (GRID_SIZE, GRID_SIZE)
        )
        pygame.draw.rect(surface, SNAKE_HEAD_COLOR, head_rect)
        pygame.draw.rect(surface, BORDER_COLOR, head_rect, 1)

        if self.last:
            last_rect = pygame.Rect(
                self.last, (GRID_SIZE, GRID_SIZE)
            )
            pygame.draw.rect(
                surface, BOARD_BACKGROUND_COLOR, last_rect
            )

    def get_head_position(self):
        return self.positions[0]

    def move(self):
        head = self.get_head_position()
        dir_x, dir_y = self.direction
        new_head = (
            (head[0] + dir_x * GRID_SIZE) % SCREEN_WIDTH,
            (head[1] + dir_y * GRID_SIZE) % SCREEN_HEIGHT,
        )

        if new_head in self.positions[1:]:
            self.reset()
            return

        self.positions.insert(0, new_head)

        if len(self.positions) > self.length:
            self.last = self.positions.pop()
        else:
            self.last = None

        self.position = new_head

    def reset(self):
        start_position = (
            (GRID_WIDTH // 2) * GRID_SIZE,
            (GRID_HEIGHT // 2) * GRID_SIZE,
        )
        self.positions = [start_position]
        self.length = 1
        self.direction = choice([UP, DOWN, LEFT, RIGHT])
        self.next_direction = None
        self.last = None
        self.position = start_position

    def update_direction(self):
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None


def handle_keys(game_object):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            raise SystemExit
        elif event.type == pygame.KEYDOWN:
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
    for x in range(0, SCREEN_WIDTH, GRID_SIZE):
        for y in range(0, SCREEN_HEIGHT, GRID_SIZE):
            rect = pygame.Rect(x, y, GRID_SIZE, GRID_SIZE)
            pygame.draw.rect(surface, GRID_COLOR, rect, 1)


def draw_score(surface, score):
    font = pygame.font.Font(None, 36)
    score_text = font.render(
        f'Счёт: {score}', True, SCORE_COLOR
    )
    surface.blit(score_text, (10, 10))


def draw_speed_indicator(surface, speed):
    font = pygame.font.Font(None, 24)
    speed_text = font.render(
        f'Скорость: {speed}', True, (150, 150, 150)
    )
    surface.blit(speed_text, (SCREEN_WIDTH - 120, 10))


def main():
    pygame.init()
    snake = Snake()
    apple = Apple()
    apple.randomize_position(snake.positions)

    score = 0
    current_speed = INITIAL_SPEED

    while True:
        clock.tick(current_speed)
        handle_keys(snake)
        snake.update_direction()
        snake.move()

        if snake.get_head_position() == apple.position:
            if apple.is_super:
                snake.length += 2
                score += 3
                if current_speed < MAX_SPEED:
                    current_speed += SPEED_INCREMENT
            else:
                snake.length += 1
                score += 1
                if score % 5 == 0 and current_speed < MAX_SPEED:
                    current_speed += SPEED_INCREMENT
            apple.randomize_position(snake.positions)

        screen.fill(BOARD_BACKGROUND_COLOR)
        draw_grid(screen)
        apple.draw(screen)
        snake.draw(screen)
        draw_score(screen, score)
        draw_speed_indicator(screen, current_speed)

        pygame.display.flip()


if __name__ == '__main__':
    main()
