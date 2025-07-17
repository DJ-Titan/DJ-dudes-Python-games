import pygame
#start pygame
pygame.init()
running=True
screen = pygame.display.set_mode((500, 500))

while running:
    
    # Press a key to exit the game loop
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:  # Press Escape to exit
                running = False

    screen.fill((0, 255, 0)) # set the background color to green


    pygame.display.flip()
pygame.quit()