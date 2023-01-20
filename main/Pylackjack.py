import pygame
import sys
from spritesheet import SpriteSheet
import ctypes
from pygame.locals import *
from random import choice

# Initializes pygame and creates the game icon:

pygame.init()

gameIcon = pygame.image.load('sprites/pylackjack.png')
pygame.display.set_icon(gameIcon)
pygame.display.set_caption("Pylackjack")

# Colors! These are chosen using a tuple of RGB values:

black = (0, 0, 0)
white = (255, 255, 255)
red = (255, 0, 0)
green = (0, 255, 0)
blue = (0, 0, 255)
dark_green = (0, 128, 0)
magenta = (255, 0, 255)
keycolor = (217, 87, 99)
msgray = (189, 189, 189)

# Global variables:

fpsclock = pygame.time.Clock()

(screen_width, screen_height) = (480, 640)
screen_centerx = (screen_width/2)
screen_centery = (screen_height/2)
(s_w, s_h) = (screen_width, screen_height)

screen = pygame.display.set_mode((screen_width, screen_height))
screen_rect = screen.get_rect()

# TODO: add splitting, fix drop menu code

# Functions:


def quitgame():
    """Quits the game."""
    print("Exited successfully.")
    pygame.quit()
    sys.exit()


def text_objects(text, font, textcolor=black):
    """Helper function for message_display. Defines the font and rect of the text input."""
    textsurf = font.render(text, False, textcolor)
    return textsurf, textsurf.get_rect()


def message_display(text, font="microsoft sans serif", size=24, center=True, x=0, y=0, textcolor=black):
    """Displays a message. Basically a GUI version of print().
       If centered, the x and y coordinates start at the center."""
    font_and_size = pygame.font.SysFont(font, size)
    textsurf, textrect = text_objects(text, font_and_size, textcolor)
    if center:
        textrect.center = (screen_centerx + x, screen_centery + y)
    else:
        textrect = (x, y)
    screen.blit(textsurf, textrect)


def end_bet():
    """Ends the bet and initiates the start of the round."""
    global Bet, Player, betting, roundstart, playing
    Player.available_money -= Bet.value
    betting = False
    playing = True
    roundstart = True
    initround()


def draw_rect(rectcolor, x, y, w, h, center=False):
    """Draws a rect. Pretty straightforward."""
    if center:
        x = screen_centerx - (w/2)
        y = screen_centery - (h/2)
    pygame.draw.rect(screen, rectcolor, (x, y, w, h))


def draw_img(img, x=0, y=0, center=True, colorkey=magenta):
    """Draws an image. The colorkey by default is magenta aka (255, 0, 255)."""
    img = pygame.image.load(img)
    w, h = img.get_size()
    if center:
        x = screen_centerx - (w/2) + x
        y = screen_centery - (h/2) + y
    img = img.convert()
    img.set_colorkey(colorkey)
    img_rect = img.get_rect()
    img_rect.x = x
    img_rect.y = y
    screen.blit(img, img_rect)


def initround():
    """Gives the player and dealer their initial cards at the start of the round."""
    # Player's cards:
    CardDraw(Player, y=121)
    CardDraw(Player, y=121)
    # Dealer's card:
    CardDraw(Dealer, y=-152)


def restartround():
    """Restarts the round."""
    global restart
    restart = True


def endround():
    """Ends the round."""
    global roundstart, betting, standing, endgame
    roundstart = False
    betting = False
    standing = False
    endgame = False


def showabout():
    """Displays the about message."""
    creditsmessage = "Pylackjack 1.02\nCopyright (c) 2018 Hxdce\nLicensed under the CC BY 3.0 License"
    ctypes.windll.user32.MessageBoxW(0, creditsmessage, "About", 64)


def resetstats():
    """Resets the player's stats, and the bet value."""
    global resettingstats
    resettingstats = True
    restartround()


def sprite_set(w, h, spritesheet, x, y, sloc_n, sloc_y=0):
    """Sets the sprite currently being used. sloc_n and sloc_y are multipliers
       that change the index on the spritesheet of the active sprite.
       The DropMenu class doesn't use sloc_y, but the ImgButton class does."""
    index = (sloc_n*w, sloc_y*h, w, h)
    image = spritesheet.image_at(index)
    image_rect = image.get_rect()
    image_rect.x = x
    image_rect.y = y
    return index, image, image_rect, image_rect.x, image_rect.y


def winlose(target, gamewon=False, tie=False):
    """Modifies the player's win-lose statistics."""
    global winlose_inc, Bet
    if not winlose_inc:
        if tie:
            target.available_money += Bet.value
        else:
            if gamewon:
                target.available_money += Bet.value*2
                target.wins += 1
            else:
                target.loses += 1
        winlose_inc = True


# Classes:

class DropMenu:
    """Component class for drop-menu buttons. Attaches to the botton of the button."""
    activate = False

    def __init__(self, spritesheet_img):
        self.ss = SpriteSheet(spritesheet_img[:-4] + "_sub.png")
        self.w, self.h = self.ss.sheet.get_size()
        self.w /= 2
        spritesetter = sprite_set(self.w, self.h, self.ss, 0, 0, 0)
        self.index, self.image, self.image_rect, self.image_rect.x, self.image_rect.y = spritesetter
        self.action = None

    def draw(self, x=0, y=0):
        self.image_rect.x = x
        self.image_rect.y = y
        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()
        if self.image_rect.collidepoint(mouse):
            spritesetter = sprite_set(self.w, self.h, self.ss, x, y, 1)
            self.index, self.image, self.image_rect, self.image_rect.x, self.image_rect.y = spritesetter
            if click[0] == 1 and self.action is not None:
                self.action()
        else:
            spritesetter = sprite_set(self.w, self.h, self.ss, x, y, 0)
            self.index, self.image, self.image_rect, self.image_rect.x, self.image_rect.y = spritesetter

        screen.blit(self.image, self.image_rect)


class DropMenuButton:
    """Object class for image-based drop-menu buttons. Has three states for the drop menu button."""
    activate = False

    def __init__(self, w, h, spritesheet_img):
        """Defines the width, height, and spritesheet image of the menu button."""
        self.ss = SpriteSheet(spritesheet_img)
        self.filename = spritesheet_img
        self.w = w
        self.h = h
        self.dropmenu = DropMenu(spritesheet_img)

    def draw(self, x=0, y=0, action=None):
        """Draws the drop menu button."""
        global menutimer
        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()
        index, image, image_rect, image_rect.x, image_rect.y = sprite_set(self.w, self.h, self.ss, x, y, 0)
        dmenu_rect = self.dropmenu.image_rect
        self.dropmenu.action = action
        if image_rect.collidepoint(mouse) and not DropMenuButton.activate:
            index, image, image_rect, image_rect.x, image_rect.y = sprite_set(self.w, self.h, self.ss, x, y, 1)
            if click[0] == 1 and menutimer == 0:
                DropMenuButton.activate = True
                menutimer = 10
        if (image_rect.collidepoint(mouse) or dmenu_rect.collidepoint(mouse)) and DropMenuButton.activate:
            index, image, image_rect, image_rect.x, image_rect.y = sprite_set(self.w, self.h, self.ss, x, y, 2)
            if click[0] == 1 and menutimer == 0:
                DropMenuButton.activate = False
                menutimer = 10
            self.dropmenu.draw(x=image_rect.left, y=image_rect.bottom)
        if not (image_rect.collidepoint(mouse) or dmenu_rect.collidepoint(mouse)):
            self.dropmenu.image_rect.x = screen_width
        if (mouse[1] > image_rect.y + self.h + self.dropmenu.h) and DropMenuButton.activate:
            DropMenuButton.activate = False
        # The code for this is honestly a mess... it needs to be fixed.
        screen.blit(image, image_rect)


class ImgButton:
    """Object class for image-based buttons. Only buttons with binary states are supported."""
    def __init__(self, w, h, spritesheet_img, sloc_x, sloc_y):
        """Defines the width, height, a sprite-sheet image, and sprite location on the sheet."""
        self.ss = SpriteSheet(spritesheet_img)
        self.w = w
        self.h = h
        self.s_x = sloc_x  # Multiplier for the chosen sprite's location on the sprite-sheet.
        self.s_y = sloc_y  # Each increase of one moves by the width and/or height of the sprite size.
        self.releaseactivate = False

    def draw(self, x=0, y=0, action=None, center=False, act_on_release=False, canmoveoff=False):
        """Draws an image-based button object and defines its action. If centered, the x and y coordinates
           start at the center. Action defines what action is executed when the button is clicked, and
           act_on_release determines if the action will execute when the button is released."""
        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()
        if center:
            x = (screen_centerx - (self.w/2)) + x
            y = (screen_centery - (self.h/2)) + y
        spritesetter = sprite_set(self.w, self.h, self.ss, x, y, self.s_x, self.s_y)
        index, image, image_rect, image_rect.x, image_rect.y = spritesetter
        if click[0] == 1 and action is not None and image_rect.collidepoint(mouse):
            spritesetter = sprite_set(self.w, self.h, self.ss, x, y, (self.s_x+1), self.s_y)
            index, image, image_rect, image_rect.x, image_rect.y = spritesetter
            screen.blit(image, image_rect)
            if not act_on_release:
                action()
            elif act_on_release:
                self.releaseactivate = True
        if not click[0] and self.releaseactivate and (image_rect.collidepoint(mouse) or canmoveoff):
            action()
            self.releaseactivate = False
        elif not click[0] and self.releaseactivate:
            self.releaseactivate = False
        screen.blit(image, image_rect)


class CardDraw(pygame.sprite.Sprite):
    """Class for card objects."""
    cards = SpriteSheet('sprites/cardsheet.png')

    cix = 75
    ciy = 100
    width = 71
    height = 96
    center = (screen_centerx - (width/2), screen_centery - (height/2))

    # These two variables define the card values and create the deck of cards:

    card_values = [10, 10, 10, 11, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    available_cards = [j for i in [[[i, e] for i in range(13)] for e in range(4)] for j in i]

    nomorecards = False

    def __init__(self, targetactor, x=0, y=0, center=True):
        """Card drawer initialization. Removes a card from the deck, appends it to the target actor's card list,
           adds to the target actor's hand value, and renders the card at the specified x and y coordinate."""
        pygame.sprite.Sprite.__init__(self)

        if not CardDraw.available_cards:  # Exception handling for when the deck runs out of cards.
            CardDraw.nomorecards = True  # Under normal gameplay conditions, it is impossible for this to happen.
        else:
            cchoice, csuit = choice(CardDraw.available_cards)  # Randomly chooses a card.
            CardDraw.available_cards.remove([cchoice, csuit])  # Removes the chosen card from the deck.
            self.index = (CardDraw.cix * csuit, CardDraw.ciy * cchoice, CardDraw.width, CardDraw.height)
            self.image = CardDraw.cards.image_at(self.index, colorkey=keycolor)
            self.image_rect = self.image.get_rect()
            self.value = self.card_values[cchoice]
            if center:
                self.image_rect.x, self.image_rect.y = CardDraw.center[0] + x, CardDraw.center[1] + y
            else:
                self.image_rect.x = x
                self.image_rect.y = y
            targetactor.value += self.value  # Increases the target actor's hand value.
            targetactor.cards.append(self)  # Adds the card to the target actor's hand.
            if cchoice == 3:  # If the chosen card is an ace...
                targetactor.gotace = True
            if len(targetactor.cards) > 1:
                # For rendering purposes.
                # Puts the new card on top of the hand (slightly offset so the prev card's value is visible)...
                # ...then moves the hand over by half of the offset so it remains centered
                targetactor.cards[-1].image_rect.x = self.center[0] + targetactor.cardoffset
                for c in range(len(targetactor.cards)-1):
                    targetactor.cards[c].image_rect.x -= 7
                targetactor.cardoffset += 7

    @staticmethod
    def resetdeck():
        """Resets the deck of cards."""
        CardDraw.available_cards = [j for i in [[[i, e] for i in range(13)] for e in range(4)] for j in i]
        CardDraw.nomorecards = False

    def draw(self):
        """Renders the cards on the screen."""
        screen.blit(self.image, self.image_rect)


class Actor:
    """Actor class for instance variables shared by the player and dealer."""

    def __init__(self):
        self.name = self

        self.busted = False
        self.gotace = False
        self.acecount = 0
        self.turn = False
        self.value = 0
        self.kqjlist = ["King!", "Queen!", "Jack!"]
        self.kingqueenjack = 10
        self.cardoffset = 7
        self.natural = False

        self.cards = []


class P(Actor):
    """Player class. Inherits from the Dealer class."""
    available_money = 100
    surrendered = False
    wins = 0
    loses = 0

    def hit(self):
        """Adds a card to the player's hand."""
        CardDraw(self, y=121)

    @staticmethod
    def stand():
        """Makes the player stand - i.e. ends their turn."""
        global roundstart, standing, actiontimer
        roundstart = False
        standing = True
        actiontimer = 240

    def dbl_down(self):
        """Doubles down - Increases their bet by a maximum of 100% and stands after the next hit."""
        global roundstart, standing, actiontimer, Bet
        if self.available_money >= Bet.value:
            self.available_money -= Bet.value
            Bet.value *= 2
        else:
            Bet.value += self.available_money
            self.available_money = 0
        CardDraw(self, y=121)
        roundstart = False
        standing = True
        actiontimer = 240

    def surrender(self):
        """Surrenders, instantly ending the the game and returning 1/2 of the player's bet."""
        global roundstart, betting, Bet, restart, playing, actiontimer
        betting = True
        roundstart = False
        playing = False
        restart = True
        self.surrendered = True
        actiontimer += 120
        self.available_money += (Bet.value//2)
        Bet.value = self.available_money


class D(Actor):
    """Dealer class. Inherits from the Actor class."""
    holecardrevealed = False


class Betobject:
    """Class for the money used in the bet."""
    value = 100  # Default bet value.

    def __init__(self):
        self.modifywait = 15  # The delay between each successive increment or decrement of the value.
        self.modifywait_waittime = 15
        self.modify_value_increase_rate = 0
        self.modify_vir_waittime = 15
        self.waittime = 0

    def keep_in_valid_range(self, player):
        """Keeps the bet from exceeding the player's available funds."""
        if self.value < 0:
            self.value = 0
        if self.value > player.available_money:
            self.value = player.available_money

    def add(self):
        """Adds to the bet."""
        self.change_value(1)

    def sub(self):
        """Subtracts from the bet."""
        self.change_value(-1)

    def change_value(self, n):
        """Changes the bet's value. The speed of the change increases as the button is held,
           then resets when released."""
        if self.waittime < 1:
            self.value += n * (2 ** self.modify_value_increase_rate)
            self.waittime += self.modifywait
        if self.modifywait > 0 and self.modifywait_waittime < 1:
            self.modifywait -= 2.5
            self.modifywait_waittime = 15
        if self.modifywait < 1 and self.modify_vir_waittime < 1:
            self.modify_value_increase_rate += 1
            self.modify_vir_waittime = 15
        self.waittime -= 1
        self.modifywait_waittime -= 1
        if self.modifywait < 1:
            self.modify_vir_waittime -= 1

    def reset_bet(self):
        """Resets the bet to its default value."""
        self.value = 100


# Variables inheriting from the classes, and other useful game-loop global variables:

Bet = Betobject()

Player = P()
Dealer = D()

card_values = [10, 10, 10, 11, 2, 3, 4, 5, 6, 7, 8, 9, 10]

# available_cards = [[0, 0, 10]]

increasebutton = ImgButton(16, 16, "sprites/betbuttons.png", 0, 0)
decreasebutton = ImgButton(16, 16, "sprites/betbuttons.png", 0, 1)

hitbutton = ImgButton(48, 32, "sprites/button_hit.png", 0, 0)
standbutton = ImgButton(78, 32, "sprites/button_stand.png", 0, 0)
doubledownbutton = ImgButton(122, 32, "sprites/button_doubledown.png", 0, 0)
surrenderbutton = ImgButton(124, 32, "sprites/button_surrender.png", 0, 0)

acceptbutton = ImgButton(96, 32, "sprites/acceptbutton.png", 0, 0)

Gamemenu = DropMenuButton(41, 19, "sprites/dropmenu_game.png")
Helpmenu = DropMenuButton(35, 19, "sprites/dropmenu_help.png")

hold_time = 0
hold_increase_time = 30
prev_hold_time = hold_time

betting = True
roundstart = False
standing = False
endgame = False
playing = False
restart = False
resettingstats = False
winlose_inc = False

actiontimer = 0
menutimer = 0

debugmode = False
# For the card coordinates:
# to move a centered card back to the origin for x is -(screen_width/2 - (card.width/2)), or -int(204.5)
# to move a centered card back to the origin for y is -(screen_height/2 - (card.height/2)), or -272
# to convert center=False coords to center=True cords, simply add the old (x, y) coords to (205, -272)

# Game loop:

while True:

    if restart:  # Reinitializes the game loop's global variables
        Player.__init__()
        Dealer.__init__()
        CardDraw.resetdeck()
        betting = True
        roundstart = False
        standing = False
        endgame = False
        playing = False
        winlose_inc = False

        if resettingstats:
            Player.available_money = 100
            Player.wins = 0
            Player.loses = 0
            Bet.value = 100
            resettingstats = False

        restart = False

    for event in pygame.event.get():
        if event.type == QUIT:
            quitgame()
        if event.type == pygame.MOUSEBUTTONDOWN:
            pass
        if event.type == pygame.MOUSEBUTTONUP:
            # Re-initializes (i.e. resets) the betting variables (except for the betting amount):
            Bet.__init__()

    # Key presses:

    keys_pressed = pygame.key.get_pressed()
    if (keys_pressed[K_LALT] or keys_pressed[K_RALT]) and keys_pressed[K_F4]:
        quitgame()

    # Screen-clearing code:

    screen.fill(dark_green)

    # Game logic and drawing code:

    draw_img("sprites/bottombox.png", 0, screen_height-25, center=False)
    draw_rect(msgray, 0, 0, screen_width, 19)
    Gamemenu.draw(action=resetstats)
    Helpmenu.draw(x=Gamemenu.w, action=showabout)
    message_display("Money: " + str(Player.available_money), size=18, x=4, y=screen_height-24, center=False)
    message_display("Wins: " + str(Player.wins), size=18, x=screen_width-165, y=screen_height-24, center=False)
    message_display("Loses: " + str(Player.loses), size=18, x=screen_width-87, y=screen_height-24, center=False)
    if CardDraw.nomorecards:
        message = "Deck is out of cards!\nSomething terribly wrong happened...\n...or you're using debug mode."
        ctypes.windll.user32.MessageBoxW(0, message, "Uhh...", 64)
        restartround()

    # Debugging stuff:

    if debugmode:
        message_display("Dealer value: " + str(Dealer.value), size=18, x=4, y=22, center=False)
        message_display("Player value: " + str(Player.value), size=18, x=4, y=40, center=False)
        deck_len = str(len(CardDraw.available_cards))
        message_display("Cards left in deck: " + deck_len, size=18, x=4, y=58, center=False)

    if betting:  # Betting stage.

        Bet.keep_in_valid_range(Player)  # Keeps the bet in the valid range.
        draw_img("sprites/cardback.png", y=-152, colorkey=keycolor)
        message_display("Welcome to blackjack.", x=0, y=-14)
        message_display("Place your bet:", x=0, y=14)
        draw_img("sprites/betbox.png", 178, 400, center=False)
        numoffset = (len(str(Bet.value)) - 3) * 8
        message_display(str(Bet.value), x=16-numoffset, y=96, size=28)
        increasebutton.draw(x=286, y=400, action=Bet.add)
        decreasebutton.draw(x=286, y=416, action=Bet.sub)
        acceptbutton.draw(y=150, center=True, action=end_bet, act_on_release=True)
        if actiontimer:
            if Player.surrendered:
                if actiontimer == 1:
                    Player.surrendered = False
                message_display("House takes half of bets.", y=188)
            actiontimer -= 1

    if playing:  # Starts the game.

        # Renders the player and dealer's cards:
        for card in Player.cards:
            card.draw()
        for card in Dealer.cards:
            card.draw()

        if roundstart:  # Start of the round. Lets the player make their moves until they either stand or bust.
            # Getting a natural 21 bypasses this.
            message_display("Dealer's hand:", y=-225)
            message_display("Your hand:", y=48)
            hitbutton.draw(x=-174, y=240, center=True, act_on_release=True, action=Player.hit)
            standbutton.draw(x=-103, y=240, center=True, act_on_release=True, action=Player.stand)
            doubledownbutton.draw(x=5, y=240, center=True, act_on_release=True, action=Player.dbl_down)
            surrenderbutton.draw(x=136, y=240, center=True, act_on_release=True, action=Player.surrender)
            if Player.value == 21 and len(Player.cards) == 2:
                Player.natural = True

        if standing:  # Basically a loop that runs until the dealer either busts or has a hand value >= 17.
            if actiontimer > 120:  # Action timer starts at 240, so at 60 fps this will display for two seconds.
                message_display("Standing. Dealers turn.")
            elif actiontimer == 120:  # Draws a card after two seconds.
                CardDraw(Dealer, y=-152)
                actiontimer -= 1
            if actiontimer <= 120:
                if not Dealer.holecardrevealed:  # If the dealer's hole card hasn't been revealed yet...
                    message_display("Dealer's hole card revealed.")
                if Dealer.holecardrevealed:  # If the hole card has already been revealed...
                    message_display("Dealer hits.")
            if not actiontimer and Dealer.value < 17:  # If the action timer runs out but the dealer's hand is < 17...
                # Dealer doesn't stop hitting until their hand is at least 17.
                Dealer.holecardrevealed = True
                actiontimer = 120
            elif not actiontimer and Dealer.value >= 17:  # Dealer's turn ends when their hand is >= 17.
                endgame = True
                standing = False
            else:
                actiontimer -= 1

        # Automatic win/lose conditions:

        if Player.natural:  # If the player's two initial cards == 21 (automatic win):
            endround()
            message_display("You got a natural 21!", y=-14)
            message_display("You win!", y=14)
            winlose(Player, gamewon=True)
            acceptbutton.draw(y=240, center=True, action=restartround, act_on_release=True)
        if Player.value > 21 and not debugmode:
            if Player.gotace and Player.acecount == 0:
                # Changes the ace's value to 1 if the player has ONE ace and busts on a "soft" hand.
                Player.value -= 10
                Player.acecount += 1
            else:  # If the player busts and has no ace, or has one ace and "hard" busts (hand value > 31):
                endround()
                message_display("Busted!", y=-14)
                message_display("You lose.", y=14)
                winlose(Player, gamewon=False)
                acceptbutton.draw(y=240, center=True, action=restartround, act_on_release=True)
        if Dealer.value > 21:
            if Dealer.gotace and Dealer.acecount == 0:
                # Changes the ace's value to 1 if the dealer has ONE ace and busts on a "soft" hand.
                Dealer.value -= 10
                Dealer.acecount += 1
            else:  # If the dealer busts and has no ace, or has one ace and "hard" busts (hand value > 31):
                endround()
                message_display("Dealer busted.", y=-14)
                message_display("You win!", y=14)
                winlose(Player, gamewon=True)
                acceptbutton.draw(y=240, center=True, action=restartround, act_on_release=True)

        # Win/Lose conditions:

        if endgame:
            if Player.value > Dealer.value:
                message_display("Your hand is greater than dealer's.", y=-14)
                message_display("You win!", y=14)
                winlose(Player, gamewon=True)
            elif Player.value < Dealer.value:
                message_display("Your hand is less than dealer's.", y=-14)
                message_display("You lose.", y=14)
                winlose(Player, gamewon=False)
            else:
                message_display("Your hand is equal to dealer's.", y=-14)
                message_display("Tie.", y=14)
                winlose(Player, tie=True)
            acceptbutton.draw(y=240, center=True, action=restartround, act_on_release=True)

    if menutimer > 0:
        menutimer -= 1

    pygame.display.update()
    fpsclock.tick(60)
