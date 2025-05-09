import random
import time
import os
import sys
import logging
from random import randint

import spidev as SPI

sys.path.append("..")
from PIL import Image, ImageDraw, ImageFont
from lib import LCD_1inch8
import RPi.GPIO as GPIO

# region LCD INIT

# GPIO configuration
GPIO.cleanup()
GPIO.setmode(GPIO.BCM)

# PINS configuration
PIN_RIGHT = 5
PIN_LEFT = 6
PIN_SHOOT = 13
PIN_SPECIAL = 19

# Ustawienie pinów jako wejścia
GPIO.setup(PIN_LEFT, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(PIN_RIGHT, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(PIN_SHOOT, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(PIN_SPECIAL, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Inicjalizacja wyświetlacza
lcd = LCD_1inch8.LCD_1inch8()
lcd.Init()
lcd.clear()
lcd.bl_DutyCycle(50)
image = Image.new("RGB", (lcd.width, lcd.height), "WHITE")
draw = ImageDraw.Draw(image)
font = ImageFont.load_default()

# endregion

# region Variables

# General settings
score = 0
lives = 3
max_count = 6
en_count = 0
row_count = 3
game_over = False

# Lists
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
drop_color = ["green", "blue", "yellow"]
drop_effects = {"green": "hp", "blue": "laser","yellow": "bomb" }

#Parametry Speciali
skill_time = 0
bomb_x = 0
bomb_y = 0
bomb_width = 10
bomb_height = 10
laser_x = 0
laser_y = 0
laser_width = 10
laser_height = lcd.height - 30

# Parametry przeciwników
enemy_width = 10
enemy_height = 8
enemy_speed = 0.3
enemy_hp = [1, 2, 3]
enemy_colors = ["orange", "red", "purple"]

# endregion

# region Funkcje Gracza


# Funkcja strzału
def shoot(channel):
    global bullets
    bullet_x = player_x + player_width / 2 - bullet_width / 2
    bullet_y = player_y
    bullets.append([bullet_x, bullet_y])


def special(channel):
    global lives,game_over,special_power, power, bomb_x ,bomb_y , laser_x, laser_y, skill_time
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

# region Update obiektów

def move_bullets():
    global bullets
    for bullet in bullets[:]:
        bullet[1] -= bullet_speed
        if bullet[1] < 0:
            bullets.remove(bullet)

def move_enemy_bullets():
    global enemy_bullets, lives, game_over
    for bullet in enemy_bullets[:]:
        bullet[1] += enemy_bullet_speed
        if bullet[1] > lcd.height - 10:
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
    global enemies, enemy_speed, game_over
    for enemy in enemies[:]:
        enemy[0] += enemy_speed
        if enemy[0] <= 0 or enemy[0] >= lcd.width - enemy_width:
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
        if bonus[1] > lcd.height - 10:
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
    if bomb_y > lcd.height - 20:
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
        if False:  # Jeśli obraz przeciwnika został wczytany
            lcd.ShowImage((enemy[0], enemy[1]),enemy_1)
        else:  # Fallback na prostokąt
            draw.rectangle((enemy[0], enemy[1], enemy[0] + enemy_width, enemy[1] + enemy_height), fill="orange")
    elif rank == enemy_colors[1]:
        if False:  # Jeśli obraz przeciwnika został wczytany
            lcd.ShowImage((enemy[0], enemy[1]), enemy_2)
        else:  # Fallback na prostokąt
            draw.rectangle((enemy[0], enemy[1], enemy[0] + enemy_width, enemy[1] + enemy_height), fill="red")
    elif rank == enemy_colors[2]:
        if False:  # Jeśli obraz przeciwnika został wczytany
            lcd.ShowImage((enemy[0], enemy[1]), enemy_3)
        else:  # Fallback na prostokąt
            draw.rectangle((enemy[0], enemy[1], enemy[0] + enemy_width, enemy[1] + enemy_height), fill="purple")
    return

def draw_game():
    draw.rectangle((0, 0, lcd.width, lcd.height), fill="WHITE")
    if True:
        draw.rectangle((player_x, player_y, player_x + player_width, player_y + player_height), fill="blue")
    for bullet in bullets:
        draw.rectangle((bullet[0], bullet[1], bullet[0] + bullet_width, bullet[1] + bullet_height), fill="red")
    for enemy in enemies:
        draw_enemies(enemy)
    for bullet in enemy_bullets:
        draw.rectangle((bullet[0], bullet[1], bullet[0] + bullet_width, bullet[1] + bullet_height), fill="orange")
    for bonus in drops:
        draw.rectangle((bonus[0], bonus[1], bonus[0] + drop_width, bonus[1] + drop_height), fill=bonus[2])
    if power == "bomb":
        draw.rectangle((bomb_x, bomb_y, bomb_x + bomb_width, bomb_y + bomb_height), fill="yellow")
    elif power == "laser":
        draw.rectangle((laser_x, laser_y, laser_x + laser_width, laser_y - laser_height), fill="blue")

    draw.rectangle((0, 112, lcd.width, lcd.height), fill="#33ccff")
    draw.text((10, 115), text=f"HP: {lives} Score: {score}", fill="black",font=font)
    draw.text((100, 115), text=f"S: {special_power}",fill="black",font=font)
    lcd.ShowImage(image)

def draw_game_over():
    mid_x = lcd.width // 2
    mid_y = lcd.height // 2
    draw.rectangle((mid_x - 30, mid_y - 15, mid_x + 30, mid_y + 15), fill="gray")
    draw.text((mid_x-25, mid_y-7), text="Game Over", fill="red",font=font)
    lcd.ShowImage(image)

# endregion

# region Funkcje Update

def check_collisions():
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
    free_space = lcd.width - enemy_width * en_row * 2 - 10
    if free_space < 0:
        en_row += -1
        free_space = lcd.width - enemy_width * en_row * 2 - 10
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
    """Reset the game to its initial state."""
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
    draw_game()
    time.sleep(0.02)

# endregion


# Funkcje ruchu
def move_left(channel):
    global player_x
    player_x = max(0, player_x - player_step)

def move_right(channel):
    global player_x
    player_x = min(lcd.width - player_width, player_x + player_step)

# Przypisanie zdarzeń do pinów
GPIO.add_event_detect(PIN_LEFT, GPIO.FALLING, callback=move_left, bouncetime=100)
GPIO.add_event_detect(PIN_RIGHT, GPIO.FALLING, callback=move_right, bouncetime=100)
GPIO.add_event_detect(PIN_SHOOT, GPIO.FALLING, callback=shoot, bouncetime=100)
GPIO.add_event_detect(PIN_SPECIAL, GPIO.FALLING, callback=special, bouncetime=200)

# Główna pętla gry
try:
    reset_game()
    while True:
        update()
except KeyboardInterrupt:
    print("END CTRL + C")
    GPIO.cleanup()
finally:
    GPIO.cleanup()
    lcd.clear()