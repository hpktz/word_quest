const session_id = document.body.dataset.session_id;
const csrf_token = document.getElementById('csrf_token').value;

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
var word = []
var wordStyle = []
var nbrOfRock = 0
const totalLetterArea = document.getElementById('word');

const image = document.getElementById('source');
const headUp = document.getElementById('up');
const headDown = document.getElementById('down');
const headLeft = document.getElementById('left');
const headRight = document.getElementById('right');

nbrLettreTrouve = 0;

function updateWord() {
    totalLetterArea.innerHTML = '';
    wordStyle.forEach((element, index) => {
        if (element != 'rock') {
            for (let i = 0; i < space_pos.length; i++) {
                if (index == space_pos[i]) {
                    totalLetterArea.innerHTML += `<span class="space"></span>`
                }
                
            }
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
    // alreadyPos = false
async function getPosition() {
    console.log("cool")
    wordStyle = []
    r = await fetch(`/dashboard/games/snake/${session_id}/getWord`)
    response = await r.json();
    space_pos = response.result.space_positions
    letterPositions = response.result.coo
    frWord.innerHTML = response.result.frensh
    for (let i = 0; i < letterPositions.length; i++) {
        word.push(letterPositions[i].letter);
        wordStyle.push(letterPositions[i].letter)
    }
    for (let index = 0; index < word.length; index++) {
        if (word[index] == 'rock') {
            nbrOfRock++;
        }
    }
    isEventListener = true
}

let d;

var snakeX = snake[0].x;
var snakeY = snake[0].y;

var startX = 0; // Position de départ
var distance = 100; // 100 px de swipe pour afficher le menu

window.addEventListener("touchstart", function(evt) {
    // Récupère les "touches" effectuées
    var touches = evt.changedTouches[0];
    startX = touches.pageX;
    startY = touches.pageY;
    betweenX = 0;
    betweenX = 0;
}, false);
window.addEventListener("touchmove", function(evt) {
    // Limite les effets de bord avec le tactile...
    evt.stopPropagation();
}, false);
window.addEventListener("touchend", function mobiletouch(evt) {
    var touches = evt.changedTouches[0];
    var betweenX = touches.pageX - startX;
    var betweenY = touches.pageY - startY;
    var current_d = {}
    if (Math.abs(betweenX) > 15 || Math.abs(betweenY) > 15) {
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
        direction(current_d)
    }
}, false);
document.addEventListener('keydown', (e) => {
    direction(e)
});

async function direction(event) {
    var old_d = d
    var key = event.keyCode;
    if (key == 37 && d != "RIGHT") {
        var d1 = "LEFT";;
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
    console.log(d1)
    if (d == d1) {
        return
    }else if ( d1 == undefined) {
        d = d;
    } else{
        d = d1
    }
    if( d != old_d){
        if (old_d == 'LEFT') {
            console.log(d)
            if (snakeX % 32 == 0) {
                return
            } else if (d != 'RIGHT') {
                if (snakeX % 32 > 16) {
                    var temp_d = d
                    d = old_d
                    await new Promise(resolve => setTimeout(resolve, 70))
                    var changeHead = {
                        x: snakeX - snakeX % 32,
                        y: snakeY
                        };
                    d = temp_d
                } else {
                    var changeHead = {
                        x: snakeX - snakeX % 32,
                        y: snakeY
                        };
                }
            }
        }
        else if (old_d == 'RIGHT') {
            console.log(d)
            if (snakeX % 32 == 0) {
                return
            } else if (d != 'LEFT') {
                if (snakeX % 32 < 16) {
                    var temp_d = d
                    d = old_d
                    await new Promise(resolve => setTimeout(resolve, 70))
                    var changeHead = {
                        x: snakeX - snakeX % 32 + 32,
                        y: snakeY
                        };
                    d = temp_d
                } else {
                    var changeHead = {
                        x: snakeX - snakeX % 32 + 32,
                        y: snakeY
                        };
                }
            }
        }
        else if (old_d == 'UP') {
            if (snakeY % 32 == 0) {
                return
            } else if(d != 'DOWN') {
                if (snakeY % 32 > 16) {
                    var temp_d = d
                    d = old_d
                    await new Promise(resolve => setTimeout(resolve, 70))
                    var changeHead = {
                        x: snakeX,
                        y: snakeY - snakeY % 32
                        };
                    d = temp_d
                } else{
                    var changeHead = {
                        x: snakeX,
                        y: snakeY - snakeY % 32
                        };
                }
                
            }
        }
        else if (old_d == 'DOWN') {
            if (snakeY % 32 == 0) {
                return
            } else if (d != 'UP') {
                if (snakeY % 32 < 16) {
                    var temp_d = d
                    d = old_d
                    await new Promise(resolve => setTimeout(resolve, 70))
                    var changeHead = {
                        x: snakeX,
                        y: snakeY - snakeY % 32 + 32
                        };
                    d = temp_d
                } else {
                    var changeHead = {
                    x: snakeX,
                    y: snakeY - snakeY % 32 + 32
                    };
                }
            }
        }
        if (changeHead != undefined) {
            draw(changeHead);
        }
    }
}
var fin = 0

function draw(changeDirection) {
    snakeX = snake[0].x;
    snakeY = snake[0].y;
    // let cool = setInterval(() => {
    if (isEventListener == true) {
        // clearInterval(cool)
        context.clearRect(0, 0, 504, 504)
        if (d != undefined) {
            pressMessage.style.display = 'none'
        } else {
            pressMessage.style.display = 'block'
        }
        context.fillStyle = "#766153";
        let background_x = 0
        let background_y = 0
        for (let i = 0; i < 15; i++) {
            for (let j = 0; j < 15; j++) {
                context.fillRect(background_x, background_y, 32, 32)
                    // context.beginPath()
                    // context.lineWidth = "10"
                    // context.strokeStyle = "brown"
                    // context.rect(background_x,background_y,55,55)
                    // context.stroke()
                if (context.fillStyle == '#cca48a') {
                    context.fillStyle = '#766153'
                } else if (context.fillStyle == '#766153') {
                    context.fillStyle = '#cca48a'
                }
                background_x += 32
                    // if(context.fillStyle == "#c1c286"){
                    //     context.fillStyle = "#84855c"
                    // } else if (context.fillStyle == '#84855c') {
                    //     context.fillStyle = "#c1c286"
                    // }

            }
            background_x = 0
            background_y += 32
        }
        var letterIndex = 0;
        letterPositions.forEach(e => {
            if (e.letter == 'rock') {
                context.drawImage(image, letterPositions[letterIndex].x - 10, letterPositions[letterIndex].y - 22, 25, 18)
            } else {
                context.fillStyle = "#373D20";
                context.font = "30px League Spartan";
                context.fillText(e.letter, letterPositions[letterIndex].x, letterPositions[letterIndex].y);
            }
            letterIndex++;
        });
        for (let i = 0; i < snake.length; i++) {
            if (i == 0) {
                // context.fillStyle = "#BCBD8B";
                // context.beginPath();
                // context.lineWidth = "2";
                // context.arc(snake[i].x + 16, snake[i].y + 16, 17, 0, 2 * Math.PI)
                // context.fill();
                i = i
            } else {
                context.fillStyle = "#ADAE82"
                context.fillRect(snake[i].x, snake[i].y, box, box);
            }
            var e = 16 * (nbrLettreTrouve + 1)
            if (snake.length != e + 1 && d != undefined) {
                snake.push(1)
            }

            // context.fillStyle = "#BCBD8B";
            // context.beginPath();
            // context.lineWidth = "2";
            // context.arc(snake[0].x + 16, snake[0].y + 16, 17, 0, 2 * Math.PI)
            // context.fill();
            // if (d == 'RIGHT') {
            //     context.drawImage(headRight, snake[0].x - 7, snake[0].y - 7, 46, 46)
            // }
            // if (d == 'LEFT') {
            //     context.drawImage(headLEFT, snake[0].x - 7, snake[0].y - 7, 46, 46)
            // }
            // if (d == 'RIGHT') {
            //     context.drawImage(headLEFT, snake[0].x - 7, snake[0].y - 7, 46, 46)
            // }
            // if (d == 'RIGHT') {
            //     context.drawImage(headRight, snake[0].x - 7, snake[0].y - 7, 46, 46)
            // }
            if (d == undefined) {
                context.drawImage(headRight, snake[0].x, snake[0].y - 10, 36, 50)
            }
        }
        var letterFind = false
        var l = false
        for (let i = 0; i < letterPositions.length; i++) {
            if (snakeX == letterPositions[i].x - 9 && snakeY == letterPositions[i].y - 27) {
                if (letterPositions[i].letter != word[0]) {
                    l = true
                } else {
                    if (co2python[0] == 'vide') {
                        co2python.shift()
                    }
                    co2python.push({ x: letterPositions[i].x, y: letterPositions[i].y })
                    letterFind = true;
                    word.shift();
                    letterPositions.splice(i, 1);
                    nbrLettreTrouve++;
                }
            }
        }
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
        if (changeDirection == 'pas de changement'){
            var newHead = {
                x: snakeX,
                y: snakeY
                };
        } else {
            var newHead = changeDirection;
        }

        if (snakeX < -2 || snakeY < -2 || snakeX > 14 * box || snakeY > 14 * box || collision(newHead, snake) || l) {
            if (fin == 0) {
                clearInterval(game)
                checkingCoo()
                fin += 1
            }
        };
        if ((word.length - nbrOfRock) == 0) {
            if (fin == 0) {
                clearInterval(game)
                checkingCoo()
                fin += 1
            }
        }
        snake.unshift(newHead);
        updateWord();
    }
    // }, 50);
}
async function checkingCoo() {
    console.log('checking')
    console.log(co2python)
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
    if (response.message == 'Le jeu est terminé!') {
        end_game(response.result.xp, response.result.time, response.result.lost_lives)
    } else if (response.message == 'ok') {
        animXp.style.animation = 'Xpanim 1s ease-in-out forwards';
        word = []
        var xp = response.result.xp
        xpWin.innerHTML = `+${xp}`
        setTimeout(() => {
            isEventListener = false
            snake = [{ x: 7 * box, y: 7 * box }]
            nbrLettreTrouve = 0
            co2python = []
            snakeX = snake[0].x;
            snakeY = snake[0].y;
            nbrOfRock = 0
            animXp.style.animation = 'disapear 0.5s ease-in-out forwards';
            getPosition()
            d = undefined
            game = setInterval(function () {
                draw('pas de changement');
            }, 14)
            fin = 0
        }, 20);
    }
}

function collision(head, array) {
    for (let g = 0; g < array.length; g++) {
        if (head.x == array[g].x && head.y == array[g].y) {
            return true;
        }
    }
    return false;
}


getPosition();
var game = setInterval(function () {
    draw('pas de changement');
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
            console.log(data);
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


// animXp.style.animation = 'Xpanim 1s ease-in-out forwards';
// animXp.style.animation = 'disapear 0.5s ease-in-out forwards';