import tkinter as tk
import random
import time
from PIL import Image, ImageTk

# Window dimensions
WINDOW_WIDTH = 160
WINDOW_HEIGHT = 128

# region Variables

# General settings
score = 0
lives = 3
max_count = 6
en_count = 0
row_count = 3
game_over = False

#Lists
enemies = []  # Lista przeciwników
drops = []  # Lista dropów
bullets = []  # Lista pocisków gracza
enemy_bullets = []  # Lista pocisków przeciwników

# Player parameters
player_x = 50
player_y = 100
player_width = 10
player_height = 8
player_step = 5

# Parametry pocisków
bullet_width = 3
bullet_height = 5
bullet_speed = 6
enemy_bullet_speed = 3

#Parametry bonusów
drop_width = 6
drop_height = 4
special_power = "none"
power = "none"
drop_color = ["green", "light blue", "yellow"]
drop_effects = {"green": "hp", "light blue": "laser","yellow": "bomb" }

#Parametry Speciali
skill_time = 0
bomb_x = 0
bomb_y = 0
bomb_width = 10
bomb_height = 10
laser_x = 0
laser_y = 0
laser_width = 10
laser_height = WINDOW_HEIGHT - 30

# Parametry przeciwników
enemy_width = 10
enemy_height = 8
enemy_speed = 0.3
enemy_hp = [1, 2, 3]
enemy_colors = ["orange", "red", "purple"]

# Key states
keys_pressed = {"Left": False, "Right": False}

# endregion

# region Funkcje Gracza

def shoot(event=None):
    """Shoot a bullet."""
    global bullets
    bullet_x = player_x + player_width / 2 - bullet_width / 2
    bullet_y = player_y
    bullets.append([bullet_x, bullet_y])

def special(event=None):
    """Special ability to reset the game."""
    global lives,game_over,special_power, power, bomb_x,bomb_y, laser_x, laser_y, skill_time
    if game_over:
        lives=3
        game_over = False
        reset_game()
        special_power="none"
        return
    if special_power=="none":
        return
    elif special_power=="hp":
        lives+=1
        special_power = "none"
        return
    elif special_power=="laser":
        special_power = "none"
        skill_time = time.time()
        laser_x = player_x + player_width / 2 - laser_width / 2
        laser_y = player_y
        power = "laser"
        return
    elif special_power=="bomb":
        power = "bomb"
        bomb_x = player_x + player_width / 2 - bomb_width / 2
        bomb_y = player_y
        special_power="none"
        return
    return

# endregion

# region Update obietków

def move_bullets():
    """Move bullets upward."""
    global bullets
    for bullet in bullets[:]:
        bullet[1] -= bullet_speed
        if bullet[1] < 0:
            bullets.remove(bullet)

def move_enemy_bullets():
    """Move enemy bullets downward and check for collision with the player."""
    global enemy_bullets, lives, game_over
    for bullet in enemy_bullets[:]:
        bullet[1] += enemy_bullet_speed
        if bullet[1] > WINDOW_HEIGHT - 10:
            enemy_bullets.remove(bullet)
        elif (bullet[0] < player_x + player_width and
              bullet[0] + bullet_width > player_x and
              bullet[1] < player_y + player_height and
              bullet[1] + bullet_height > player_y):
            enemy_bullets.remove(bullet)
            lives -= 1
            if lives < 1:
                game_over = True

def move_enemies():
    """Move enemies and randomly shoot bullets."""
    global enemies, enemy_speed, game_over
    for enemy in enemies[:]:
        enemy[0] += enemy_speed
        if enemy[0] <= 0 or enemy[0] >= WINDOW_WIDTH - enemy_width:
            for e in enemies:
                e[1] += enemy_height
                if e[1] > player_y - player_height:
                    game_over = True
            enemy_speed *= -1
        if random.randint(1, 100) <= 1:  # 1% chance to shoot
            bullet_x = enemy[0] + enemy_width / 2 - bullet_width / 2
            bullet_y = enemy[1] + enemy_height
            enemy_bullets.append([bullet_x, bullet_y])

def move_bonuses():
    global drops, special_power
    for bonus in drops[:]:
        bonus[1] += enemy_bullet_speed
        if bonus[1] > WINDOW_HEIGHT - 10:
            drops.remove(bonus)
        elif (bonus[0] < player_x + player_width and
              bonus[0] + drop_width > player_x and
              bonus[1] < player_y + player_height and
              bonus[1] + drop_height > player_y):
            drops.remove(bonus)
            special_power = bonus[3]

def move_bomb():
    global bomb_x, bomb_y, power, score, en_count
    bomb_y += -bullet_speed
    if bomb_y > WINDOW_HEIGHT - 20:
        power = "none"
        return
    for enemy in enemies[:]:
        if (bomb_x < enemy[0] + enemy_width and
                bomb_x + bomb_width > enemy[0] and
                bomb_y < enemy[1] + enemy_height and
                bomb_y + bomb_height > enemy[1]):
                enemies.remove(enemy)
                en_count -= 1
                if enemy[2] == "orange":
                    score += 10
                elif enemy[2] == "red":
                    score += 30
                elif enemy[2] == "purple":
                    score += 50

def move_laser():
    global laser_x, laser_y, power, score, en_count
    if time.time() - skill_time > 1.2:
        power = "none"
        return
    laser_x = player_x + player_width / 2 - laser_width / 2
    for enemy in enemies[:]:
        if laser_x < enemy[0] + enemy_width and laser_x + laser_width > enemy[0]:
                enemies.remove(enemy)
                en_count -= 1
                if enemy[2] == "orange":
                    score += 10
                elif enemy[2] == "red":
                    score += 30
                elif enemy[2] == "purple":
                    score += 50

# endregion

# region Funkcje Draw


def draw_enemies(enemy):
    rank = enemy[2]
    if rank == enemy_colors[0]:
        if enemy1_photo:  # Jeśli obraz przeciwnika został wczytany
            canvas.create_image(enemy[0], enemy[1], anchor=tk.NW, image=enemy1_photo)
        else:  # Fallback na prostokąt
            canvas.create_rectangle(enemy[0], enemy[1], enemy[0] + enemy_width, enemy[1] + enemy_height, fill="orange")
    elif rank == enemy_colors[1]:
        if enemy2_photo:  # Jeśli obraz przeciwnika został wczytany
            canvas.create_image(enemy[0], enemy[1], anchor=tk.NW, image=enemy2_photo)
        else:  # Fallback na prostokąt
            canvas.create_rectangle(enemy[0], enemy[1], enemy[0] + enemy_width, enemy[1] + enemy_height, fill="red")
    elif rank == enemy_colors[2]:
        if enemy3_photo:  # Jeśli obraz przeciwnika został wczytany
            canvas.create_image(enemy[0], enemy[1], anchor=tk.NW, image=enemy3_photo)
        else:  # Fallback na prostokąt
            canvas.create_rectangle(enemy[0], enemy[1], enemy[0] + enemy_width, enemy[1] + enemy_height, fill="purple")
    return

def draw():
    """Draw all game elements."""
    canvas.delete("all")
    if player_photo:
        canvas.create_image(player_x, player_y, anchor=tk.NW, image=player_photo)
    else:
        canvas.create_rectangle(player_x, player_y, player_x + player_width, player_y + player_height, fill="blue")
    for bullet in bullets:
        canvas.create_rectangle(bullet[0], bullet[1], bullet[0] + bullet_width, bullet[1] + bullet_height, fill="red")
    for enemy in enemies:
        draw_enemies(enemy)
    for bullet in enemy_bullets:
        canvas.create_rectangle(bullet[0], bullet[1], bullet[0] + bullet_width, bullet[1] + bullet_height, fill="orange")
    for bonus in drops:
        canvas.create_rectangle(bonus[0], bonus[1], bonus[0] + drop_width, bonus[1] + drop_height, fill=bonus[2])
    if power == "bomb":
        canvas.create_rectangle(bomb_x, bomb_y, bomb_x + bomb_width, bomb_y + bomb_height, fill="yellow")
    elif power == "laser":
        canvas.create_rectangle(laser_x, laser_y, laser_x + laser_width, laser_y - laser_height, fill="blue")

    canvas.create_rectangle(0, 112, WINDOW_WIDTH, WINDOW_HEIGHT, fill="light blue")
    canvas.create_text(55, 120, text=f"HP: {lives} Score: {score}", fill="black")
    canvas.create_text(120, 120, text=f"S: {special_power}",fill="black")

def draw_game_over():
    mid_x = WINDOW_WIDTH // 2
    mid_y = WINDOW_HEIGHT // 2
    canvas.create_rectangle(mid_x - 30, mid_y - 15, mid_x + 30, mid_y + 15, fill="gray")
    canvas.create_text(mid_x, mid_y, text="Game Over", fill="red")

# endregion

# region Funkcje Update

def check_collisions():
    """Check collisions between bullets and enemies."""
    global bullets, enemies, score, en_count
    for bullet in bullets[:]:
        for enemy in enemies[:]:
            if (bullet[0] < enemy[0] + enemy_width and
                bullet[0] + bullet_width > enemy[0] and
                bullet[1] < enemy[1] + enemy_height and
                bullet[1] + bullet_height > enemy[1]):
                bullets.remove(bullet)
                enemy[3] += -1
                if enemy[3] < 1:
                    if enemy[2] == "orange":
                        score += 10
                    elif enemy[2] == "red":
                        score += 30
                    elif enemy[2] == "purple":
                        score += 50
                    if random.random() < 0.8:  # 50% szans na drop
                        drop_rank = random.choice(list(drop_color))
                        bonus_x = enemy[0] + enemy_width / 2 - bullet_width / 2
                        bonus_y = enemy[1] + enemy_height
                        drops.append([bonus_x, bonus_y, drop_rank,drop_effects[drop_rank]])
                    enemies.remove(enemy)
                    en_count -= 1
                break

def set_level():
    global max_count, en_count, row_count
    en_row = int(random.randint(4, max_count))
    en_count = en_row * row_count
    free_space = WINDOW_WIDTH - enemy_width * en_row * 2 - 10
    if free_space < 0:
        en_row += -1
        free_space = WINDOW_WIDTH - enemy_width * en_row * 2 - 10
    for i in range(row_count):
        free = random.randint(0, free_space)
        rank = random.choice(list(enemy_colors))
        if rank=="orange":
            hp=1
        elif rank=="red":
            hp=2
        else:
            hp=3
        for j in range(en_row):
            enemies.append([free, 15 * i,rank , hp])
            free += enemy_width * 2

def reset_game():
    global player_x, player_y, bullets, enemies, enemy_bullets, lives, enemy_speed
    player_x = 50
    player_y = 100
    bullets.clear()
    enemies.clear()
    enemy_bullets.clear()
    enemy_speed = 0.3
    set_level()
    update()

def update():
    global game_over, power
    if game_over:
        draw_game_over()
        return
    if en_count <= 0:
        set_level()
    if power == "bomb":
        move_bomb()
    elif power == "laser":
        move_laser()
    move_bullets()
    move_enemy_bullets()
    move_enemies()
    move_bonuses()
    check_collisions()
    apply_movement()
    draw()
    root.after(20, update)

# endregion



def apply_movement():
    """Move the player based on key presses."""
    global player_x
    if keys_pressed["Left"]:
        player_x = max(0, player_x - player_step)
    if keys_pressed["Right"]:
        player_x = min(WINDOW_WIDTH - player_width, player_x + player_step)

def key_press(event):
    if event.keysym in keys_pressed:
        keys_pressed[event.keysym] = True

def key_release(event):
    if event.keysym in keys_pressed:
        keys_pressed[event.keysym] = False

# Set up the main window
root = tk.Tk()
root.title("Shooter Game")
root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT + 20}")
root.resizable(False, False)

try:
    enemy_1 = Image.open("Ship1.png")
    #enemy_1 = enemy_1.resize((enemy_width*2, enemy_height*2))  # Skalowanie obrazu
    enemy_2 = Image.open("Ship2.png")
    #enemy_2 = enemy_2.resize((enemy_width * 2, enemy_height * 2))  # Skalowanie obrazu
    enemy_3 = Image.open("Ship3.png")
    #enemy_3 = enemy_3.resize((enemy_width * 2, enemy_height * 2))  # Skalowanie obrazu
    player = Image.open("Player.png")
    #player = player.resize((player_width * 2, player_height * 2))  # Skalowanie obrazu
    enemy1_photo = ImageTk.PhotoImage(enemy_1)
    enemy2_photo = ImageTk.PhotoImage(enemy_2)
    enemy3_photo = ImageTk.PhotoImage(enemy_3)
    player_photo = ImageTk.PhotoImage(player)
except Exception as e:
    print("Nie udało się wczytać obrazu przeciwnika:", e)
    enemy1_photo = None
    enemy2_photo = None
    enemy3_photo = None
    player_photo = None

# Create the canvas
canvas = tk.Canvas(root, width=WINDOW_WIDTH, height=WINDOW_HEIGHT, bg="light gray")
canvas.pack()

# Bind keys
root.bind("<KeyPress>", key_press)
root.bind("<KeyRelease>", key_release)
root.bind("<space>", shoot)
root.bind("<r>", special)

# Start the game
reset_game()
root.mainloop()
