import turtle
import random
import collections
import time

# إعدادات الشاشة
WIDTH, HEIGHT = 700, 750
GRID_SIZE = 20
GRID_WIDTH = 30
GRID_HEIGHT = 30
GAME_WIDTH = GRID_WIDTH * GRID_SIZE
GAME_HEIGHT = GRID_HEIGHT * GRID_SIZE

# اتجاهات الحركة
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# الألوان
BACKGROUND_COLOR = "#f0f8ff"
BORDER_COLOR = "#2c3e50"
SNAKE_HEAD_COLOR = "#145A32"
SNAKE_BODY_COLOR = "#27ae60r"
SNAKE_BODY_COLOR2 = "#229954"
FOOD_COLOR = "#e74c3c"
SCORE_BG_COLOR = "#34495e"
SCORE_TEXT_COLOR = "white"
GRID_COLOR = "#d6dbdf"

class Snake:
    def __init__(self):
        self.positions = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
        self.direction = RIGHT
        self.next_direction = RIGHT
        self.grow = False
        self.speed = 0.15
        
    def get_head_position(self):
        return self.positions[0]
    
    def update(self):
        self.direction = self.next_direction
        head = self.get_head_position()
        x, y = self.direction
        new_head = ((head[0] + x) % GRID_WIDTH, (head[1] + y) % GRID_HEIGHT)
        
        # منع الاصطدام الذاتي
        if new_head in self.positions[1:]:
            return self.avoid_self_collision()
            
        self.positions.insert(0, new_head)
        
        if not self.grow:
            self.positions.pop()
        else:
            self.grow = False
            
        return True
    
    def avoid_self_collision(self):
        """تجنب الاصطدام الذاتي باختيار اتجاه آمن"""
        head = self.get_head_position()
        safe_directions = []
        
        for direction in [UP, DOWN, LEFT, RIGHT]:
            x, y = direction
            new_head = ((head[0] + x) % GRID_WIDTH, (head[1] + y) % GRID_HEIGHT)
            
            if (direction[0] * -1, direction[1] * -1) == self.direction:
                continue
                
            if new_head not in self.positions[1:]:
                safe_directions.append(direction)
        
        if safe_directions:
            self.next_direction = random.choice(safe_directions)
            return self.update()
        
        for direction in [UP, DOWN, LEFT, RIGHT]:
            x, y = direction
            new_head = ((head[0] + x) % GRID_WIDTH, (head[1] + y) % GRID_HEIGHT)
            if new_head not in self.positions:
                self.next_direction = direction
                return self.update()
        
        return True
    
    def change_direction(self, direction):
        if (direction[0] * -1, direction[1] * -1) != self.direction:
            self.next_direction = direction
            
    def increase_speed(self):
        self.speed = max(0.05, 0.15 - (len(self.positions) * 0.001))

class Food:
    def __init__(self, snake_positions):
        self.position = self.randomize_position(snake_positions)
        
    def randomize_position(self, snake_positions):
        position = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
        while position in snake_positions:
            position = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
        return position

def find_safe_path(snake, food):
    """إيجاد مسار آمن يتجنب الاصطدام الذاتي"""
    start = snake.get_head_position()
    goal = food.position
    
    if goal in snake.positions:
        return None
    
    queue = collections.deque([[start]])
    seen = set([start])
    
    while queue:
        path = queue.popleft()
        x, y = path[-1]
        
        if (x, y) == goal:
            return path
        
        for dx, dy in [UP, DOWN, LEFT, RIGHT]:
            nx, ny = (x + dx) % GRID_WIDTH, (y + dy) % GRID_HEIGHT
            next_pos = (nx, ny)
            
            if next_pos in snake.positions and next_pos != snake.positions[-1]:
                continue
                
            if next_pos not in seen:
                queue.append(path + [next_pos])
                seen.add(next_pos)
    
    return None

def get_direction_from_path(path, snake_head):
    if not path or len(path) < 2:
        return None
        
    next_pos = path[1]
    head_x, head_y = snake_head
    next_x, next_y = next_pos
    
    dx = next_x - head_x
    dy = next_y - head_y
    
    if dx > 1:
        dx = -1
    elif dx < -1:
        dx = 1
    if dy > 1:
        dy = -1
    elif dy < -1:
        dy = 1
    
    if dx == 1:
        return RIGHT
    elif dx == -1:
        return LEFT
    elif dy == 1:
        return DOWN
    elif dy == -1:
        return UP
        
    return None

# ---- رسم القطع ----
def draw_snake_segment(t, x, y, size, color, is_head=False, direction=None):
    """رسم قطعة من جسم الثعبان بشكل أقرب للحقيقي"""
    cx = x * size - GAME_WIDTH//2 + size//2
    cy = y * size - GAME_HEIGHT//2 + size//2

    if is_head:
        # رأس الثعبان (بيضاوي)
        t.penup()
        t.goto(cx, cy - size//3)
        t.pendown()
        t.begin_fill()
        t.fillcolor(SNAKE_HEAD_COLOR)
        t.circle(size//2, steps=20)
        t.end_fill()

        # العيون
        eye_size = max(2, size//6)
        offset = size//4
        t.penup()
        if direction == RIGHT:
            eyes = [(cx + offset, cy + eye_size), (cx + offset, cy - eye_size)]
        elif direction == LEFT:
            eyes = [(cx - offset, cy + eye_size), (cx - offset, cy - eye_size)]
        elif direction == UP:
            eyes = [(cx - eye_size, cy + offset), (cx + eye_size, cy + offset)]
        else:  # DOWN
            eyes = [(cx - eye_size, cy - offset), (cx + eye_size, cy - offset)]
        
        for ex, ey in eyes:
            t.goto(ex, ey)
            t.pendown()
            t.dot(eye_size, "white")
            t.dot(max(1, eye_size//2), "black")
            t.penup()

        # لسان (رسم سريع)
        t.pencolor("red")
        t.pensize(2)
        t.goto(cx, cy)
        if direction == RIGHT:
            t.setheading(0)
        elif direction == LEFT:
            t.setheading(180)
        elif direction == UP:
            t.setheading(90)
        else:
            t.setheading(270)
        t.pendown()
        t.forward(size * 0.6)
        # شكل لسان بسيط
        t.right(30)
        t.forward(size * 0.18)
        t.backward(size * 0.18)
        t.left(60)
        t.forward(size * 0.18)
        t.penup()
        t.pensize(1)
        t.pencolor("black")
        t.setheading(0)
    else:
        # جسم الثعبان (دوائر متدرجة مع تأثير حراشف صغير)
        t.penup()
        t.goto(cx, cy - size//3)
        t.pendown()
        t.begin_fill()
        t.fillcolor(color)
        t.circle(size//2 * 0.9, steps=20)
        t.end_fill()
        
        # "حراشف" نقطية داخلية لعمق بصري بسيط
        t.penup()
        t.goto(cx, cy)
        t.pendown()
        t.dot(max(1, size//3), "#196F3D")
        t.penup()

def draw_food(t, x, y, size):
    """رسم الطعام بشكل تفاحة واقعية بسيطة"""
    cx = x * size - GAME_WIDTH//2 + size//2
    cy = y * size - GAME_HEIGHT//2 + size//2

    # جسم التفاحة
    t.penup()
    t.goto(cx, cy - size//3)
    t.pendown()
    t.begin_fill()
    t.fillcolor(FOOD_COLOR)
    t.circle(size//2 * 0.8)
    t.end_fill()

    # الساق
    t.penup()
    t.goto(cx, cy + size * 0.28)
    t.pendown()
    t.pensize(2)
    t.pencolor("#8B4513")
    t.goto(cx, cy + size * 0.45)
    t.pensize(1)
    t.pencolor("black")
    t.penup()

    # ورقة خضراء صغيرة
    t.penup()
    t.goto(cx + size * 0.14, cy + size * 0.43)
    t.pendown()
    t.begin_fill()
    t.fillcolor("green")
    t.circle(max(1, int(size * 0.12)))
    t.end_fill()
    t.penup()

# ---- خلفية ثابتة وHUD ----
def draw_background(bg):
    """ارسم الشبكة والحدود ومنطقة النقاط (ثابت مرة واحدة)"""
    # الشبكة
    bg.color(GRID_COLOR)
    bg.pensize(1)
    for y in range(GRID_HEIGHT + 1):
        bg.penup()
        bg.goto(-GAME_WIDTH//2, y * GRID_SIZE - GAME_HEIGHT//2)
        bg.pendown()
        bg.goto(GAME_WIDTH//2, y * GRID_SIZE - GAME_HEIGHT//2)
    
    for x in range(GRID_WIDTH + 1):
        bg.penup()
        bg.goto(x * GRID_SIZE - GAME_WIDTH//2, -GAME_HEIGHT//2)
        bg.pendown()
        bg.goto(x * GRID_SIZE - GAME_WIDTH//2, GAME_HEIGHT//2)

    # الحدود الخارجية
    bg.penup()
    bg.goto(-GAME_WIDTH//2, -GAME_HEIGHT//2)
    bg.pendown()
    bg.pensize(3)
    bg.color(BORDER_COLOR)
    for _ in range(2):
        bg.forward(GAME_WIDTH)
        bg.left(90)
        bg.forward(GAME_HEIGHT)
        bg.left(90)
    bg.pensize(1)

    # صندوق النقاط (خلفية ثابتة)
    score_width = 160
    score_height = 70
    bg.penup()
    bg.goto(-score_width//2, GAME_HEIGHT//2 + 10)
    bg.pendown()
    bg.begin_fill()
    bg.fillcolor(SCORE_BG_COLOR)
    for _ in range(2):
        bg.forward(score_width)
        bg.left(90)
        bg.forward(score_height)
        bg.left(90)
    bg.end_fill()

    # نص ثابت "اضغط Q للخروج"
    bg.penup()
    bg.goto(0, GAME_HEIGHT//2 + 15)
    bg.color(SCORE_TEXT_COLOR)
    bg.write("اضغط Q للخروج", align="center", font=("Arial", 12, "normal"))
    bg.penup()

def draw_score_hud(hud, score):
    hud.clear()
    hud.penup()
    hud.goto(0, GAME_HEIGHT//2 + 40)
    hud.color(SCORE_TEXT_COLOR)
    hud.write(f"النقاط: {score}", align="center", font=("Arial", 20, "bold"))
    hud.penup()

# ---- البرنامج الرئيسي ----
def main():
    screen = turtle.Screen()
    screen.setup(WIDTH, HEIGHT)
    screen.title("لعبة الثعبان - شكل واقعي (ثابت الخلفية)")
    screen.bgcolor(BACKGROUND_COLOR)
    screen.tracer(0)  # نتحكم نحن بالتحديث

    screen.listen()

    # خلفية ثابتة (ترسم مرة واحدة)
    bg = turtle.Turtle()
    bg.hideturtle()
    bg.speed(0)
    bg.penup()

    # HUD (للنقاط المتغيرة)
    hud = turtle.Turtle()
    hud.hideturtle()
    hud.speed(0)
    hud.penup()

    # قلم رئيسي للرسم المتكرر (الثعبان + الطعام)
    pen = turtle.Turtle()
    pen.hideturtle()
    pen.speed(0)
    pen.penup()

    # ارسم الخلفية مرة واحدة
    draw_background(bg)

    snake = Snake()
    food = Food(snake.positions)
    score = 0
    running = True
    should_quit = False

    def quit_game():
        nonlocal should_quit
        should_quit = True

    screen.onkeypress(quit_game, "q")
    screen.onkeypress(quit_game, "Q")

    # رسم أولي للنقاط
    draw_score_hud(hud, score)
    screen.update()

    while running:
        if should_quit:
            break

        path = find_safe_path(snake, food)
        if path:
            direction = get_direction_from_path(path, snake.get_head_position())
            if direction:
                snake.change_direction(direction)

        snake.update()

        # أكل الطعام
        if snake.get_head_position() == food.position:
            snake.grow = True
            food = Food(snake.positions)
            score += 1
            snake.increase_speed()

        # نظف فقط الرسم المتحرك ثم ارسم الثعبان والطعام وHUD
        pen.clear()
        hud.clear()

        # رسم الثعبان
        for i, (x, y) in enumerate(snake.positions):
            if i == 0:
                draw_snake_segment(pen, x, y, GRID_SIZE, SNAKE_HEAD_COLOR, True, snake.direction)
            else:
                color = SNAKE_BODY_COLOR if i % 2 == 0 else SNAKE_BODY_COLOR2
                draw_snake_segment(pen, x, y, GRID_SIZE, color, False, None)

        # رسم الطعام
        draw_food(pen, food.position[0], food.position[1], GRID_SIZE)

        # تحديث HUD للنقاط
        draw_score_hud(hud, score)

        # تحديث واحد لكل إطار
        screen.update()
        time.sleep(snake.speed)

    # رسالة الوداع
    pen.clear()
    hud.clear()
    pen.penup()
    pen.goto(0, 0)
    pen.color(BORDER_COLOR)
    pen.write(f"شكراً للعب! النقاط النهائية: {score}", align="center", font=("Arial", 24, "bold"))
    screen.update()
    time.sleep(2)
    screen.bye()

if __name__ == "__main__":
    main()
