# Blackjack.

import sys
from random import randint, choice

# Global variables and strings (too long to fit in PEP-8 guidelines otherwise):

wins = 0
loses = 0
totalplays = 0
ratio = 0
money = 100
rationotset = True

optionlist = \
    "Hit (1), Stand (2), Double down (3), Surrender (4), or Options (5)."

optionsmenuchoices = \
    "View Player Stats (1), Reset Stats (2), Return (3), or Quit (n)"

stats = \
      "Wins: %i, Loses: %i, Ratio: %f, Money: %i, Times played: %i" % \
      (wins, loses, round(ratio, 1), money, totalplays)

# Classes:


class Actor(object):
    """actor class for variables and methods shared by player and dealer"""
    name = "Generic actor"
    busted = False
    gotace = False
    turn = False
    numofaces = 0
    value = 0
    ace = 11
    kqjlist = ["King!", "Queen!", "Jack!"]
    kingqueenjack = 10

    def __init__(self):
        pass

    def gethand(self, nowworth):
        """Print's the person's hand. 'nowworth' is a boolean for printing
           'X's hand is now worth Y.' instead of 'X's hand is worth Y.'"""
        if nowworth:
            print("%s's hand is now worth %i." % (self.name, self.value))
        else:
            print("%s's hand is worth %i." % (self.name, self.value))

    def silentcardpick(self):
        """Picks card with no announcement."""
        cpick = randint(1, 14)
        if cpick == 1:
            print("Ace!")
            self.value += self.ace
            self.gotace = True
        elif cpick > 10:
            print(choice(self.kqjlist))
            self.value += self.kingqueenjack
        else:
            print(str(cpick))
            self.value += cpick

    def cardpick(self):
        """Picks card with announcement."""
        self.silentcardpick()
        self.gethand(False)

    def softace(self):
        """Sets the ace's value to 1 and lower's the person's value by 10."""
        self.ace = 1
        self.value -= 10
        self.gethand(True)


class D(Actor):
    """Dealer class."""
    name = "Dealer"
    holeace = False
    holekqj = False
    holecard = 0
    revealhole = True

    def holecardpick(self):
        """Picks the dealer's hole card."""
        cpick = randint(1, 14)
        if cpick == 1:
            self.holeace = True
            self.value += self.ace
            self.gotace = True
        elif cpick > 10:
            self.holekqj = True
            self.value += self.kingqueenjack
        else:
            self.holecard = cpick
            self.value += cpick

    def revealholepick(self):
        """Reveals the dealer's hole card."""
        print("Dealer's hole card revealed.")
        if self.holeace:
            print("Ace!")
        elif self.holekqj:
            print(choice(self.kqjlist))
        else:
            print(str(self.holecard))
        self.gethand(False)


class P(Actor):
    """Player class."""
    name = "Player"
    stand = False
    surrender = False
    inoptions = False
    resetstats = False

    def doubledown(self):
        """Doubles the player's bet, then forces them to stand
           after picking one more card."""
        self.cardpick()

    def options(self):
        print("-Options Menu-")
        ochoice = input("Choose to %s\n" % (optionsmenuchoices + "Choice: "))
        while ochoice not in "Nn" \
                and not (ochoice.isdigit() and int(ochoice) in range(1, 4)):
            # If the choice is not a digit or not in the range of choices.
            ochoice = input("Invalid input.\nChoice: ")
        if ochoice in "Nn":
            print("---\n--\n-")
            sys.exit()
        elif int(ochoice) == 1:
            print(stats)
        elif int(ochoice) == 2:
            self.resetstats = True
            print("Stats reset.")
        elif int(ochoice) == 3:
            self.inoptions = False
            print("-")
            self.gethand(False)


##################

playing = True

print("Welcome to blackjack.")

while playing:

    # Game variables, reset each round:
    
    dealer = D()
    player = P()
    roundstart = True

    print("-\n--\n---")

    # Placing your bet.

    bet = input("You have %i dollarydoos. Place your bet: " % money)
    while not bet.isdigit() or int(bet) > money:
        # If the input is not a digit,
        # or if the amount betted exceeds player's balance.
        if not bet.isdigit():
            bet = input("Invalid input.\nPlace your bet: ")
        elif int(bet) > money:
            bet = input("Insufficient funds.\nPlace your bet: ")
    bet = int(bet)
    money -= bet

    if roundstart:
        # Starts the round. Sets up the dealer's initial hand,
        # dealer's hole (hidden/face down) card, and
        # gives the player their initial two cards.
        
        print("Dealer's initial hand:")
        
        dealer.cardpick()
        dealer.holecardpick()
        
        # Player's initial two cards:
        
        print("-\nPlayer's initial hand:")
        player.silentcardpick()
        player.cardpick()
        if player.value == 21:
            # Checks if player got 21 on first two cards (blackjack/natural).
            print("Player got a natural 21!\n-")
            player.turn = False
            dealer.turn = True
        else:
            player.turn = True
            print("-\nPlayer's turn.")
        roundstart = False

    # Player's turn.
    while player.turn:
        if (player.value > 21 and not player.gotace)\
           or (player.value > 21 and player.gotace and player.ace == 1):
            # Checks if the player busted. Instant lose.
            dealer.turn = False
            break
        if player.value > 21 and player.gotace and player.ace == 11:
            # Checks if the player busted with one ace.
            print("Player had a soft bust. Ace is now worth 1.")
            player.softace()
        pchoice = input("Choose to %s\n" % (optionlist + "Choice: "))
        while not pchoice.isdigit() or int(pchoice) not in range(1, 6):
            # If the choice is not a digit or not in the range of choices.
            pchoice = input("Invalid input.\nChoice: ")
        if int(pchoice) == 1:
            # If Hit is chosen, randomly selects a card.
            player.cardpick()
        elif int(pchoice) == 2:
            # If Stand is chosen, end turn.
            print("Player stood.\n-")
            dealer.turn = True
            break
        elif int(pchoice) == 3:
            # If Double Down is chosen, double bets, pick one card, then stand.
            if bet > money:
                print("Insufficient funds.")
            else:
                money -= bet
                bet *= 2
                print("Player doubled down. Bets doubled.")
                print("You now have %i dollarydoos." % money)
                dealer.turn = True
                player.doubledown()
                print("-")
                break
        elif int(pchoice) == 4:
            # If surrender is chosen, the round ends.
            dealer.turn = False
            player.surrender = True
            break
        elif int(pchoice) == 5:
            # Brings up the options menu.
            player.inoptions = True
            while player.inoptions:
                if totalplays > 0 and rationotset:
                    # Sets the ratio to wins/totalplays.
                    # This prevents division by zero from totalplays == 0.
                    ratio = wins/totalplays
                    rationotset = False
                player.options()
                if player.resetstats:
                    # Resets player's stats.
                    wins = 0
                    loses = 0
                    totalplays = 0
                    ratio = 0
                    money = 100
                    bet = 0
                    rationotset = True
                    player.resetstats = False

    # Dealer's turn.
    while dealer.turn:
        if dealer.revealhole:
            # Reveals the hole card.
            dealer.revealholepick()
            dealer.revealhole = False
        if dealer.value < 17:
            # Dealer keeps hitting until their hand is 17 or greater.
            dealer.cardpick()
        if dealer.value >= 17 and dealer.gotace and dealer.ace == 11:
            # If the dealer's value is greater than or equal to 17,
            # the dealer got an ace, and he hasn't had his ace
            # revalued to one (soft hand).
            print("Dealer got a soft 17. Ace is now worth 1.")
            dealer.softace()
        if dealer.value == 21:
            # If the dealer got 21.
            print("Dealer got 21!\n-")
            dealer.turn = False
        if dealer.value > 21:
            # If the dealer got more than 21 (busted).
            print("-")
            dealer.turn = False
        if (dealer.value in range(17, 22) and not dealer.gotace)\
           or (dealer.value in range(17, 22) and dealer.gotace):
            # If the dealer's hand is >= 17 without an ace,
            # or the dealer's hand  is > 17 with the ace already used (hard).
            print("Dealer stood.\n-")
            dealer.turn = False
            break

    # Game condition check:
    if player.surrender:
        print("Player surrendered. House takes half of bets.")
        money += int(bet/2)
    else:
        if player.value > 21:
            print("Player busted! You lose.")
            player.busted = True
            loses += 1
        elif dealer.value > 21:
            print("Dealer busted! You win!")
            money += bet*2
            dealer.busted = True
            wins += 1
        if not (player.busted or dealer.busted):
            if player.value > dealer.value:
                print("Player hand is greater than dealer's. You Win!")
                money += bet*2
                wins += 1
            elif player.value == dealer.value:
                print("Player's hand is the same as the dealer's. Tie.")
                money += bet
            else:
                print("Player's hand is less than dealer's. You Lose.")
                loses += 1

    # Resets the game.
    while True:
        totalplays += 1
        print("-\nNew game? y/n")
        newgameinput = input("Choice: ")
        if newgameinput in "Yy":
            break
        elif newgameinput in "Nn":
            print("---\n--\n-")
            sys.exit()
        print("Invalid input.")
    print("---\n--\n-")
