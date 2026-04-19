import pygame
import random

from wcwidth import center

# khoi tao
pygame.init()

game_font = pygame.font.SysFont('Arial', 40)

# cau hinh man hinh
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()

# tai hinh anh
bird_surface = pygame.image.load('static/uploads/flappy-bird.png').convert_alpha()
bird_surface = pygame.transform.scale(bird_surface, (40, 30))

pipe_surface = pygame.image.load('static/uploads/pipe.jpg').convert_alpha()
pipe_surface = pygame.transform.scale(pipe_surface, (50, 500))
# bien so game
gravity = 0.25
bird_movement = 0
game_active = True
score = 0
hight_score = 0
can_score = True
# tao nhan vat chim
bird_rect = pygame.Rect(50, 300, 30, 30)

# tao ong cong
pipe_list = []
SPAWPIPE = pygame.USEREVENT
pygame.time.set_timer(SPAWPIPE, 1200)
pipe_height = [300, 400, 500]


def draw_bird():
    rotated_bird = pygame.transform.rotozoom(bird_surface, -bird_movement * 3, 1)
    screen.blit(rotated_bird, bird_rect)


def create_pipe():
    random_pips_pos = random.choice(pipe_height)
    bottom_pips = pygame.Rect(400, random_pips_pos, 50, 600)
    top_pipe = pygame.Rect(400, random_pips_pos - 750, 50, 600)
    return bottom_pips, top_pipe


def move_pipes(pipes):
    for pipe in pipes:
        pipe.centerx -= 3
    return [pipe for pipe in pipes if pipe.right > 0]


def draw_pipes(pipes):
    for pipe in pipes:
        pygame.draw.rect(screen, (0, 200, 0), pipe)


def check_collision(pipes):
    for pipe in pipes:
        if bird_rect.colliderect(pipe):
            return False
    if bird_rect.top <= -50 or bird_rect.bottom >= 600:
        return False
    return True


def display_score(status):
    if status == 'playing':
        score_surface = game_font.render(f'Score: {int(score)}', True, (255, 255, 255))
        score_rect = score_surface.get_rect(center=(200, 50))
        screen.blit(score_surface, score_rect)

    if status == 'game_over':
        #         hien thi diem hien tai
        score_surface = game_font.render(f'Score: {int(score)}', True, (255, 255, 255))
        score_rect = score_surface.get_rect(center=(200, 50))
        screen.blit(score_surface, score_rect)

        #         hien thi hight score
        hight_score_surface = game_font.render(f'Hight Score: {int(hight_score)}', True, (255, 255, 255))
        hight_score_rect = hight_score_surface.get_rect(center=(200, 500))
        screen.blit(hight_score_surface, hight_score_rect)

        msg_surface = game_font.render('Press SPACE to Start', True, (255, 255, 255))
        msg_rect = msg_surface.get_rect(center=(200, 300))
        screen.blit(msg_surface, msg_rect)


# vong lap chinh
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and game_active:
                bird_movement = 0
                bird_movement -= 6
            if event.key == pygame.K_SPACE and not game_active:
                game_active = True
                pipe_list.clear()
                bird_rect.center = (50, 300)
                bird_movement = 0
                score = 0
        if event.type == SPAWPIPE:
            pipe_list.extend(create_pipe())
    screen.fill((135, 206, 235))
    if game_active:
        # logic chim
        bird_movement += gravity
        bird_rect.centery += bird_movement
        draw_bird()
        # pygame.draw.ellipse(screen, (255, 200, 0), bird_rect)

        # logic ong
        pipe_list = move_pipes(pipe_list)
        draw_pipes(pipe_list)
        display_score('playing')
        # kiem tra va cham
        game_active = check_collision(pipe_list)
        score += 0.01
    else:
        if score > high_score:
            high_score = score
        display_score('game_over')

    pygame.display.update()
    clock.tick(60)
