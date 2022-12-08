import operator
from cs50 import SQL
from flask import Flask, jsonify, redirect, render_template, request
import random

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure CS50 Library to use SQLite database with pazaak players data
db = SQL("sqlite:///users.db")

# dictionary of table deck, with cards ID and respective images
tableDeck = [{"id": 1, "image": "static/images/card1.png"},
             {"id": 2, "image": "static/images/card2.png"},
             {"id": 3, "image": "static/images/card3.png"},
             {"id": 4, "image": "static/images/card4.png"},
             {"id": 5, "image": "static/images/card5.png"},
             {"id": 6, "image": "static/images/card6.png"},
             {"id": 7, "image": "static/images/card7.png"},
             {"id": 8, "image": "static/images/card8.png"},
             {"id": 9, "image": "static/images/card9.png"},
             {"id": 10, "image": "static/images/card10.png"}]

# dictionary of player's possible choices for his deck, with cards ID and respective images
mainDeck = [{"id": 1, "image": "static/images/card1.png"},
            {"id": 2, "image": "static/images/card2.png"},
            {"id": 3, "image": "static/images/card3.png"},
            {"id": 4, "image": "static/images/card4.png"},
            {"id": 5, "image": "static/images/card5.png"},
            {"id": 6, "image": "static/images/card6.png"},
            {"id": -1, "image": "static/images/cardn1.png"},
            {"id": -2, "image": "static/images/cardn2.png"},
            {"id": -3, "image": "static/images/cardn3.png"},
            {"id": -4, "image": "static/images/cardn4.png"},
            {"id": -5, "image": "static/images/cardn5.png"},
            {"id": -6, "image": "static/images/cardn6.png"},
            {"id": 11, "image": "static/images/card1or1.png"},
            {"id": 12, "image": "static/images/card2or2.png"},
            {"id": 13, "image": "static/images/card3or3.png"},
            {"id": 14, "image": "static/images/card4or4.png"},
            {"id": 15, "image": "static/images/card5or5.png"},
            {"id": 16, "image": "static/images/card6or6.png"},
            {"id": 17, "image": "static/images/card2and4.png"},
            {"id": 18, "image": "static/images/card3and6.png"}]

# list of possible AI opponents
aiNames = ["Atton Rand", "Mira", "Kreia", "Bao-Dur", "Visas Marr", "Goto", "HK-47", "T3-M4", "Mical", "Brianna", "Mandalore",
           "Hanharr", "The Champ", "Geredi", "Dahnis", "S4-C8-GE3", "Mebla Dule", "Nikko", "Pato Ado"]

# list of dictionary with the player's card choices
playerDeck = []

# dictionary with all the match data to be sent to the html pages through jinja (on initial render)
# and ajax success response (after the initial render)
matchData = {"PlayerScore": 0,
             "AiScore": 0,
             "PlayerTable": [],
             "PlayerHand": [],
             "AiTable": [],
             "AiHand": [],
             "PlayerSetWins": 0,
             "AiSetWins": 0,
             "PlayerStance": "Skip",
             "AiStance": "Skip",
             "message": "",
             "PlayerName": "",
             "AiName": "",
             "GameEnded": 0,
             }


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


def Get_Card(listOfCards=tableDeck, numberOfCards=1):
    # function that returns n cards from the list of cards
    # used to get 4 random cards from the deck the player chose, for his Hand
    # and 4 random cards from the main deck, for the AI hand
    return random.sample(listOfCards, numberOfCards)


def Make_Deck(cardsId):
    # function that returns the dictionary data from the maindeck respective
    # to the list of card IDs sent from the front-end, i.e the cards the player
    # selected for his deck. Basically, makes int 1 become "id": 1, "image": "static/images/card1.png"
    for i in range(0, len(cardsId)):
        for j in range(0, len(mainDeck)):
            if int(cardsId[i]) == mainDeck[j]["id"]:
                cardsId[i] = mainDeck[j]
                break
    return cardsId


def Get_DictFromCardId(cardId):
    # similar as above, but returns the dictionary data for the singular card ID
    for i in range(0, len(mainDeck)):
        if cardId == mainDeck[i]["id"]:
            return mainDeck[i]


def Player_ThrowCard(newCard=None, cardType=0):
    # function called when the user plays a card from his hand
    newCard = int(newCard)
    cardType = int(cardType)

    for i in range(0, len(matchData["PlayerHand"])):
        if matchData["PlayerHand"][i]["id"] == newCard:
            matchData["PlayerHand"].pop(i)
            # pops the card played to the table from the player's hand
            break

    match cardType:
        # if the card is a +/- card, makes its score be either + or -
        # depending on player's choice
        case -1:
            newCard = (newCard - 10) * -1
        case 1:
            newCard -= 10

    if newCard == 17:
        # if the card is the yellow 2/4 or 3/6 cards, makes it invert
        # the values of 2 and 4 or 3 and 6 cards already in the table
        for i in range(0, len(matchData["PlayerTable"])):
            if abs(matchData["PlayerTable"][i]["id"]) == 2 or abs(matchData["PlayerTable"][i]["id"]) == 4:
                matchData["PlayerTable"][i] = Get_DictFromCardId(int(matchData["PlayerTable"][i]["id"]) * -1)
    elif newCard == 18:
        for i in range(0, len(matchData["PlayerTable"])):
            if abs(matchData["PlayerTable"][i]["id"]) == 3 or abs(matchData["PlayerTable"][i]["id"]) == 6:
                matchData["PlayerTable"][i] = Get_DictFromCardId(int(matchData["PlayerTable"][i]["id"]) * -1)

    matchData["PlayerTable"].append(Get_DictFromCardId(newCard))
    matchData["PlayerScore"] = Score_Check(matchData["PlayerTable"])
    # appends the played card to the table and updates the player's score


def Score_Check(cards):
    # function that returns a score for that set of cards

    score = 0
    if cards == None or len(cards) == 0:
        return score
    for i in range(0, len(cards)):
        if cards[i]["id"] <= 10:
            score += cards[i]["id"]
    return score


def Set_PlayerStance(newStance):
    # funciton that updates the player's stance
    # if his score is 20, pazaak
    # if > 20, bust
    # else, makes it whichever button the player clicked, stand or skip
    if matchData["PlayerScore"] == 20:
        matchData["PlayerStance"] = "Pazaak"
    elif matchData["PlayerScore"] > 20:
        matchData["PlayerStance"] = "Bust"
    else:
        matchData["PlayerStance"] = newStance


def Start_Set(whoWon=0):
    # function that starts the set, clearing the table and scores
    # and choosing who will start playing

    matchData["AiScore"] = 0
    matchData["PlayerScore"] = 0
    matchData["AiTable"].clear()
    matchData["PlayerTable"].clear()
    matchData["AiStance"] = "Skip"
    matchData["PlayerStance"] = "Skip"

    if whoWon == 0:
        # if no one won the last set or the match just begun
        # randomizes who will start
        starter = random.randint(1, 2)
        match starter:
            case 1:
                # if the player was chosen, adds a card to his table, updates his score
                # and awaits his input to stand or skip or throw card
                matchData["PlayerTable"].append(Get_Card(tableDeck, 1)[0])
                matchData["PlayerScore"] = Score_Check(matchData["PlayerTable"])
                matchData["message"] += matchData["PlayerName"] + " STARTED THE SET"
            case 2:
                # if the AI was chosen, adds a card to the AI table, updates AI score
                # and skips back to the player turn, adding a card to his table and again
                # awaiting his input
                matchData["AiTable"].append(Get_Card(tableDeck, 1)[0])
                matchData["AiScore"] = Score_Check(matchData["AiTable"])
                matchData["PlayerTable"].append(Get_Card(tableDeck, 1)[0])
                matchData["PlayerScore"] = Score_Check(matchData["PlayerTable"])
                matchData["message"] += matchData["AiName"] + " STARTED THE SET"
    else:
        if whoWon == 1:
            # if the player won the last set, he starts the next
            matchData["PlayerTable"].append(Get_Card(tableDeck, 1)[0])
            matchData["PlayerScore"] = Score_Check(matchData["PlayerTable"])
        elif whoWon == 2:
            # if the AI won the last set, the AI starts the next, does his turn
            # and fowards to the player turn
            matchData["AiTable"].append(Get_Card(tableDeck, 1)[0])
            matchData["AiScore"] = Score_Check(matchData["AiTable"])
            matchData["PlayerTable"].append(Get_Card(tableDeck, 1)[0])
            matchData["PlayerScore"] = Score_Check(matchData["PlayerTable"])


def End_Set():
    # function that establishes the set winner and starts the next set OR ends the match if
    # either player reached 3 set wins

    # goes through the possible combinations of stances and scores
    # at the set end and establishes who won and lost the set
    # and starts the next with the winner playing first, if the set did not tie
    if matchData["PlayerStance"] == matchData["AiStance"]:
        if matchData["PlayerScore"] > 20 or matchData["PlayerScore"] == matchData["AiScore"]:
            matchData["message"] = "TIE - "
            Start_Set(0)
        elif matchData["PlayerScore"] > matchData["AiScore"]:
            matchData["PlayerSetWins"] += 1
            matchData["message"] = matchData["PlayerName"] + " WON THE SET AND STARTS THE NEXT"
            Start_Set(1)
        elif matchData["PlayerScore"] < matchData["AiScore"]:
            matchData["AiSetWins"] += 1
            matchData["message"] = matchData["AiName"] + " WON THE SET AND STARTS THE NEXT"
            Start_Set(2)
    elif matchData["PlayerScore"] > 20 and matchData["AiScore"] <= 20:
        matchData["AiSetWins"] += 1
        matchData["message"] = matchData["AiName"] + " WON THE SET AND STARTS THE NEXT"
        Start_Set(2)
    elif matchData["AiScore"] > 20 and matchData["PlayerScore"] <= 20:
        matchData["PlayerSetWins"] += 1
        matchData["message"] = matchData["PlayerName"] + " WON THE SET AND STARTS THE NEXT"
        Start_Set(1)
    elif matchData["PlayerStance"] == "Pazaak":
        matchData["PlayerSetWins"] += 1
        matchData["message"] = matchData["PlayerName"] + " WON THE SET AND STARTS THE NEXT"
        Start_Set(1)
    elif matchData["AiStance"] == "Pazaak":
        matchData["AiSetWins"] += 1
        matchData["message"] = matchData["AiName"] + " WON THE SET AND STARTS THE NEXT"
        Start_Set(2)

    if (matchData["AiSetWins"] == 3 or matchData["PlayerSetWins"] == 3):
        # if either player reached 3 set wins, ends the match, updates the leaderboard table in users.db
        # and updates the front-end to show the 3 end game button options

        winner = ""
        loser = ""
        if matchData["AiSetWins"] == 3:
            matchData["message"] = matchData["AiName"] + " WON THE MATCH"

            winner = matchData["AiName"]
            loser = matchData["PlayerName"]
        else:
            matchData["message"] = matchData["PlayerName"] + " WON THE MATCH"

            loser = matchData["AiName"]
            winner = matchData["PlayerName"]

        winnerInDb = db.execute("SELECT * FROM leaderboard WHERE username=?", winner)
        loserInDb = db.execute("SELECT * FROM leaderboard WHERE username=?", loser)

        if len(winnerInDb) <= 0:
            db.execute("INSERT INTO leaderboard VALUES(?, ?, ?, ?)", winner, 100, 1, 0)
        else:
            winnerWinPercentage = int(((winnerInDb[0]["victories"] + 1) /
                                       (winnerInDb[0]["victories"] + winnerInDb[0]["losses"] + 1)) * 100)

            db.execute("UPDATE leaderboard SET victories=?, winpercentage=? WHERE username=?",
                       winnerInDb[0]["victories"] + 1, winnerWinPercentage, winner)

        if len(loserInDb) <= 0:
            db.execute("INSERT INTO leaderboard VALUES(?, ?, ?, ?)", loser, 0, 0, 1)
        else:
            loserWinPercentage = int((loserInDb[0]["victories"] /
                                      (loserInDb[0]["victories"] + loserInDb[0]["losses"] + 1)) * 100)

            db.execute("UPDATE leaderboard SET losses=?, winpercentage=? WHERE username=?",
                       loserInDb[0]["losses"] + 1, loserWinPercentage, loser)

        matchData["AiSetWins"] = 0
        matchData["PlayerSetWins"] = 0

        # when GameEnded equals 1 in the ajax success response, the table div is closed
        # and the post-match buttons are shown
        matchData["GameEnded"] = 1


def AI_OneRound():
    # function called when it is the AI's round

    matchData["AiTable"].append(Get_Card(tableDeck, 1)[0])
    matchData["AiScore"] = Score_Check(matchData["AiTable"])
    # appends a card to the AI table and updates his score

    # basic AI decision maker, depending on his score and cards in hand
    # TO BE IMPROVED
    if matchData["AiScore"] == 20:
        matchData["AiStance"] = "Pazaak"
    elif matchData["AiScore"] > 20:
        if len(matchData["AiHand"]) <= 0:
            matchData["AiStance"] = "Bust"
        else:
            for i in range(0, len(matchData["AiHand"])):
                if int(matchData["AiHand"][i]["id"]) < 0:
                    if (matchData["AiScore"] + int(matchData["AiHand"][i]["id"])) == 20:
                        matchData["AiTable"].append(matchData["AiHand"][i])
                        matchData["AiHand"].pop(i)
                        matchData["AiStance"] = "Pazaak"
                        matchData["AiScore"] = Score_Check(matchData["AiTable"])
                        return

            if not matchData["AiStance"] == "Pazaak":
                for i in range(0, len(matchData["AiHand"])):
                    if int(matchData["AiHand"][i]["id"]) < 0:
                        if (matchData["AiScore"] + int(matchData["AiHand"][i]["id"])) < 20:
                            matchData["AiTable"].append(matchData["AiHand"][i])
                            matchData["AiHand"].pop(i)
                            matchData["AiStance"] = "Stand"
                            matchData["AiScore"] = Score_Check(matchData["AiTable"])
                            return
            matchData["AiStance"] = "Bust"

    elif matchData["AiScore"] < 20:
        if matchData["PlayerStance"] == "Bust":
            matchData["AiStance"] = "Stand"
        elif matchData["PlayerStance"] == "Stand":
            if matchData["PlayerScore"] < matchData["AiScore"]:
                matchData["AiStance"] = "Stand"
            elif matchData["PlayerScore"] == matchData["AiScore"]:
                if matchData["AiScore"] > 14:
                    if len(matchData["AiHand"]) > 0:
                        for i in range(0, len(matchData["AiHand"])):
                            if int(matchData["AiHand"][i]["id"]) <= 10:
                                if (matchData["AiScore"] + int(matchData["AiHand"][i]["id"])) <= 20 and matchData["AiScore"] + int(matchData["AiHand"][i]["id"]) > matchData["PlayerScore"]:
                                    matchData["AiTable"].append(matchData["AiHand"][i])
                                    matchData["AiHand"].pop(i)
                                    matchData["AiScore"] = Score_Check(matchData["AiTable"])
                                    break
                        if matchData["AiScore"] == 20:
                            matchData["AiStance"] = "Pazaak"
                        elif matchData["AiScore"] >= 18:
                            matchData["AiStance"] = "Stand"
                    else:
                        matchData["AiStance"] = "Skip"
                else:
                    matchData["AiStance"] = "Skip"


def Clean_Table():
    # function that makes sure the table is clean
    # and chooses the player and AI hands, as well as AI opponent name

    global playerDeck
    matchData["PlayerHand"] = Get_Card(playerDeck, 4)
    matchData["AiHand"] = Get_Card(mainDeck, 4)
    matchData["AiName"] = random.choice(aiNames)
    matchData["AiScore"] = 0
    matchData["PlayerScore"] = 0
    matchData["AiTable"].clear()
    matchData["PlayerTable"].clear()
    matchData["AiStance"] = "Skip"
    matchData["PlayerStance"] = "Skip"
    matchData["AiSetWins"] = 0
    matchData["PlayerSetWins"] = 0
    matchData["message"] = ""
    matchData["GameEnded"] = 0


@app.route("/", methods=["GET"])
def index():
    # Main page that displays the leaderboard
    # Play button goes to /chooseDeck
    leaderboard = db.execute("SELECT username, winpercentage, victories, losses FROM leaderboard LIMIT 10")
    leaderboard.sort(key=operator.itemgetter("winpercentage", "victories"), reverse=True)
    return render_template("index.html", leaderboard=leaderboard)


@app.route("/chooseDeck", methods=["GET", "POST"])
def chooseDeck():

    if request.method == "GET":
        return redirect("/")
    else:
        if not request.form.get("playername"):
            # if player did not input a name, returns to the main page
            return redirect("/")

        # else, adds the name to the match data, and returns the chooseDeck.html
        # so that the player can choose the 10 cards for his deck
        matchData["PlayerName"] = request.form.get("playername")
        return render_template("chooseDeck.html", mainDeck=mainDeck)


@app.route("/chooseDeckAgain", methods=["GET", "POST"])
def chooseDeckAgain():
    if request.method == "GET":
        return redirect("/")
    else:
        # after a match ended, if the player clicks the choose new deck button
        # returns him to the chooseDeck.html
        return render_template("chooseDeck.html", mainDeck=mainDeck)


@app.route("/play", methods=["GET", "POST"])
def play():

    if request.method == "GET":
        return redirect("/")
    else:
        # route started once the player hits the play button in chooseDeck.html
        global playerDeck

        playerDeck = Make_Deck(request.form.getlist("cards"))
        Clean_Table()
        # makes sure the table is clean and transforms the card IDs
        # into their respective dictionaries, with the Make_Deck function

        Start_Set(0)
        # chooses who will start the set and updates the table correspondingly
        # and renders the play.html page with the matchData as it stands
        return render_template("play.html", matchData=matchData)


@app.route("/playAgain", methods=["POST"])
def playAgain():

    # after a match ended, if the player clicks the play again button
    # returns him to the play.html with a clean table and then a new started set, with new opponent

    Clean_Table()
    Start_Set(0)

    return render_template("play.html", matchData=matchData)


@app.route("/playCard", methods=["POST"])
def playCard():

    # ajax request when the player plays a card from his hand to the table

    if request.method == "POST":
        Player_ThrowCard(request.form.get("Played Card"), request.form.get("Card Type"))
        # throws the respective card and updates the table, score and player hand

    # returns the matchData to the ajax request, in order to update the play.html plage seamlessly
    return jsonify(matchData)


@app.route("/switchTurn", methods=["POST"])
def switchTurn():

    # ajax request when the player ends his turn

    if request.method == "POST":
        Set_PlayerStance(request.form.get("Player Stance"))
        # sets the player stance, depending on his score (pazaak or bust)
        # and which button he clicked (skip or stand)

        if (matchData["PlayerStance"] == "Skip"):
            # if the player did not stand, pazaak or bust, does ONE ai round
            if (matchData["AiStance"] == "Skip"):
                AI_OneRound()

            # and returns to the player turn, adding a card to his table and updating his score
            # and awaiting his decision again
            matchData["PlayerTable"].append(Get_Card(tableDeck, 1)[0])
            matchData["PlayerScore"] = Score_Check(matchData["PlayerTable"])

        else:
            # if the player will not play further this set

            if matchData["AiStance"] == "Skip":
                # if the AI is still playing further this set, does AI turns again and again
                # UNTIL AI either busts, pazaak, or stands
                while matchData["AiStance"] == "Skip":
                    AI_OneRound()

            # ends the set when both stood, pazaak or busted
            End_Set()

    # returns the matchData to the ajax request, in order to update the play.html page seamlessly
    return jsonify(matchData)

