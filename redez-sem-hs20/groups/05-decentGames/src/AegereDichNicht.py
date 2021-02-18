import pygame
import random
import time
import udp_connection
from logSync import database_sync
import sys
import os
import pickle
from logStore.appconn.chat_connection import ChatFunction
import feed_control

# determine absolute path of this folder
dirname = os.path.abspath(os.path.dirname(__file__))

# Import from group 04
folderG4 = os.path.join(dirname, '../../../../groups/04-logMerge/eventCreationTool')
sys.path.append(folderG4)
import EventCreationTool


pickle_file_names = ['personList.pkl', 'roles.pkl']

pygame.font.init()


class Player:
    def __init__(self, position, colour, colourstring):
        self.position = position
        self.colour = colour
        self.colourstring = colourstring
        self.moved = False


def correctposition(colour, number):
    if colour == colourYellow:
        if number == 0:  # start, impossible
            return 70, 390  # yellow
        if number == 1:
            return 150, 390
        if number == 2:
            return 230, 390
        if number == 3:
            return 310, 390
        if number == 4:
            return 390, 390
        if number == 5:
            return 390, 310
        if number == 6:
            return 390, 230
        if number == 7:
            return 390, 150
        if number == 8:
            return 390, 70
        if number == 9:
            return 450, 70
        if number == 10:
            return 510, 70  # green
        if number == 11:
            return 510, 150
        if number == 12:
            return 510, 230
        if number == 13:
            return 510, 310
        if number == 14:
            return 510, 390
        if number == 15:
            return 590, 390
        if number == 16:
            return 670, 390
        if number == 17:
            return 750, 390
        if number == 18:
            return 830, 390
        if number == 19:
            return 830, 450
        if number == 20:
            return 830, 510  # red
        if number == 21:
            return 750, 510
        if number == 22:
            return 670, 510
        if number == 23:
            return 590, 510
        if number == 24:
            return 510, 510
        if number == 25:
            return 510, 590
        if number == 26:
            return 510, 670
        if number == 27:
            return 510, 750
        if number == 28:
            return 510, 830
        if number == 29:
            return 450, 830
        if number == 30:
            return 390, 830  # black
        if number == 31:
            return 390, 750
        if number == 32:
            return 390, 670
        if number == 33:
            return 390, 590
        if number == 34:
            return 390, 510
        if number == 35:
            return 310, 510
        if number == 36:
            return 230, 510
        if number == 37:
            return 150, 510
        if number == 38:
            return 70, 510
        if number == 39:
            return 70, 450
        if number == 40:  # number 40 is finish
            return 350, 450
    elif colour == colourGreen:
        if number == 0:  # start, impossible
            return 510, 70  # green
        if number == 1:
            return 510, 150
        if number == 2:
            return 510, 230
        if number == 3:
            return 510, 310
        if number == 4:
            return 510, 390
        if number == 5:
            return 590, 390
        if number == 6:
            return 670, 390
        if number == 7:
            return 750, 390
        if number == 8:
            return 830, 390
        if number == 9:
            return 830, 450
        if number == 10:
            return 830, 510  # red
        if number == 11:
            return 750, 510
        if number == 12:
            return 670, 510
        if number == 13:
            return 590, 510
        if number == 14:
            return 510, 510
        if number == 15:
            return 510, 590
        if number == 16:
            return 510, 670
        if number == 17:
            return 510, 750
        if number == 18:
            return 510, 830
        if number == 19:
            return 450, 830
        if number == 20:
            return 390, 830  # black
        if number == 21:
            return 390, 750
        if number == 22:
            return 390, 670
        if number == 23:
            return 390, 590
        if number == 24:
            return 390, 510
        if number == 25:
            return 310, 510
        if number == 26:
            return 230, 510
        if number == 27:
            return 150, 510
        if number == 28:
            return 70, 510
        if number == 29:
            return 70, 450
        if number == 30:
            return 70, 390  # yellow
        if number == 31:
            return 150, 390
        if number == 32:
            return 230, 390
        if number == 33:
            return 310, 390
        if number == 34:
            return 390, 390
        if number == 35:
            return 390, 310
        if number == 36:
            return 390, 230
        if number == 37:
            return 390, 150
        if number == 38:
            return 390, 70
        if number == 39:
            return 450, 70
        if number == 40:  # number 40 is finish
            return 450, 350
    elif colour == colourRed:
        if number == 0:  # start, impossible
            return 830, 510  # red
        if number == 1:
            return 750, 510
        if number == 2:
            return 670, 510
        if number == 3:
            return 590, 510
        if number == 4:
            return 510, 510
        if number == 5:
            return 510, 590
        if number == 6:
            return 510, 670
        if number == 7:
            return 510, 750
        if number == 8:
            return 510, 830
        if number == 9:
            return 450, 830
        if number == 10:
            return 390, 830  # black
        if number == 11:
            return 390, 750
        if number == 12:
            return 390, 670
        if number == 13:
            return 390, 590
        if number == 14:
            return 390, 510
        if number == 15:
            return 310, 510
        if number == 16:
            return 230, 510
        if number == 17:
            return 150, 510
        if number == 18:
            return 70, 510
        if number == 19:
            return 70, 450
        if number == 20:
            return 70, 390  # yellow
        if number == 21:
            return 150, 390
        if number == 22:
            return 230, 390
        if number == 23:
            return 310, 390
        if number == 24:
            return 390, 390
        if number == 25:
            return 390, 310
        if number == 26:
            return 390, 230
        if number == 27:
            return 390, 150
        if number == 28:
            return 390, 70
        if number == 29:
            return 450, 70
        if number == 30:
            return 510, 70  # green
        if number == 31:
            return 510, 150
        if number == 32:
            return 510, 230
        if number == 33:
            return 510, 310
        if number == 34:
            return 510, 390
        if number == 35:
            return 590, 390
        if number == 36:
            return 670, 390
        if number == 37:
            return 750, 390
        if number == 38:
            return 830, 390
        if number == 39:
            return 830, 450
        if number == 40:  # number 40 is finish
            return 550, 450
    elif colour == colourBlack:
        if number == 0:  # start, impossible
            return 390, 830  # black
        if number == 1:
            return 390, 750
        if number == 2:
            return 390, 670
        if number == 3:
            return 390, 590
        if number == 4:
            return 390, 510
        if number == 5:
            return 310, 510
        if number == 6:
            return 230, 510
        if number == 7:
            return 150, 510
        if number == 8:
            return 70, 510
        if number == 9:
            return 70, 450
        if number == 10:
            return 70, 390  # yellow
        if number == 11:
            return 150, 390
        if number == 12:
            return 230, 390
        if number == 13:
            return 310, 390
        if number == 14:
            return 390, 390
        if number == 15:
            return 390, 310
        if number == 16:
            return 390, 230
        if number == 17:
            return 390, 150
        if number == 18:
            return 390, 70
        if number == 19:
            return 450, 70
        if number == 20:
            return 510, 70  # green
        if number == 21:
            return 510, 150
        if number == 22:
            return 510, 230
        if number == 23:
            return 510, 310
        if number == 24:
            return 510, 390
        if number == 25:
            return 590, 390
        if number == 26:
            return 670, 390
        if number == 27:
            return 750, 390
        if number == 28:
            return 830, 390
        if number == 29:
            return 830, 450
        if number == 30:
            return 830, 510  # red
        if number == 31:
            return 750, 510
        if number == 32:
            return 670, 510
        if number == 33:
            return 590, 510
        if number == 34:
            return 510, 510
        if number == 35:
            return 510, 590
        if number == 36:
            return 510, 670
        if number == 37:
            return 510, 750
        if number == 38:
            return 510, 830
        if number == 39:
            return 450, 830
        if number == 40:  # number 40 is finish
            return 450, 550


screen = pygame.display.set_mode([900, 900])
pygame.display.set_caption('Mensch Ärgere Dich Nicht!')
myfont = pygame.font.SysFont('Georgia', 30)


yellow_dice_image = pygame.image.load("../res/dice.bmp")
green_dice_image = pygame.image.load("../res/dice.bmp")
black_dice_image = pygame.image.load("../res/dice.bmp")
red_dice_image = pygame.image.load("../res/dice.bmp")


yellow_dice = screen.blit(yellow_dice_image, (50, 50))
green_dice = screen.blit(green_dice_image, (750, 50))
black_dice = screen.blit(black_dice_image, (50, 750))
red_dice = screen.blit(red_dice_image, (750, 750))


textmensch = myfont.render('Mensch', True, (0, 0, 0))
textaergere = myfont.render('Ärgere', True, (0, 0, 0))
textdich = myfont.render('Dich', True, (0, 0, 0))
textnicht = myfont.render('Nicht!', True, (0, 0, 0))

myfont = pygame.font.SysFont('Georgia', 30)

colourYellow = (255, 234, 3)
colourGreen = (3, 148, 61)
colourBlack = (24, 24, 22)
colourRed = (225, 2, 15)

yellow = Player(0, colourYellow, 'yellow')
green = Player(0, colourGreen, 'green')
black = Player(0, colourBlack, 'black')
red = Player(0, colourRed, 'red')

radius = 50

yellow_rect = pygame.draw.rect(screen, yellow.colour,
                               (correctposition(yellow.colour, yellow.position) + (radius, radius)))
green_rect = pygame.draw.rect(screen, yellow.colour,
                              (correctposition(green.colour, green.position) + (radius, radius)))
black_rect = pygame.draw.rect(screen, yellow.colour,
                              (correctposition(black.colour, black.position) + (radius, radius)))
red_rect = pygame.draw.rect(screen, yellow.colour,
                            (correctposition(red.colour, red.position) + (radius, radius)))

ecf = EventCreationTool.EventFactory()
public_key = ecf.get_feed_id()
chat_function = ChatFunction()
first_event = ecf.first_event('chat', chat_function.get_host_master_id())

chat_function.insert_event(first_event)
dictionary = {
    'role': 'free',
    'public_key': public_key
}
pickle.dump(dictionary, open(pickle_file_names[1], "wb"))

# Set EventFactory
chat_function = ChatFunction()
chat_function.get_current_event(chat_function.get_all_feed_ids()[1])
feed_id = dictionary['public_key']
most_recent_event = chat_function.get_current_event(feed_id)
ecf = EventCreationTool.EventFactory(most_recent_event)  # so that the same ID is used


def draw_background():
    pygame.init()

    screen.fill((253, 235, 149))

    screen.blit(textmensch, (150, 280))
    screen.blit(textaergere, (620, 280))
    screen.blit(textdich, (150, 620))
    screen.blit(textnicht, (620, 620))

    screen.blit(yellow_dice_image, (50, 70))
    screen.blit(green_dice_image, (750, 70))
    screen.blit(black_dice_image, (50, 770))
    screen.blit(red_dice_image, (750, 770))

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


def draw_players():
    pygame.draw.rect(screen, yellow.colour, (correctposition(yellow.colour, yellow.position) + (radius, radius)))
    pygame.draw.rect(screen, green.colour, (correctposition(green.colour, green.position) + (radius, radius)))
    pygame.draw.rect(screen, black.colour, (correctposition(black.colour, black.position) + (radius, radius)))
    pygame.draw.rect(screen, red.colour, (correctposition(red.colour, red.position) + (radius, radius)))
    pygame.display.update()
    time.sleep(1)


def staggered_move(player, throw):
    target = throw + player.position
    if player.position > 40:
        player.position = 40
    if target > 40:
        target = 40
    while player.position < target:
        player.position = player.position + 1
        draw_background()
        draw_players()
    to_save = player.colourstring+"#split:#"+str(player.position)
    new_event = ecf.next_event('chat/saveMessage',
                               {'messagekey': to_save, 'chat_id': 'game', 'timestampkey': time.time()})
    chat_function.insert_chat_msg(new_event)
    sync_server()


def game_loop():
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    sync_client()
                    args = ['ui']
                    feed_control.main(args)
                    sync_client()
                    read_from_others()
                if event.key == pygame.K_RIGHT:
                    sync_server()
        if pygame.mouse.get_pressed()[0]:
            if yellow_dice.collidepoint(pygame.mouse.get_pos()):
                staggered_move(yellow, throw_dice())
            if green_dice.collidepoint(pygame.mouse.get_pos()):
                staggered_move(green, throw_dice())
            if black_dice.collidepoint(pygame.mouse.get_pos()):
                staggered_move(black, throw_dice())
            if red_dice.collidepoint(pygame.mouse.get_pos()):
                staggered_move(red, throw_dice())


        pygame.display.update()
    # pygame.quit()


def throw_dice():
    number = random.choice([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12])
    print('Rolled ', number)
    return number


def sync_server():
    udp_connection.Server(4051)


def sync_client():
    client = udp_connection.Client(4051)
    database_sync.sync_database(client.get_list_of_needed_extensions(), client.get_packet_to_receive_as_bytes())


def read_from_others():
    chat = chat_function.get_full_chat('game')

    for i in range(1, len(chat)):
        chat_message = chat[i][0].split(
            "#split:#")  # a chat-message is like: username#split:#message, so we need to split this two
        colourtomove = chat_message[0]
        movetonumber = chat_message[1]
        print(colourtomove, movetonumber)

        if colourtomove == 'yellow':
            if yellow.position < movetonumber:
                staggered_move(yellow, (movetonumber - yellow.position))
        if colourtomove == 'red':
            if red.position < movetonumber:
                staggered_move(red, (movetonumber - red.position))
        if colourtomove == 'green':
            if green.position < movetonumber:
                staggered_move(green, (movetonumber - green.position))
        if colourtomove == 'black':
            if black.position < movetonumber:
                staggered_move(black, (movetonumber - black.position))



if __name__ == '__main__':
    draw_background()
    draw_players()
    game_loop()
