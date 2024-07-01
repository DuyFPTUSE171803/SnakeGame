import pygame
import random
from enum import Enum
from collections import namedtuple
import numpy as np

pygame.init()
pygame.mixer.init()
font = pygame.font.Font('arial.ttf', 25)

# Constants
BLOCK_SIZE = 20
SPEED = 20

# Colors
WHITE = (255, 255, 255)
GREEN = (0, 205, 0)
DARK_GREEN = (0, 100, 0)
BLACK = (0, 0, 0)
RED = (200, 0, 0)

# Sound
eat_sound = pygame.mixer.Sound('eat.mp3')  # Ensure you have this sound file

# Load images
food_image = pygame.image.load('apple.jpg')  # Load an image for the food
food_image = pygame.transform.scale(food_image, (BLOCK_SIZE, BLOCK_SIZE))
background_image = pygame.image.load('bg.jpeg')

class Direction(Enum):
    RIGHT = 1
    LEFT = 2
    UP = 3
    DOWN = 4

Point = namedtuple('Point', 'x, y')

class SnakeGame:
    def __init__(self, w=640, h=480):
        self.w = w
        self.h = h
        self.display = pygame.display.set_mode((self.w, self.h))
        pygame.display.set_caption('Snake')
        self.clock = pygame.time.Clock()
        self.reset()
        self.background = pygame.transform.scale(background_image, (self.w, self.h))

    def reset(self):
        self.direction = Direction.RIGHT
        self.head = Point(self.w / 2, self.h / 2)
        self.snake = [self.head,
                      Point(self.head.x - BLOCK_SIZE, self.head.y),
                      Point(self.head.x - (2 * BLOCK_SIZE), self.head.y)]
        self.score = 0
        self.food = None
        self._place_food()
        self.frame_iteration = 0

    def _place_food(self):
        x = random.randint(0, (self.w - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
        y = random.randint(0, (self.h - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
        self.food = Point(x, y)
        if self.food in self.snake:
            self._place_food()

    def _update_ui(self):
        self.display.blit(self.background, (0, 0))
        for pt in self.snake:
            if pt == self.head:
                pygame.draw.rect(self.display, DARK_GREEN, pygame.Rect(pt.x, pt.y, BLOCK_SIZE, BLOCK_SIZE))
            else:
                pygame.draw.rect(self.display, GREEN, pygame.Rect(pt.x, pt.y, BLOCK_SIZE, BLOCK_SIZE))
                pygame.draw.rect(self.display, BLACK, pygame.Rect(pt.x + 4, pt.y + 4, BLOCK_SIZE - 8, BLOCK_SIZE - 8))

        self.display.blit(food_image, (self.food.x, self.food.y))

        text = font.render("Score: " + str(self.score), True, WHITE)
        self.display.blit(text, [0, 0])
        pygame.display.flip()

    def play_step(self, action):
        self.frame_iteration += 1
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        self._move(action)
        self.snake.insert(0, self.head)

        reward = 0
        game_over = False
        if self.is_collision(self.head):
            game_over = True
            reward = -10
            return reward, game_over, self.score

        if self.head == self.food:
            self.score += 1
            self._place_food()
            eat_sound.play()
            reward = 10
        else:
            self.snake.pop()

        self._update_ui()
        self.clock.tick(SPEED)
        return reward, game_over, self.score

    def is_collision(self, pt):
        # Check if the point hits the boundaries of the game
        if pt.x >= self.w or pt.x < 0 or pt.y >= self.h or pt.y < 0:
            return True
        # Check if the point is any part of the snake, excluding the tail unless the snake just ate
        if pt in self.snake[1:]:
            return True
        return False

    def _move(self, action):
        direction_order = [Direction.RIGHT, Direction.DOWN, Direction.LEFT, Direction.UP]
        idx = direction_order.index(self.direction)

        if np.array_equal(action, [1, 0, 0]):
            new_dir = direction_order[idx]
        elif np.array_equal(action, [0, 1, 0]):
            new_dir = direction_order[(idx + 1) % 4]
        else:
            new_dir = direction_order[(idx - 1) % 4]

        self.direction = new_dir
        x, y = self.head.x, self.head.y
        if self.direction == Direction.RIGHT:
            x += BLOCK_SIZE
        elif self.direction == Direction.LEFT:
            x -= BLOCK_SIZE
        elif self.direction == Direction.DOWN:
            y += BLOCK_SIZE
        elif self.direction == Direction.UP:
            y -= BLOCK_SIZE

        self.head = Point(x, y)

if __name__ == '__main__':
    game = SnakeGame()
    while True:
        reward, game_over, score = game.play_step([1, 0, 0])
        if game_over:
            break

    print('Final Score', score)
    pygame.quit()
