const session_id = document.body.dataset.session_id;
const csrf_token = document.getElementById('csrf_token').value;

const successAudioUrl = '/static/sounds/success-sound-effect.mp3';
const successAudio = new Audio(successAudioUrl);
successAudio.volume = 1;
successAudio.load();
const failAudioUrl = '/static/sounds/wrong-sound-effect.mp3';
const failAudio = new Audio(failAudioUrl);
failAudio.volume = 1;
failAudio.load();
const eatingAudioUrl = '/static/sounds/eating-snake-sound-effect.mp3';
const eatingAudio = new Audio(eatingAudioUrl);
eatingAudio.volume = 1;
eatingAudio.load();
const hitAudioUrl = '/static/sounds/hit-snake-sound-effect.mp3';
const hitAudio = new Audio(hitAudioUrl);
hitAudio.volume = 1;
hitAudio.load();

const canvas = document.querySelector("canvas");
const context = canvas.getContext('2d');


const animXp = document.getElementById('animation-xp');
const xpWin = document.getElementById('xpnotif');
const frWord = document.getElementById('frensh-word');

let box = 32

const pressMessage = document.getElementById('press-message');
const score = document.getElementById('xp')
var xpTotal = 0

score.innerHTML = xpTotal + ' Xp'

var snake = [{ x: 7 * box, y: 7 * box }];

snake[0] = { x: 7 * box, y: 7 * box }

var word = [] // word is the list used to check the letter eaten by the user

var wordStyle = [] // wordStyle is the list used to print the word on the window


var nbrOfRock = 0
const totalLetterArea = document.getElementById('word');

const image = document.getElementById('source');
const headUp = document.getElementById('up');
const headDown = document.getElementById('down');
const headLeft = document.getElementById('left');
const headRight = document.getElementById('right');

nbrLettreTrouve = 0;

/**
 * 
 * This function is used to update the English word when the user eat letter
 * 
 * @function updateWord
 * 
 * @returns {void} - The result of the function
 */
function updateWord() {
    totalLetterArea.innerHTML = '';
    wordStyle.forEach((element, index) => {
        if (element != 'rock') {

            // Add an space if the English word is compound word
            for (let i = 0; i < space_pos.length; i++) {
                if (index == space_pos[i]) {
                    totalLetterArea.innerHTML += `<span class="space"></span>`
                }
            }

            // Print the letter if it is found
            if (index < nbrLettreTrouve) {
                totalLetterArea.innerHTML += `<span class="letter">${element}</span>`
            } else {
                totalLetterArea.innerHTML += `<span class="letter"></span>`
            };
        }
    });
}

var isEventListener = false
var letterPositions = [{ x: 0, y: 0 }];
var co2python = []
var space_pos = []

/**
 * 
 * This function is used to get the position of each letter on the snake grid
 * 
 * @function getPosition
 * 
 * @returns {void} - The result of the function
 */
async function getPosition() {
    wordStyle = []
    // get the position in python
    r = await fetch(`/dashboard/games/snake/${session_id}/getWord`)
    response = await r.json();
    console.log(response.result.coo)

    // Get the space position if the word is a compound word
    space_pos = response.result.space_positions

    // Get the coordinates of the letter (and the rock)
    letterPositions = response.result.coo

    // Get the translation of the word
    frWord.innerHTML = response.result.frensh

    // add the letter and the rock in word and wordStyle
    for (let i = 0; i < letterPositions.length; i++) {
        word.push(letterPositions[i].letter);
        wordStyle.push(letterPositions[i].letter)
    }
    // Count the number of rock
    for (let index = 0; index < word.length; index++) {
        if (word[index] == 'rock') {
            nbrOfRock++;
        }
    }
    updateWord()
    isEventListener = true
}


let d; // d is the direction of the snake

var snakeX = snake[0].x;
var snakeY = snake[0].y;

var startX = 0; // Start position


// these three eventListener is used to get the direction choosen on smartphone or tablet
window.addEventListener("touchstart", function(evt) {
    // Recovers "touches" performed
    var touches = evt.changedTouches[0];
    startX = touches.pageX;
    startY = touches.pageY;
    betweenX = 0;
    betweenX = 0;
}, false);
window.addEventListener("touchmove", function(evt) {
    // Limits edge effects with touch...
    evt.stopPropagation();
}, false);
window.addEventListener("touchend", function mobiletouch(evt) {
    var touches = evt.changedTouches[0];

    // Get the difference in width and height between the touch and the release of the finger
    var betweenX = touches.pageX - startX;
    var betweenY = touches.pageY - startY;

    var current_d = {}

    // Check if the direction is Right, Left, Up or Down
    if (Math.abs(betweenX) > 15 || Math.abs(betweenY) > 15) {
        // Provides a keyCode for imitating keyboard pressure
        if (Math.abs(betweenX) >= Math.abs(betweenY) + 10) {
            if (betweenX > 0 && d != 'LEFT') current_d = {keyCode: 39}
            else{
                current_d = {keyCode: 37}
            }
        } else {
            if (betweenY > 0 && d != 'UP') current_d = {keyCode: 40}
            else {
                current_d = {keyCode: 38}
            }
        }

        // Set the new direction
        direction(current_d)
    }
}, false);


document.addEventListener('keydown', (e) => {
    direction(e)
});


/**
 * 
 * This function is used to change the direction of the snake
 * 
 * @function getPosition
 * @param {Event} event the new direction
 * 
 * @returns {void} - The result of the function
 */
async function direction(event) {
    // Records the snake's current direction
    var old_d = d
    var key = event.keyCode;
    // Set the new direction
    if (key == 37 && d != "RIGHT") {
        var d1 = "LEFT";
    }
    if (key == 39 && d != "LEFT") {
        var d1 = "RIGHT";
    }
    if (key == 38 && d != "DOWN") {
        var d1 = "UP";
    }
    if (key == 40 && d != "UP") {
        var d1 = "DOWN";
    }
    // Stop the function if the direction didn't change
    if (d == d1) {
        return
    }
    
    else if ( d1 == undefined) {
        d = d;
    } 
    
    // Change the direction
    else{
        d = d1
    }
    if( d != old_d){

        // Set up the new snake head if direction is Left
        if (old_d == 'LEFT') {
            
            // Stop the function if the snake head is perfectly in a collumn
            if (snakeX % 32 == 0) {
                return
            } else if (d != 'RIGHT') {
                // Wait 70ms if the snake is too far from the next column to make the movement smoother
                if (snakeX % 32 > 16) {
                    var temp_d = d
                    d = old_d
                    await new Promise(resolve => setTimeout(resolve, 70))
                    var changeHead = {
                        x: snakeX - snakeX % 32,
                        y: snakeY
                        };
                    d = temp_d
                } 
                
                // Set up the new head in the next column
                else {
                    var changeHead = {
                        x: snakeX - snakeX % 32,
                        y: snakeY
                        };
                }
            }
        }

        // Set up the new snake head if direction is Right
        else if (old_d == 'RIGHT') {
            // Stop the function if the snake head is perfectly in a collumn
            if (snakeX % 32 == 0) {
                return
            } else if (d != 'LEFT') {
                // Wait 70ms if the snake is too far from the next column to make the movement smoother
                if (snakeX % 32 < 16) {
                    var temp_d = d
                    d = old_d
                    await new Promise(resolve => setTimeout(resolve, 70))
                    var changeHead = {
                        x: snakeX - snakeX % 32 + 32,
                        y: snakeY
                        };
                    d = temp_d
                } 
                
                // Set up the new head in the next column
                else {
                    var changeHead = {
                        x: snakeX - snakeX % 32 + 32,
                        y: snakeY
                        };
                }
            }
        }

        // Set up the new snake head if direction is Up
        else if (old_d == 'UP') {
            // Stop the function if the snake head is perfectly in a line
            if (snakeY % 32 == 0) {
                return
            } else if(d != 'DOWN') {

                // Wait 70ms if the snake is too far from the next line to make the movement smoother
                if (snakeY % 32 > 16) {
                    var temp_d = d
                    d = old_d
                    await new Promise(resolve => setTimeout(resolve, 70))
                    var changeHead = {
                        x: snakeX,
                        y: snakeY - snakeY % 32
                        };
                    d = temp_d
                } 
                
                // Set up the new head in the next column
                else{
                    var changeHead = {
                        x: snakeX,
                        y: snakeY - snakeY % 32
                        };
                }
                
            }
        }

        // Set up the new snake head if direction is Down
        else if (old_d == 'DOWN') {
            // Stop the function if the snake head is perfectly in a line
            if (snakeY % 32 == 0) {
                return
            } else if (d != 'UP') {

                // Wait 70ms if the snake is too far from the next line to make the movement smoother
                if (snakeY % 32 < 16) {
                    var temp_d = d
                    d = old_d
                    await new Promise(resolve => setTimeout(resolve, 70))
                    var changeHead = {
                        x: snakeX,
                        y: snakeY - snakeY % 32 + 32
                        };
                    d = temp_d
                } 
                
                // Set up the new head in the next column
                else {
                    var changeHead = {
                    x: snakeX,
                    y: snakeY - snakeY % 32 + 32
                    };
                }
            }
        }

        // Slightly teleports the snake to the next colony/line if necessary
        if (changeHead != undefined) {
            draw(changeHead);
        }
    }
}
var fin = 0


/**
 * 
 * This function is used to draw the canvas
 * 
 * @function draw
 * @param {null | Object} event the new direction
 * 
 * @returns {void} - The result of the function
 */
function draw(changeDirection) {
    snakeX = snake[0].x;
    snakeY = snake[0].y;
    if (isEventListener == true) {
        // Clear the canvas
        context.clearRect(0, 0, 504, 504)

        if (d != undefined) {
            pressMessage.style.display = 'none'
        } else {
            pressMessage.style.display = 'block'
        }

        // Draw the background of the grid
        context.fillStyle = "#766153";
        let background_x = 0
        let background_y = 0

        // Alternates between the two background colors
        for (let i = 0; i < 15; i++) {
            for (let j = 0; j < 15; j++) {
                context.fillRect(background_x, background_y, 32, 32)
                if (context.fillStyle == '#635146') {
                    context.fillStyle = '#766153'
                } else if (context.fillStyle == '#766153') {
                    context.fillStyle = '#635146'
                }
                background_x += 32

            }
            background_x = 0
            background_y += 32
        }


        var letterIndex = 0;
        // Add letter and rocks on the grid
        letterPositions.forEach(e => {
            if (e.letter == 'rock') {
                context.drawImage(image, letterPositions[letterIndex].x - 9, letterPositions[letterIndex].y - 25, 30, 28)
            } else {
                context.font = "30px Bangers";
                context.lineWidth = 2;
                context.fillStyle = "#ADAE82";
                context.fillText(e.letter, letterPositions[letterIndex].x - 2, letterPositions[letterIndex].y);
            }
            letterIndex++;
        });

        // Draw the snake
        for (let i = 0; i < snake.length; i++) {
            if (i == 0) {
                i = i
            } 
            
            // Draw the body of the snake (16 circle for one case)
            else {
                context.fillStyle = "#ADAE82";
                context.beginPath();
                context.arc(snake[i].x + 16, snake[i].y + 16, 16, 0, 2 * Math.PI);
                context.fill();
            }

            var e = 16 * (nbrLettreTrouve + 1) // The number of circle which composed the snake

            // complete the snake with 1 to have good longer of snake
            if (snake.length != e + 1 && d != undefined) {
                snake.push(1)
            }

            // Set the head on right at the begining of game
            if (d == undefined) {
                context.drawImage(headRight, snake[0].x, snake[0].y - 10, 36, 50)
            }
        }
        
        var letterFind = false
        var l = false
        for (let i = 0; i < letterPositions.length; i++) {
            // Check if the snake is on a letter or a rock
            if (snakeX == letterPositions[i].x - 9 && snakeY == letterPositions[i].y - 28) {
                // Check if the letter eat is the good letter
                if (letterPositions[i].letter != word[0]) {
                    l = true
                } else {
                    // Add he coordinate to the list co2python in order to verifie the coordinates at the end of the word
                    co2python.push({ x: letterPositions[i].x, y: letterPositions[i].y })
                    letterFind = true;
                    word.shift();
                    letterPositions.splice(i, 1);
                    nbrLettreTrouve++;
                    eatingAudio.play();
                    updateWord();
                }
            }
        }
        // Moves and draws the snake's head according to direction
        if (d == "LEFT"){
            snakeX -= Math.floor(box / 16)
            context.drawImage(headLeft, snake[0].x - 10, snake[0].y - 10, 36, 51)
        }
        if (d == "RIGHT") {
            snakeX += Math.floor(box / 16)
            context.drawImage(headRight, snake[0].x, snake[0].y - 9, 38, 51)
        };
        if (d == "UP"){
            snakeY -= Math.floor(box / 16);
            context.drawImage(headUp, snake[0].x - 9, snake[0].y - 10, 51, 36)
        }
        if (d == "DOWN") {
            snakeY += Math.floor(box / 16)
            context.drawImage(headDown, snake[0].x - 10, snake[0].y + 1, 51, 36)
        };
        if (!letterFind) {
            snake.pop()
        }

        // Set up the new head of the snake
        if (changeDirection == null){
            var newHead = {
                x: snakeX,
                y: snakeY
                };
        } else {
            var newHead = changeDirection;
        }

        // Check if the snake comes out of the grid, eat himself or the badletter/rock
        if (snakeX < -2 || snakeY < -2 || snakeX > 14 * box || snakeY > 14 * box || collision(newHead, snake) || l) {
            if (fin == 0) {
                clearInterval(game)
                hitAudio.play()
                checkingCoo()
                fin += 1
            }
        };


        // Finish the game if the word is completed
        if ((word.length - nbrOfRock) == 0) {
            if (fin == 0) {
                clearInterval(game)
                checkingCoo()
                fin += 1
            }
        }

        // Add the new head to the snake
        snake.unshift(newHead);
    }
}

/**
 * 
 * This function is used to draw the canvas
 * 
 * @function checkingCoo
 * 
 * @returns {void} - The result of the function
 */
async function checkingCoo() {
    // Check the coordinates Javascripts with the coordinates in python
    r = await fetch(`/dashboard/games/snake/${session_id}/check_coo`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrf_token
        },
        body: JSON.stringify({
            coo: co2python
        })
    })
    response = await r.json()

    if (response.code == 500) {
        window.location.href = '/dashboard/errors/500';
    }

    xpTotal = response.result.xpTot
    score.innerHTML = xpTotal + ' Xp'

    // end the game if there are no more word left
    if (response.message == 'Le jeu est terminé!') {
        end_game(response.result.xp, response.result.time, response.result.lost_lives)
    } else if (response.message == 'ok') {
        animXp.style.animation = 'Xpanim 1s ease-in-out forwards';
        word = []
        var xp = response.result.xp
        xpWin.innerHTML = `+${xp}`
        setTimeout(() => {
            // Reset all params
            isEventListener = false
            snake = [{ x: 7 * box, y: 7 * box }]
            nbrLettreTrouve = 0
            co2python = []
            snakeX = snake[0].x;
            snakeY = snake[0].y;
            nbrOfRock = 0
            animXp.style.animation = 'disapear 0.5s ease-in-out forwards';

            // Get the position of the next word
            getPosition()
            d = undefined

            // Restart the game with the new word
            game = setInterval(function () {
                draw(null);
            }, 14)
            fin = 0
        }, 1500);
    }
}

/**
 * 
 * This function is used to check if the snake eat himself
 * 
 * @function timer
 * @param {Object} head - Snake head coordinates
 * @param {Object} array - the snake's body
 * 
 * @returns {void} - The result of the function
 */
function collision(head, array) {
    for (let g = 0; g < array.length; g++) {
        // Check if the coordinates of the head is the same as body coordinates
        if (head.x == array[g].x && head.y == array[g].y) {
            return true;
        }
    }
    return false;
}

setTimeout(() => {
    getPosition();
}, 500);
var game = setInterval(function () {
    draw(null);
}, 14)




/**
 * 
 * This function is used to display the end pop-up
 * 
 * @function timer
 * @param {Event} event - The event that triggered the function
 * 
 * @returns {void} - The result of the function
 */
var timer = setInterval(async() => {
    // Get the time element
    const time = document.getElementById('time');
    // Decrease the time by 1
    time.innerHTML = parseInt(time.innerHTML) - 1;

    // If the timer is over
    if (time.textContent == 0) {
        clearInterval(timer);
        try {
            // Check the status of the game
            const response = await fetch(`/dashboard/games/snake/${session_id}/check_status`);
            const data = await response.json();
            // If the game is over
            if (data.code == 201) {
                // End the game
                end_game(data.result.xp, data.result.time, data.result.lost_lives);
            }
        } catch (error) {
            window.location.href = '/dashboard/errors/500';
        }
    }
}, 1000);

timer;