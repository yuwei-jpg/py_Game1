import pygame

from GMB.Level.level import Level_Background, screen
from GMB.Particles.particles import Trail
from GMB.World.world import load_level, World
from projectiles import Bullet, Grenade
from GMB.Button.button import Button
from GMB.Text.texts import Text, Message, MessageBox
from GMB.player import Player

pygame.init()

WIDTH, HEIGHT = 640, 384
win = pygame.display.set_mode((WIDTH, HEIGHT), pygame.NOFRAME)
TILE_SIZE = 16

clock = pygame.time.Clock()
FPS = 45

# IMAGES **********************************************************************

BG5 = pygame.transform.scale(pygame.image.load('assets/BG5.png'), (WIDTH, HEIGHT))
BG2 = pygame.transform.scale(pygame.image.load('assets/BG2.png'), (WIDTH, HEIGHT))
BG3 = pygame.transform.scale(pygame.image.load('assets/BG3.png'), (WIDTH, HEIGHT))
MOON = pygame.transform.scale(pygame.image.load('assets/moon.png'), (295, 220))

# FONTS ***********************************************************************

title_font = "Fonts/Aladin-Regular.ttf"
instructions_font = 'Fonts/BubblegumSans-Regular.ttf'
about_intro_font = 'Fonts/DalelandsUncialBold-82zA.ttf'
about_intro_font2 = 'Fonts/times new roman bold.ttf'
GMB = Message(WIDTH // 2 + 5, HEIGHT // 2 - 90, 90, "Gem Mech Battle", title_font, (255, 255, 255), win)
left_key = Message(WIDTH // 2 + 10, HEIGHT // 2 - 125, 20, "Press A key to go left", instructions_font,
                   (255, 255, 255), win)
right_key = Message(WIDTH // 2 + 10, HEIGHT // 2 - 100, 20, "Press D key to go right", instructions_font,
                    (255, 255, 255), win)
up_key = Message(WIDTH // 2 + 10, HEIGHT // 2 - 75, 20, "Press W key to jump", instructions_font,
                 (255, 255, 255), win)
space_key = Message(WIDTH // 2 + 10, HEIGHT // 2 - 50, 20, "Press space key to shoot", instructions_font,
                    (255, 255, 255), win)
g_key = Message(WIDTH // 2 + 10, HEIGHT // 2 - 25, 20, "Press G key to throw grenade", instructions_font,
                (255, 255, 255), win)
w_key = Message(WIDTH // 2 + 10, HEIGHT // 2 - 0, 20, "Press S key to defend (4 times)", instructions_font,
                (255, 255, 255), win)
game_won_msg = Message(WIDTH // 2 + 10, HEIGHT // 2 - 5, 20, "You have won the game", instructions_font,
                       (255, 255, 255), win)
t = Text(instructions_font, 18)
font_color = (12, 12, 12)
play = t.render('Play', font_color)
level_text = t.render('Level', font_color)
about = t.render('About', font_color)
controls = t.render('Controls', font_color)
exit = t.render('Exit', font_color)
main_menu = t.render('Main Menu', font_color)

about_font = pygame.font.SysFont('Times New Roman', 20)
counter_font = pygame.font.Font(None, 25)

with open('Data/about.txt') as f:
    info = f.read().replace('\n', ' ')

# BUTTONS *********************************************************************

ButtonBG = pygame.image.load('Assets/ButtonBG.png')
bwidth = ButtonBG.get_width()

play_btn = Button(WIDTH // 2 - bwidth // 4, HEIGHT // 2, ButtonBG, 0.5, play, 10)
level_btn = Button(WIDTH // 2 - bwidth // 4, HEIGHT // 2 + 30, ButtonBG, 0.5, level_text, 10)
about_btn = Button(WIDTH // 2 - bwidth // 4, HEIGHT // 2 + 60, ButtonBG, 0.5, about, 10)
controls_btn = Button(WIDTH // 2 - bwidth // 4, HEIGHT // 2 + 90, ButtonBG, 0.5, controls, 10)
exit_btn = Button(WIDTH // 2 - bwidth // 4, HEIGHT // 2 + 120, ButtonBG, 0.5, exit, 10)
main_menu_btn = Button(WIDTH // 2 - bwidth // 4, HEIGHT // 2 + 150, ButtonBG, 0.5, main_menu, 20)

# MUSIC ***********************************************************************

pygame.mixer.music.load('Sounds/menu2.mp3')
pygame.mixer.music.play(loops=-1)
pygame.mixer.music.set_volume(0.5)

diamond_fx = pygame.mixer.Sound('Sounds/point.mp3')
diamond_fx.set_volume(0.6)
bullet_fx = pygame.mixer.Sound('Sounds/bullet.wav')
jump_fx = pygame.mixer.Sound('Sounds/jump.mp3')
health_fx = pygame.mixer.Sound('Sounds/health.wav')
menu_click_fx = pygame.mixer.Sound('Sounds/menu.mp3')
next_level_fx = pygame.mixer.Sound('Sounds/level.mp3')
grenade_throw_fx = pygame.mixer.Sound('Sounds/grenade throw.wav')
grenade_throw_fx.set_volume(0.6)

# GROUPS **********************************************************************

trail_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
grenade_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()
water_group = pygame.sprite.Group()
diamond_group = pygame.sprite.Group()
potion_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()

objects_group = [water_group, diamond_group, potion_group, enemy_group, exit_group]
target_height = 0
image = pygame.image.load(f'Assets/Player2/Player2Idle1.png')
original_width, original_height = image.get_size()
scale_factor = target_height / original_height
new_width = int(original_width * scale_factor)
p_image = pygame.transform.scale(pygame.image.load('Assets/Player2/Player2Idle1.png'), (34, 38))
p_rect = p_image.get_rect(center=(470, 200))
p_dy = 1
p_ctr = 1

# CALCULATE THE COLLECTED_DIAMONDS *********************************************
collected_diamonds = 0
total_diamonds = 0

# LEVEL VARIABLES **************************************************************

ROWS = 24
COLS = 40
SCROLL_THRES = 200
MAX_LEVEL = 4

level = 1
level_length = 0
screen_scroll = 0
bg_scroll = 0
dx = 0


# RESET ***********************************************************************

def reset_level(level):
    trail_group.empty()
    bullet_group.empty()
    grenade_group.empty()
    explosion_group.empty()
    enemy_group.empty()
    water_group.empty()
    diamond_group.empty()
    potion_group.empty()
    exit_group.empty()

    # LOAD LEVEL WORLD

    world_data, level_length = load_level(level)
    w = World(objects_group)
    w.generate_world(world_data, win)

    return world_data, level_length, w


def reset_player():
    p = Player(250, 50)
    # p2 = Player2(255, 50)
    moving_left = False
    moving_right = False

    return p, moving_left, moving_right


# WINNING PAGE *******************************************************************
alpha = 0
message_display_time = 5000
start_display_time = None

# MAIN GAME *******************************************************************

main_menu = True
level_page = False
about_page = False
controls_page = False
exit_page = False
game_start = False
game_start2 = False
game_won = True
running = True

while running:
    win.fill((0, 0, 0))
    for x in range(5):
        win.blit(BG5, ((x * WIDTH) - bg_scroll * 0.6, 0))
        win.blit(BG2, ((x * WIDTH) - bg_scroll * 0.7, 0))
        win.blit(BG3, ((x * WIDTH) - bg_scroll * 0.8, 0))

    if not game_start or level_page:
        win.blit(MOON, (-40, 150))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                moving_left = True
            if event.key == pygame.K_d:
                moving_right = True
            if event.key == pygame.K_w:
                if not p.jump2:
                    p.jump = False
                    p.jump2 = True
                    jump_fx.play()
            if event.key == pygame.K_s:
                p.defense = True

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE or \
                    event.key == pygame.K_q:
                running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                moving_left = True
            if event.key == pygame.K_RIGHT:
                moving_right = True
            if event.key == pygame.K_UP:
                if not p.jump:
                    p.jump2 = False
                    p.jump = True
                    jump_fx.play()
            if event.key == pygame.K_SPACE:
                x, y = p.rect.center
                direction = p.direction
                bullet = Bullet(x, y, direction, (240, 240, 240), 1, win)
                bullet_group.add(bullet)
                bullet_fx.play()

                p.attack = True
            if event.key == pygame.K_g:
                if p.grenades:
                    p.grenades -= 1
                    grenade = Grenade(p.rect.centerx, p.rect.centery, p.direction, win)
                    grenade_group.add(grenade)
                    grenade_throw_fx.play()

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT:
                moving_left = False
            if event.key == pygame.K_RIGHT:
                moving_right = False
            if event.key == pygame.K_a:
                moving_left = False
            if event.key == pygame.K_d:
                moving_right = False
            if event.key == pygame.K_s:
                p.defense = False
    if main_menu:
        GMB.update()
        trail_group.update()

        if play_btn.draw(win):
            menu_click_fx.play()
            world_data, level_length, w = reset_level(level)
            p, moving_left, moving_right = reset_player()

            game_start = True
            main_menu = False
            game_won = False

        if level_btn.draw(win):
            menu_click_fx.play()
            level_page = True
            main_menu = False

        if about_btn.draw(win):
            menu_click_fx.play()
            about_page = True
            main_menu = False

        if controls_btn.draw(win):
            menu_click_fx.play()
            controls_page = True
            main_menu = False

        if exit_btn.draw(win):
            menu_click_fx.play()
            running = False

    elif about_page:
        MessageBox(win, about_font, 'Introduction ', info)
        if main_menu_btn.draw(win):
            menu_click_fx.play()
            about_page = False
            main_menu = True
    elif level_page:
        selected_level = Level_Background(win)
        if selected_level == 'main_menu':
            level_page = False
            main_menu = True
        elif selected_level == 1:
            level_page = False
            main_menu = False
            game_won = False
            game_start = True
            world_data, level_length, w = reset_level(level)
            p, moving_left, moving_right = reset_player()

        elif selected_level == 2:
            level_page = False
            main_menu = False
            game_won = False
            game_start = True
            world_data, level_length, w = reset_level(2)
            p, moving_left, moving_right = reset_player()

        elif selected_level == 3:
            level_page = False
            main_menu = False
            game_won = False
            game_start = True
            world_data, level_length, w = reset_level(3)
            p, moving_left, moving_right = reset_player()

        elif selected_level == 4:
            level_page = False
            main_menu = False
            game_won = False
            game_start = True
            world_data, level_length, w = reset_level(4)
            p, moving_left, moving_right = reset_player()


    elif controls_page:
        left_key.update()
        right_key.update()
        up_key.update()
        space_key.update()
        g_key.update()
        w_key.update()

        if main_menu_btn.draw(win):
            menu_click_fx.play()
            controls_page = False
            main_menu = True

    elif exit_page:
        pass

    elif game_won:
        game_start = False
        if start_display_time is None:
            start_display_time = pygame.time.get_ticks()
        message = (f"You have got {total_diamonds} gems, you can take these gems with you! Thank you for playing the "
                   f"GEM MECH BATTLE")

        # Drawing Winning Screen ********************************************************
        # Calculating The Transparency Of Message
        time_passed = pygame.time.get_ticks() - start_display_time
        alpha = min(255, time_passed // 20)  # Gradually Increase Transparency Until 255
        win.fill((0, 0, 0))

        font = pygame.font.Font(None, 40)
        lines = message.split(" ")  # Split By Space First
        wrapped_lines = []
        line = ""
        for word in lines:
            test_line = f"{line} {word}".strip()
            # Test The Width Of This Line Of Text After Adding New Words
            width, height = font.size(test_line)
            if width <= WIDTH - 20:
                line = test_line
            else:
                wrapped_lines.append(line)  # Save Current Line
                line = word
        wrapped_lines.append(line)  # Append Last Line
        line_spaceing = 10
        total_height = len(wrapped_lines) * height
        start_y = (HEIGHT - total_height) // 2
        for i, line in enumerate(wrapped_lines):
            text_surface = font.render(line, True, (255, 255, 255))
            text_surface.set_alpha(alpha)  # Set Transparency for text
            text_rect = text_surface.get_rect(center=(WIDTH // 2, start_y + i * (height + line_spaceing)))
            win.blit(text_surface, text_rect)

        # Return To The Main Page
        if time_passed > message_display_time + 2000:
            if main_menu_btn.draw(win):
                menu_click_fx.play()
                controls_page = False
                main_menu = True
                level = 1


    elif game_start:
        win.blit(MOON, (-40, -10))
        w.draw_world(win, screen_scroll)
        # Calculating Diamonds ********************************************************
        diamonds_text = counter_font.render(f"Diamonds: {collected_diamonds}/{w.get_total_diamonds()}", True,
                                            (255, 255, 255))
        screen.blit(diamonds_text, (WIDTH - diamonds_text.get_width() - 10, 10))
        # Updating Objects ********************************************************

        bullet_group.update(screen_scroll, w)
        grenade_group.update(screen_scroll, p, enemy_group, explosion_group, w)
        explosion_group.update(screen_scroll)
        trail_group.update()
        water_group.update(screen_scroll)
        water_group.draw(win)
        diamond_group.update(screen_scroll)
        diamond_group.draw(win)
        potion_group.update(screen_scroll)
        potion_group.draw(win)
        exit_group.update(screen_scroll)
        exit_group.draw(win)

        enemy_group.update(screen_scroll, bullet_group, p)
        enemy_group.draw(win)

        if p.jump:
            t = Trail(p.rect.center, (220, 220, 220), win)
            trail_group.add(t)
        if p.jump2:
            t2 = Trail(p.rect.center, (220, 220, 220), win)
            trail_group.add(t2)

        screen_scroll = 0
        p.update(moving_left, moving_right, w)
        p.draw(win)

        if (p.rect.right >= WIDTH - SCROLL_THRES and bg_scroll < (level_length * TILE_SIZE) - WIDTH) \
                or (p.rect.left <= SCROLL_THRES and bg_scroll > abs(dx)):
            dx = p.dx
            p.rect.x -= dx
            screen_scroll = -dx
            bg_scroll -= screen_scroll

        # Collision Detetction ****************************************************

        if p.rect.bottom > HEIGHT:
            p.health = 0

        if pygame.sprite.spritecollide(p, water_group, False):
            p.health = 0
            level = 1

        if pygame.sprite.spritecollide(p, diamond_group, True):
            diamond_fx.play()
            collected_diamonds += 1
            pass

        if pygame.sprite.spritecollide(p, exit_group, False):
            if collected_diamonds == w.get_total_diamonds() or collected_diamonds > w.get_total_diamonds():
                total_diamonds += collected_diamonds
                collected_diamonds = 0
                next_level_fx.play()
                level += 1

            else:
                print("You haven't collected enough diamonds!")
            if level <= MAX_LEVEL:
                health = p.health

                world_data, level_length, w = reset_level(level)
                p, moving_left, moving_right = reset_player()

                p.health = health

                screen_scroll = 0
                bg_scroll = 0
            else:

                game_won = True

        potion = pygame.sprite.spritecollide(p, potion_group, False)
        if potion:
            if p.health < 100:
                potion[0].kill()
                p.health += 15
                health_fx.play()
                if p.health > 100:
                    p.health = 100

        for bullet in bullet_group:
            enemy = pygame.sprite.spritecollide(bullet, enemy_group, False)
            if enemy and bullet.type == 1:
                if not enemy[0].hit:
                    enemy[0].hit = True
                    enemy[0].health -= 50
                bullet.kill()
            if bullet.rect.colliderect(p):
                if bullet.type == 2:
                    if p.defense and p.defense_count > 0:
                        p.defense_count -= 1
                    elif p.defense and p.defense_count <= 0:
                        if not p.hit:
                            p.hit = True
                            p.health -= 20
                            print(p.health)
                    else:
                        if not p.hit:
                            p.hit = True
                            p.health -= 20
                            print(p.health)
                    bullet.kill()

        # drawing variables *******************************************************
        if p.alive:
            color = (0, 255, 0)
            if p.health <= 40:
                color = (255, 0, 0)
            pygame.draw.rect(win, color, (6, 8, p.health, 20), border_radius=10)
        pygame.draw.rect(win, (255, 255, 255), (6, 8, 100, 20), 2, border_radius=10)

        for i in range(p.grenades):
            pygame.draw.circle(win, (200, 200, 200), (20 + 15 * i, 40), 5)
            pygame.draw.circle(win, (255, 50, 50), (20 + 15 * i, 40), 4)
            pygame.draw.circle(win, (0, 0, 0), (20 + 15 * i, 40), 1)

        if p.health <= 0:
            world_data, level_length, w = reset_level(level)
            p, moving_left, moving_right = reset_player()

            screen_scroll = 0
            bg_scroll = 0

            main_menu = True
            about_page = False
            controls_page = False
            game_start = False




    pygame.draw.rect(win, (255, 255, 255), (0, 0, WIDTH, HEIGHT), 4, border_radius=10)
    clock.tick(FPS)
    pygame.display.update()

pygame.quit()
