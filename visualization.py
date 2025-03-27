
# Example file showing a basic pygame "game loop"
import pygame

# pygame setup
pygame.init()
screen = pygame.display.set_mode()
window = screen.get_rect()
clock = pygame.time.Clock()
running = True
TITLE_FONT = pygame.font.Font("Fonts/Audiowide/Audiowide-Regular.ttf", 50)

while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # fill the screen with a color to wipe away anything from last frame
    screen.fill("black")

    # RENDER YOUR GAME HERE
    title = TITLE_FONT.render("Spotify Recommender System", True, (255,255,255))
    screen.blit(title, window.center)

    # flip() the display to put your work on screen
    pygame.display.flip()

    clock.tick(60)  # limits FPS to 60

pygame.quit()


