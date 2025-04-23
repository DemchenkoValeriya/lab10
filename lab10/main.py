import psycopg2
import pygame
import sys
import random
import time
import copy

# Database connection
conn = psycopg2.connect(
    dbname='lab10',
    user='postgres',
    password='dfgh4639ryei0288ksk4',
    host='localhost',
    port='5432'
)
cur = conn.cursor()

# Choose: new player or returning player
mode = input("New player or returning player? (new/returning): ").strip().lower()
username = input("Enter your name: ").strip()

user_id = None
score = 0
level = 0
SPEED = 10

cur.execute("SELECT id FROM users WHERE username = %s", (username,))
user = cur.fetchone()

if mode == "new":
    if not user:
        cur.execute("INSERT INTO users (username) VALUES (%s) RETURNING id", (username,))
        user_id = cur.fetchone()[0]
        conn.commit()
    else:
        user_id = user[0]
    score = 0
    level = 0

elif mode == "returning":
    if user:
        user_id = user[0]
        cur.execute("SELECT score, level FROM user_score WHERE user_id = %s ORDER BY saved_at DESC LIMIT 1", (user_id,))
        row = cur.fetchone()
        score = row[0] if row else 0
        level = row[1] if row else 0
        SPEED += level
        print(f"Welcome back, {username}! Your current level is {level} and your score is {score}.")
    else:
        print("This user was not found.")
        sys.exit()
else:
    print("You must enter either 'new' or 'returning'!")
    sys.exit()

print("The game will start in 5 seconds...")
time.sleep(5)

# Game Setup
pygame.init()
scale = 15
food_x = 10
food_y = 10
display = pygame.display.set_mode((500, 500))
pygame.display.set_caption("Snake Game")
clock = pygame.time.Clock()

background_top = (0, 0, 50)
background_bottom = (0, 0, 0)
snake_colour = (255, 137, 0)
food_colour = (random.randint(1, 255), random.randint(1, 255), random.randint(1, 255))
snake_head = (255, 247, 0)
font_colour = (255, 255, 255)
defeat_colour = (255, 0, 0)

class Snake:
    def __init__(self, x_start, y_start):
        self.x = x_start
        self.y = y_start
        self.w = scale
        self.h = scale
        self.x_dir = 1
        self.y_dir = 0
        self.history = [[self.x, self.y]]
        self.length = 1

    def reset(self):
        self.x = 250 - scale
        self.y = 250 - scale
        self.x_dir = 1
        self.y_dir = 0
        self.history = [[self.x, self.y]]
        self.length = 1

    def show(self):
        for i in range(self.length):
            color = snake_head if i == 0 else snake_colour
            pygame.draw.rect(display, color, (self.history[i][0], self.history[i][1], self.w, self.h))

    def check_eaten(self):
        return abs(self.history[0][0] - food_x) < scale and abs(self.history[0][1] - food_y) < scale

    def check_level(self):
        global level
        return self.length % 5 == 0

    def grow(self):
        self.length += 1
        self.history.append(self.history[self.length - 2])

    def death(self):
        for i in range(1, self.length):
            if abs(self.history[0][0] - self.history[i][0]) < self.w and abs(self.history[0][1] - self.history[i][1]) < self.h and self.length > 2:
                return True
        return False

    def update(self):
        for i in range(self.length - 1, 0, -1):
            self.history[i] = copy.deepcopy(self.history[i - 1])
        self.history[0][0] += self.x_dir * scale
        self.history[0][1] += self.y_dir * scale

class Food:
    def new_location(self):
        global food_x, food_y
        food_x = random.randrange(1, int(500 / scale) - 1) * scale
        food_y = random.randrange(1, int(500 / scale) - 1) * scale

    def show(self):
        pygame.draw.rect(display, food_colour, (food_x, food_y, scale, scale))

def show_score():
    font = pygame.font.SysFont(None, 20)
    text = font.render("Score: " + str(score), True, font_colour)
    display.blit(text, (scale, scale))

def show_level():
    font = pygame.font.SysFont(None, 20)
    text = font.render("Level: " + str(level), True, font_colour)
    display.blit(text, (90 - scale, scale))

def save_game_state():
    global score, level
    cur.execute("INSERT INTO user_score (user_id, score, level) VALUES (%s, %s, %s)", (user_id, score, level))
    conn.commit()
    print("Game state saved to the database.")

def gameLoop():
    global score, level, SPEED
    snake = Snake(250, 250)
    food = Food()
    food.new_location()
    game_paused = False

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:  # Quit the game
                    return
                if event.key == pygame.K_p:  # Pause or resume the game
                    game_paused = not game_paused
                    if game_paused:
                        save_game_state()
                        print("Game paused. Current game state saved.")

                if not game_paused:
                    if snake.y_dir == 0:
                        if event.key == pygame.K_UP:
                            snake.x_dir = 0
                            snake.y_dir = -1
                        if event.key == pygame.K_DOWN:
                            snake.x_dir = 0
                            snake.y_dir = 1
                    if snake.x_dir == 0:
                        if event.key == pygame.K_LEFT:
                            snake.x_dir = -1
                            snake.y_dir = 0
                        if event.key == pygame.K_RIGHT:
                            snake.x_dir = 1
                            snake.y_dir = 0

        if not game_paused:
            for y in range(500):
                color = (
                    background_top[0] + (background_bottom[0] - background_top[0]) * y / 500,
                    background_top[1] + (background_bottom[1] - background_top[1]) * y / 500,
                    background_top[2] + (background_bottom[2] - background_top[2]) * y / 500
                )
                pygame.draw.line(display, color, (0, y), (500, y))

            snake.show()
            snake.update()
            food.show()
            show_score()
            show_level()

            if snake.check_eaten():
                food.new_location()
                score += random.randint(1, 5)
                snake.grow()

            if snake.check_level():
                level += 1
                SPEED += 1
                snake.grow()

            if snake.death():
                font = pygame.font.SysFont(None, 100)
                text = font.render("Game Over!", True, defeat_colour)
                display.blit(text, (50, 200))
                pygame.display.update()
                time.sleep(3)
                return

            if snake.history[0][0] > 500: snake.history[0][0] = 0
            if snake.history[0][0] < 0: snake.history[0][0] = 500
            if snake.history[0][1] > 500: snake.history[0][1] = 0
            if snake.history[0][1] < 0: snake.history[0][1] = 500

            pygame.display.update()
            clock.tick(SPEED)

# Run the game
gameLoop()

# Close database connection
cur.close()
conn.close()
