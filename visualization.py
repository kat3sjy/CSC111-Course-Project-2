# Example file showing a basic pygame "game loop"
import pygame

# pygame setup
pygame.init()
screen = pygame.display.set_mode()
current = "home"
window_y = screen.get_height()
window_x = screen.get_width()
title_x = 750
title_y = 150
clock = pygame.time.Clock()
running = True
user_input_active = False
user_input_text = ''
question_index = 0
question_list = ["Question 1", "Question 2", "Question 3"]

# different fonts
TITLE_FONT = pygame.font.Font("Fonts/Audiowide/Audiowide-Regular.ttf", 90)
SUBTITLE_FONT = pygame.font.Font("Fonts/Audiowide/Audiowide-Regular.ttf", 60)
PARAGRAPH_FONT = pygame.font.Font("Fonts/Audiowide/Audiowide-Regular.ttf", 25)

while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window

    mouse = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if start_button.collidepoint(event.pos) and current == "home":
                current = "recommender"
            elif user_input.collidepoint(event.pos) and current == "recommender":
                user_input_active = True
            elif input_enter.collidepoint(event.pos) and current == "recommender":
                user_input_text = ""
                if question_index < len(question_list) - 1:
                    question_index += 1
                else:
                    current = "recommendations"

        elif event.type == pygame.KEYDOWN:
                if user_input_active:
                    if event.key == pygame.K_BACKSPACE:
                        user_input_text = user_input_text[:-1]
                    else:
                        user_input_text += event.unicode

    # fill the screen with a color to wipe away anything from last frame
    screen.fill("black")

    if current == "home":
        # title stuff
        title = TITLE_FONT.render("Spotify Recommender System", True, (255, 255, 255))
        screen.blit(title, (window_x // 2 - title_x, window_y // 2 - title_y))
        start_button = pygame.draw.rect(screen, (44, 201, 76), (window_x // 2 - title_x/3, window_y // 2, 500, 100), 0)
        start_button_text = SUBTITLE_FONT.render("START", True, (255,255,255))
        screen.blit(start_button_text, (window_x // 2 - title_x/6, window_y // 2 +title_y/13))

    elif current == "recommender":

        question_text = SUBTITLE_FONT.render(question_list[question_index], True, (255,255,255))
        screen.blit(question_text, (window_x // 2 - title_x/6, 200))

        user_input = pygame.draw.rect(screen, (44, 201, 76), (window_x // 2 - title_x/3, window_y // 2, 500, 100), 0)
        input_text = PARAGRAPH_FONT.render(user_input_text, True, (255,255,255))
        screen.blit(input_text, (window_x // 2 - title_x/6, window_y // 2 +title_y/13))

        input_enter = pygame.draw.rect(screen, (255,255,255), (window_x // 2 - title_x/3, window_y // 2 + 200, 500, 100), 0)
        enter_text = SUBTITLE_FONT.render("ENTER", True, (0,0,0))
        screen.blit(enter_text, (window_x // 2 - title_x/6, window_y // 2 +title_y/13+200))

    elif current == "recommendations":
        question_text = SUBTITLE_FONT.render("insert random recs", True, (255, 255, 255))
        screen.blit(question_text, (window_x // 2 - title_x / 6, 200))


    # flip() the display to put your work on screen
    pygame.display.flip()

    clock.tick(60)  # limits FPS to 60

pygame.quit()
