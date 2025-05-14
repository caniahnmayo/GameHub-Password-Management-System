import random
import pygame

font_button = 'super-larky-font/SuperLarky-nALLR.ttf'
font_title = 'snake-holiday-font/SnakeHoliday-vmYXD.otf'

def show_score(color, score, game_window):
    score_font = pygame.font.Font(font_button, 20)
    score_surface = score_font.render("Score : " + str(score), True, color)
    score_rect = score_surface.get_rect(topleft=(10, 10))
    game_window.blit(score_surface, score_rect)

def game_over(score, color, x, y, game_window):
    black = pygame.Color(0, 0, 0)

    game_window.fill(black)

    my_font = pygame.font.Font(font_title, 50)
    game_over_surface = my_font.render("Game Over! Your score: " + str(score), True, color)
    game_over_rect = game_over_surface.get_rect(center=(x // 2, y // 3))
    game_window.blit(game_over_surface, game_over_rect)

    button_font = pygame.font.Font(font_button, 30)
    play_button_surface = button_font.render("Play Again", True, black)
    play_button_rect = pygame.Rect((x // 2) - 125, (y // 2), 250, 50)
    pygame.draw.rect(game_window, (0, 255, 0), play_button_rect)
    game_window.blit(play_button_surface, play_button_surface.get_rect(center=play_button_rect.center))

    quit_button_surface = button_font.render("Quit", True, black)
    quit_button_rect = pygame.Rect((x // 2) - 125, (y // 2) + 70, 250, 50)
    pygame.draw.rect(game_window, (255, 0, 0), quit_button_rect)
    game_window.blit(quit_button_surface, quit_button_surface.get_rect(center=quit_button_rect.center))

    pygame.display.flip()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if play_button_rect.collidepoint(event.pos):
                    return "play_again"
                if quit_button_rect.collidepoint(event.pos):
                    return "quit"

def snake_game():
    window_x = 720
    window_y = 480

    black = pygame.Color(0, 0, 0)
    white = pygame.Color(255, 255, 255)
    green = pygame.Color(0, 255, 0)
    blue = pygame.Color(0, 0, 255)

    pygame.init()
    pygame.display.set_caption("VIPER")
    game_window = pygame.display.set_mode((window_x, window_y))
    fps = pygame.time.Clock()

    while True:
        # Initialize game state
        viper_position = [100, 50]
        viper_speed = 15
        viper_body = [[100, 50], [90, 50], [80, 50]]
        fruit_position = [random.randrange(1, (window_x // 10)) * 10, random.randrange(1, (window_y // 10)) * 10]
        fruit_spawn = True
        direction = 'RIGHT'
        change_to = direction
        score = 0

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP and direction != 'DOWN':
                        change_to = 'UP'
                    if event.key == pygame.K_DOWN and direction != 'UP':
                        change_to = 'DOWN'
                    if event.key == pygame.K_LEFT and direction != 'RIGHT':
                        change_to = 'LEFT'
                    if event.key == pygame.K_RIGHT and direction != 'LEFT':
                        change_to = 'RIGHT'

            direction = change_to

            if direction == 'UP':
                viper_position[1] -= 10
            if direction == 'DOWN':
                viper_position[1] += 10
            if direction == 'LEFT':
                viper_position[0] -= 10
            if direction == 'RIGHT':
                viper_position[0] += 10

            viper_body.insert(0, list(viper_position))
            if viper_position[0] == fruit_position[0] and viper_position[1] == fruit_position[1]:
                score += 10
                viper_speed += 1
                fruit_spawn = False
            else:
                viper_body.pop()

            if not fruit_spawn:
                fruit_position = [random.randrange(1, (window_x // 10)) * 10, random.randrange(1, (window_y // 10)) * 10]
                fruit_spawn = True

            game_window.fill(black)

            for pos in viper_body:
                pygame.draw.rect(game_window, blue, pygame.Rect(pos[0], pos[1], 10, 10))

            pygame.draw.rect(game_window, green, pygame.Rect(fruit_position[0], fruit_position[1], 10, 10))

            if viper_position[0] < 0 or viper_position[0] >= window_x or viper_position[1] < 0 or viper_position[1] >= window_y:
                result = game_over(score, white, window_x, window_y, game_window)
                if result == "play_again":
                    break
                elif result == "quit":
                    pygame.quit()

            for block in viper_body[1:]:
                if viper_position[0] == block[0] and viper_position[1] == block[1]:
                    result = game_over(score, white, window_x, window_y, game_window)
                    if result == "play_again":
                        break
                    elif result == "quit":
                        pygame.quit()

            show_score(white, score, game_window)

            pygame.display.update()
            fps.tick(viper_speed)
