function showhidebuttons(e) {
    // function called when the player clicks a card in his Hand

    cardClicked = e.srcElement;
    // gets the card clicked
    if (cardClicked.value >= 11 && cardClicked.value <= 16)
    {
        // if its a special +/- card, hides the normal Play Card button, and shows
        // the Play Card as Positive/Negative buttons
        document.getElementById("mainButton").style.display = "none";
        document.getElementById("buttonPositive").style.display = "initial";
        document.getElementById("buttonNegative").style.display = "initial";
    }
    else
    {
        // if its a regular card, hides the special buttons and shows the regular Play Card Button
        document.getElementById("mainButton").style.display = "initial";
        document.getElementById("buttonPositive").style.display = "none";
        document.getElementById("buttonNegative").style.display = "none";
    }

    // toggles on the Play Card Buttons visibility, so that their display changed above can hide or show them
    document.getElementById("mainButton").style.visibility = "visible";
    document.getElementById("buttonPositive").style.visibility = "visible";
    document.getElementById("buttonNegative").style.visibility = "visible";

    // removes the selected outline from all other cards in the player's Hand
    document.querySelectorAll("label[name='cardLabels']").forEach(function(item) {
        item.classList.remove('card-checkbox-checked');
      });

    // adds the selected outline to the card clicked this time
    document.querySelector("label[for='" + CSS.escape(cardClicked.value) + "']").classList.add('card-checkbox-checked');
}


function playCard(posOrNeg=0){
    // function called when the user clicks a Play Card button

    document.getElementById("mainButton").style.visibility = "hidden";
    document.getElementById("buttonPositive").style.visibility = "hidden";
    document.getElementById("buttonNegative").style.visibility = "hidden";
    // hides the buttons and sends an ajax request to the server with the following info:
    // ID of the card that was selected at the time of clicking the Play Card button
    // and the card type - if it was a special +/- thrown as negative (identified by the -1 posOrNeg) or positive (1)
    // or just 0, a regular card

    $.ajax({
        type: "POST",
        url: "/playCard",
        data: {"Played Card": document.querySelector("input[name='cards']:checked").value, "Card Type": posOrNeg},
        success: function(response) {
            // the response from the ajax request
            // updates the player score with his new score
            $('#playerScore').text(response.PlayerScore);

            // updates the player's table and Hand cards
            let handstr = '';
            response.PlayerHand.forEach(function(element) {
                handstr += '<div class="col-md-1 pad"><input type="radio" style="opacity:0" name="cards" id="' + element["id"] + '"onclick="showhidebuttons(event)" value="' + element["id"] + '"><label name="cardLabels" class="card-checkbox" for="' + element["id"] + '"><img class="img-responsive" src="' + element["image"] + '"alt="#"></label></div>';
            })
            document.getElementById('playerHand').innerHTML = handstr;

            let tablestr = '';
            response.PlayerTable.forEach(function(element) {
                tablestr += '<img src="' + element["image"] + '"alt="#" width="70" height="96">';
            })
            document.getElementById('playerTable').innerHTML = tablestr;
        }
    })
}


function endTurn(playerStance){
    // function called when the user clicks the skip or stand buttons
    // ajax requet that sends to the server the player's stance: stand or skip
    $.ajax({
        type: "POST",
        url: "/switchTurn",
        data: {"Player Stance": playerStance},
        success: function(response) {

        // the response from the ajax request
        // updates the entire table with the new match data
        $('#aiScore').text(response.AiScore);
        $('#aiStance').text(response.AiStance);

        $('#playerScore').text(response.PlayerScore);
        $('#playerStance').text(response.playerStance);

        // makes the AI and Player Stance text get its respective style, as in, bust is written in red
        switch (response.playerStance)
        {
            case "Pazaak":
                $('#playerStance').attr("class", "pazaak");
                break;
            case "Stand":
                $('#playerStance').attr("class", "stand");
                break;
            case "Skip":
                $('#playerStance').attr("class", "skip");
                break;
            case "Bust":
                $('#playerStance').attr("class", "bust");
                break;
        }

        switch (response.AiStance)
        {
            case "Pazaak":
                $('#aiStance').attr("class", "pazaak");
                break;
            case "Stand":
                $('#aiStance').attr("class", "stand");
                break;
            case "Skip":
                $('#aiStance').attr("class", "skip");
                break;
            case "Bust":
                $('#aiStance').attr("class", "bust");
                break;
        }

        // makes the set counter image update to the number of set wins the respective player has
        document.getElementById('aiSetWins').src = "static/images/roundwins" + response.AiSetWins + ".png"
        document.getElementById('playerSetWins').src = "static/images/roundwins" + response.PlayerSetWins + ".png"

        // updates the tables and Hands of both players
        let aiHandStr = '';
        response.AiHand.forEach(function(element) {
            aiHandStr += '<div class="col-md-1 pad"><img class="img-responsive" src="static/images/cardhidden.png" alt="#"></div>';
        })
        document.getElementById('aiHand').innerHTML = aiHandStr;

        let aiTableStr = '';
        response.AiTable.forEach(function(element) {
            aiTableStr += '<img src="' + element["image"] + '"alt="#" width="70" height="96">';
        })
        document.getElementById('aiTable').innerHTML = aiTableStr;

        let tablestr = '';
        response.PlayerTable.forEach(function(element) {
            tablestr += '<img src="' + element["image"] + '"alt="#" width="70" height="96">';
        })
        document.getElementById('playerTable').innerHTML = tablestr;

        // updates the header with the results of the set
        $("#message").text(response.message);

        if (response.GameEnded == 1)
        {
            // if the game ended, hides the entire table and shows the post game buttons
            document.getElementById("fullTable").style.visibility = "hidden";
            document.getElementById("fullTable").style.display = "none";
            document.getElementById("playAgain").style.display = "initial";
            document.getElementById("newDeck").style.display = "initial";
            document.getElementById("home").style.display = "initial";
        }
        }
    })
}