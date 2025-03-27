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
TITLE_FONT = pygame.font.Font("Fonts/Audiowide/Audiowide-Regular.ttf", 90)
SUBTITLE_FONT = pygame.font.Font("Fonts/Audiowide/Audiowide-Regular.ttf", 60)

while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window

    mouse = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if window_x // 2 - title_x/3 <= mouse[0] <= window_x // 2 - title_x/3 + 500 and window_y // 2 <= mouse[1] <= window_y // 2 + 100:
                current = "recommender"

    # fill the screen with a color to wipe away anything from last frame
    screen.fill("black")

    if current == "home":
        # RENDER YOUR GAME HERE

        title = TITLE_FONT.render("Spotify Recommender System", True, (255, 255, 255))
        screen.blit(title, (window_x // 2 - title_x, window_y // 2 - title_y))
        start_button = pygame.draw.rect(screen, (44, 201, 76), (window_x // 2 - title_x/3, window_y // 2, 500, 100), 0)
        start_button_text = SUBTITLE_FONT.render("START", True, (255,255,255))
        screen.blit(start_button_text, (window_x // 2 - title_x/6, window_y // 2 +title_y/13))

    elif current == "recommender":
        idk_button = pygame.draw.rect(screen, (44, 201, 76), (window_x // 2 - title_x/3, window_y // 2, 500, 100), 0)


    # flip() the display to put your work on screen
    pygame.display.flip()

    clock.tick(60)  # limits FPS to 60

pygame.quit()
