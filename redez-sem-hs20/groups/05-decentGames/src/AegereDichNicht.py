import pygame
import random

pygame.font.init()

screen = pygame.display.set_mode([900, 900])
pygame.display.set_caption('Mensch Ärgere Dich Nicht!')
myfont = pygame.font.SysFont('Georgia', 30)
diceimage = pygame.image.load("../res/dice.bmp")
dice = screen.blit(diceimage, (550, 750))

textmensch = myfont.render('Mensch', True, (0, 0, 0))
textaergere = myfont.render('Ärgere', True, (0, 0, 0))
textdich = myfont.render('Dich', True, (0, 0, 0))
textnicht = myfont.render('Nicht!', True, (0, 0, 0))

myfont = pygame.font.SysFont('Georgia', 30)
playeryellow = myfont.render('X', True, (255, 234, 3))
playergreen = myfont.render('X', True, (3, 148, 61))
playerblack = myfont.render('X', True, (24, 24, 22))
playerred = myfont.render('X', True, (225, 2, 15))


def setup():
    pygame.init()

    screen.fill((253, 235, 149))

    screen.blit(textmensch, (150, 280))
    screen.blit(textaergere, (620, 280))
    screen.blit(textdich, (150, 620))
    screen.blit(textnicht, (620, 620))
    dice = screen.blit(diceimage, (550, 750))

    # red border
    pygame.draw.rect(screen, (225, 2, 15), (0, 0, 900, 900), 20)

    # yellow top left group
    pygame.draw.circle(screen, (255, 234, 3), (50, 50), 20)
    pygame.draw.circle(screen, (0, 0, 0), (50, 50), 20, 1)
    pygame.draw.circle(screen, (255, 234, 3), (150, 50), 20)
    pygame.draw.circle(screen, (0, 0, 0), (150, 50), 20, 1)
    pygame.draw.circle(screen, (255, 234, 3), (50, 150), 20)
    pygame.draw.circle(screen, (0, 0, 0), (50, 150), 20, 1)
    pygame.draw.circle(screen, (255, 234, 3), (150, 150), 20)
    pygame.draw.circle(screen, (0, 0, 0), (150, 150), 20, 1)

    # final yellow slots
    pygame.draw.circle(screen, (255, 234, 3), (200, 450), 20)
    pygame.draw.circle(screen, (0, 0, 0), (200, 450), 20, 1)
    pygame.draw.circle(screen, (255, 234, 3), (250, 450), 20)
    pygame.draw.circle(screen, (0, 0, 0), (250, 450), 20, 1)
    pygame.draw.circle(screen, (255, 234, 3), (300, 450), 20)
    pygame.draw.circle(screen, (0, 0, 0), (300, 450), 20, 1)
    pygame.draw.circle(screen, (255, 234, 3), (350, 450), 20)
    pygame.draw.circle(screen, (0, 0, 0), (350, 450), 20, 1)

    # green top right group
    pygame.draw.circle(screen, (3, 148, 61), (750, 50), 20)
    pygame.draw.circle(screen, (0, 0, 0), (750, 50), 20, 1)
    pygame.draw.circle(screen, (3, 148, 61), (850, 50), 20)
    pygame.draw.circle(screen, (0, 0, 0), (850, 50), 20, 1)
    pygame.draw.circle(screen, (3, 148, 61), (750, 150), 20)
    pygame.draw.circle(screen, (0, 0, 0), (750, 150), 20, 1)
    pygame.draw.circle(screen, (3, 148, 61), (850, 150), 20)
    pygame.draw.circle(screen, (0, 0, 0), (850, 150), 20, 1)

    # final green slots
    pygame.draw.circle(screen, (3, 148, 61), (450, 200), 20)
    pygame.draw.circle(screen, (0, 0, 0), (450, 200), 20, 1)
    pygame.draw.circle(screen, (3, 148, 61), (450, 250), 20)
    pygame.draw.circle(screen, (0, 0, 0), (450, 250), 20, 1)
    pygame.draw.circle(screen, (3, 148, 61), (450, 300), 20)
    pygame.draw.circle(screen, (0, 0, 0), (450, 300), 20, 1)
    pygame.draw.circle(screen, (3, 148, 61), (450, 350), 20)
    pygame.draw.circle(screen, (0, 0, 0), (450, 350), 20, 1)

    # black bottom left group
    pygame.draw.circle(screen, (24, 24, 22), (50, 750), 20)
    pygame.draw.circle(screen, (0, 0, 0), (50, 750), 20, 1)
    pygame.draw.circle(screen, (24, 24, 22), (50, 850), 20)
    pygame.draw.circle(screen, (0, 0, 0), (50, 850), 20, 1)
    pygame.draw.circle(screen, (24, 24, 22), (150, 750), 20)
    pygame.draw.circle(screen, (0, 0, 0), (150, 750), 20, 1)
    pygame.draw.circle(screen, (24, 24, 22), (150, 850), 20)
    pygame.draw.circle(screen, (0, 0, 0), (150, 850), 20, 1)

    # final black slots
    pygame.draw.circle(screen, (24, 24, 22), (450, 550), 20)
    pygame.draw.circle(screen, (0, 0, 0), (450, 550), 20, 1)
    pygame.draw.circle(screen, (24, 24, 22), (450, 600), 20)
    pygame.draw.circle(screen, (0, 0, 0), (450, 600), 20, 1)
    pygame.draw.circle(screen, (24, 24, 22), (450, 650), 20)
    pygame.draw.circle(screen, (0, 0, 0), (450, 650), 20, 1)
    pygame.draw.circle(screen, (24, 24, 22), (450, 700), 20)
    pygame.draw.circle(screen, (0, 0, 0), (450, 700), 20, 1)

    # red bottom right group
    pygame.draw.circle(screen, (225, 2, 15), (750, 750), 20)
    pygame.draw.circle(screen, (0, 0, 0), (750, 750), 20, 1)
    pygame.draw.circle(screen, (225, 2, 15), (850, 750), 20)
    pygame.draw.circle(screen, (0, 0, 0), (850, 750), 20, 1)
    pygame.draw.circle(screen, (225, 2, 15), (750, 850), 20)
    pygame.draw.circle(screen, (0, 0, 0), (750, 850), 20, 1)
    pygame.draw.circle(screen, (225, 2, 15), (850, 850), 20)
    pygame.draw.circle(screen, (0, 0, 0), (850, 850), 20, 1)

    # final red slots
    pygame.draw.circle(screen, (225, 2, 15), (550, 450), 20)
    pygame.draw.circle(screen, (0, 0, 0), (550, 450), 20, 1)
    pygame.draw.circle(screen, (225, 2, 15), (600, 450), 20)
    pygame.draw.circle(screen, (0, 0, 0), (600, 450), 20, 1)
    pygame.draw.circle(screen, (225, 2, 15), (650, 450), 20)
    pygame.draw.circle(screen, (0, 0, 0), (650, 450), 20, 1)
    pygame.draw.circle(screen, (225, 2, 15), (700, 450), 20)
    pygame.draw.circle(screen, (0, 0, 0), (700, 450), 20, 1)

    # lines
    pygame.draw.line(screen, (24, 24, 22), ([70, 390]), ([390, 390]), 1)
    pygame.draw.line(screen, (24, 24, 22), ([390, 390]), ([390, 70]), 1)
    pygame.draw.line(screen, (24, 24, 22), ([510, 70]), ([510, 390]), 1)
    pygame.draw.line(screen, (24, 24, 22), ([510, 390]), ([830, 390]), 1)
    pygame.draw.line(screen, (24, 24, 22), ([830, 510]), ([510, 510]), 1)
    pygame.draw.line(screen, (24, 24, 22), ([510, 510]), ([510, 830]), 1)
    pygame.draw.line(screen, (24, 24, 22), ([390, 830]), ([390, 510]), 1)
    pygame.draw.line(screen, (24, 24, 22), ([390, 510]), ([70, 510]), 1)

    # connecting lines
    pygame.draw.line(screen, (24, 24, 22), ([70, 390]), ([70, 510]), 1)
    pygame.draw.line(screen, (24, 24, 22), ([390, 70]), ([510, 70]), 1)
    pygame.draw.line(screen, (24, 24, 22), ([830, 390]), ([830, 510]), 1)
    pygame.draw.line(screen, (24, 24, 22), ([390, 830]), ([510, 830]), 1)

    # playing tiles, start 9 o'clock going clockwise
    pygame.draw.circle(screen, (255, 234, 3), (70, 390), 25)  # yellow
    pygame.draw.circle(screen, (24, 24, 22), (70, 390), 25, 1)
    pygame.draw.circle(screen, (255, 255, 255), (150, 390), 25)
    pygame.draw.circle(screen, (24, 24, 22), (150, 390), 25, 1)
    pygame.draw.circle(screen, (255, 255, 255), (230, 390), 25)
    pygame.draw.circle(screen, (24, 24, 22), (230, 390), 25, 1)
    pygame.draw.circle(screen, (255, 255, 255), (310, 390), 25)
    pygame.draw.circle(screen, (24, 24, 22), (310, 390), 25, 1)
    pygame.draw.circle(screen, (255, 255, 255), (390, 390), 25)
    pygame.draw.circle(screen, (24, 24, 22), (390, 390), 25, 1)

    # pygame.draw.circle(screen, (255, 255, 255), (390, 390), 25)
    # pygame.draw.circle(screen, (24, 24, 22), (390, 390), 25, 1)
    pygame.draw.circle(screen, (255, 255, 255), (390, 310), 25)
    pygame.draw.circle(screen, (24, 24, 22), (390, 310), 25, 1)
    pygame.draw.circle(screen, (255, 255, 255), (390, 230), 25)
    pygame.draw.circle(screen, (24, 24, 22), (390, 230), 25, 1)
    pygame.draw.circle(screen, (255, 255, 255), (390, 150), 25)
    pygame.draw.circle(screen, (24, 24, 22), (390, 150), 25, 1)
    pygame.draw.circle(screen, (255, 255, 255), (390, 70), 25)
    pygame.draw.circle(screen, (24, 24, 22), (390, 70), 25, 1)

    pygame.draw.circle(screen, (255, 255, 255), (510, 390), 25)
    pygame.draw.circle(screen, (24, 24, 22), (510, 390), 25, 1)
    pygame.draw.circle(screen, (255, 255, 255), (590, 390), 25)
    pygame.draw.circle(screen, (24, 24, 22), (590, 390), 25, 1)
    pygame.draw.circle(screen, (255, 255, 255), (670, 390), 25)
    pygame.draw.circle(screen, (24, 24, 22), (670, 390), 25, 1)
    pygame.draw.circle(screen, (255, 255, 255), (750, 390), 25)
    pygame.draw.circle(screen, (24, 24, 22), (750, 390), 25, 1)
    pygame.draw.circle(screen, (255, 255, 255), (830, 390), 25)
    pygame.draw.circle(screen, (24, 24, 22), (830, 390), 25, 1)

    # pygame.draw.circle(screen, (255, 255, 255), (510, 390), 25)
    # pygame.draw.circle(screen, (24, 24, 22), (510, 390), 25, 1)
    pygame.draw.circle(screen, (255, 255, 255), (510, 310), 25)
    pygame.draw.circle(screen, (24, 24, 22), (510, 310), 25, 1)
    pygame.draw.circle(screen, (255, 255, 255), (510, 230), 25)
    pygame.draw.circle(screen, (24, 24, 22), (510, 230), 25, 1)
    pygame.draw.circle(screen, (255, 255, 255), (510, 150), 25)
    pygame.draw.circle(screen, (24, 24, 22), (510, 150), 25, 1)
    pygame.draw.circle(screen, (3, 148, 61), (510, 70), 25)  # green
    pygame.draw.circle(screen, (24, 24, 22), (510, 70), 25, 1)

    pygame.draw.circle(screen, (255, 255, 255), (70, 510), 25)
    pygame.draw.circle(screen, (24, 24, 22), (70, 510), 25, 1)
    pygame.draw.circle(screen, (255, 255, 255), (150, 510), 25)
    pygame.draw.circle(screen, (24, 24, 22), (150, 510), 25, 1)
    pygame.draw.circle(screen, (255, 255, 255), (230, 510), 25)
    pygame.draw.circle(screen, (24, 24, 22), (230, 510), 25, 1)
    pygame.draw.circle(screen, (255, 255, 255), (310, 510), 25)
    pygame.draw.circle(screen, (24, 24, 22), (310, 510), 25, 1)
    pygame.draw.circle(screen, (255, 255, 255), (390, 510), 25)
    pygame.draw.circle(screen, (24, 24, 22), (390, 510), 25, 1)

    pygame.draw.circle(screen, (255, 255, 255), (510, 510), 25)
    pygame.draw.circle(screen, (24, 24, 22), (510, 510), 25, 1)
    pygame.draw.circle(screen, (255, 255, 255), (590, 510), 25)
    pygame.draw.circle(screen, (24, 24, 22), (590, 510), 25, 1)
    pygame.draw.circle(screen, (255, 255, 255), (670, 510), 25)
    pygame.draw.circle(screen, (24, 24, 22), (670, 510), 25, 1)
    pygame.draw.circle(screen, (255, 255, 255), (750, 510), 25)
    pygame.draw.circle(screen, (24, 24, 22), (750, 510), 25, 1)
    pygame.draw.circle(screen, (225, 2, 15), (830, 510), 25)  # red
    pygame.draw.circle(screen, (24, 24, 22), (830, 510), 25, 1)

    # pygame.draw.circle(screen, (255, 255, 255), (510, 510), 25)
    # pygame.draw.circle(screen, (24, 24, 22), (510, 510), 25, 1)
    pygame.draw.circle(screen, (255, 255, 255), (510, 590), 25)
    pygame.draw.circle(screen, (24, 24, 22), (510, 590), 25, 1)
    pygame.draw.circle(screen, (255, 255, 255), (510, 670), 25)
    pygame.draw.circle(screen, (24, 24, 22), (510, 670), 25, 1)
    pygame.draw.circle(screen, (255, 255, 255), (510, 750), 25)
    pygame.draw.circle(screen, (24, 24, 22), (510, 750), 25, 1)
    pygame.draw.circle(screen, (255, 255, 255), (510, 830), 25)
    pygame.draw.circle(screen, (24, 24, 22), (510, 830), 25, 1)

    # pygame.draw.circle(screen, (255, 255, 255), (390, 510), 25)
    # pygame.draw.circle(screen, (24, 24, 22), (390, 510), 25, 1)
    pygame.draw.circle(screen, (255, 255, 255), (390, 590), 25)
    pygame.draw.circle(screen, (24, 24, 22), (390, 590), 25, 1)
    pygame.draw.circle(screen, (255, 255, 255), (390, 670), 25)
    pygame.draw.circle(screen, (24, 24, 22), (390, 670), 25, 1)
    pygame.draw.circle(screen, (255, 255, 255), (390, 750), 25)
    pygame.draw.circle(screen, (24, 24, 22), (390, 750), 25, 1)
    pygame.draw.circle(screen, (24, 24, 22), (390, 830), 25)  # black
    pygame.draw.circle(screen, (24, 24, 22), (390, 830), 25, 1)

    # connecting points
    pygame.draw.circle(screen, (255, 255, 255), (450, 70), 25)
    pygame.draw.circle(screen, (24, 24, 22), (450, 70), 25, 1)
    pygame.draw.circle(screen, (255, 255, 255), (830, 450), 25)
    pygame.draw.circle(screen, (24, 24, 22), (830, 450), 25, 1)
    pygame.draw.circle(screen, (255, 255, 255), (450, 830), 25)
    pygame.draw.circle(screen, (24, 24, 22), (450, 830), 25, 1)
    pygame.draw.circle(screen, (255, 255, 255), (70, 450), 25)
    pygame.draw.circle(screen, (24, 24, 22), (70, 450), 25, 1)

    pygame.display.flip()


def gameloop(screen):
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        if pygame.mouse.get_pressed()[0] and dice.collidepoint(pygame.mouse.get_pos()):
            moveplayer(screen, 'yellow')
        pygame.display.flip()
    # pygame.quit()


def throwdice():
    dice = random.choice([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12])
    return dice


def moveplayer(screen, player):
    if player == 'yellow':
        screen.blit(playeryellow, (150, 390))


def correctposition(colour, number):
    if colour == 'yellow':
        if number == 1:
            return (70, 390)
        if number == 2:
            return '(150, 390)'
        if number == 3:
            return '(230, 390)'
        if number == 4:
            return '(310, 390)'
        if number == 5:
            return '(390, 390)'
        if number == 6:
            return '(390, 310)'
        if number == 7:
            return '(390, 230)'
        if number == 8:
            return '(390, 150)'
        if number == 9:
            return '(390, 70)'
        if number == 10:
            return '(450, 70)'
        if number == 11:
            return '(510, 70)'
        if number == 12:
            return '(510, 150)'
        if number == 13:
            return '(0, 0)'
        if number == 14:
            return '(0, 0)'
        if number == 15:
            return '(0, 0)'
        if number == 16:
            return '(0, 0)'
        if number == 17:
            return '(0, 0)'
        if number == 18:
            return '(0, 0)'
        if number == 19:
            return '(0, 0)'
        if number == 20:
            return '(0, 0)'
        if number == 21:
            return '(0, 0)'
        if number == 22:
            return '(0, 0)'
        if number == 23:
            return '(0, 0)'
        if number == 24:
            return '(0, 0)'
        if number == 25:
            return '(0, 0)'
        if number == 26:
            return '(0, 0)'
        if number == 27:
            return '(0, 0)'
        if number == 28:
            return '(0, 0)'
        if number == 29:
            return '(0, 0)'
        if number == 30:
            return '(0, 0)'
        if number == 31:
            return '(0, 0)'
        if number == 32:
            return '(0, 0)'
        if number == 33:
            return '(0, 0)'
        if number == 341:
            return '(0, 0)'
        if number == 35:
            return '(0, 0)'
        if number == 36:
            return '(0, 0)'
        if number == 37:
            return '(0, 0)'
        if number == 38:
            return '(0, 0)'
        if number == 39:
            return '(0, 0)'
        if number == 40:
            return '(0, 0)'
    elif colour == 'green':
        return (0, 0)
    elif colour == 'red':
        return (0, 0)
    elif colour == 'black':
        return (0, 0)


if __name__ == '__main__':
    setup()
    gameloop(screen)