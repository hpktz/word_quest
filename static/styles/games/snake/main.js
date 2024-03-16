const session_id = document.body.dataset.session_id;

const canvas = document.querySelector("canvas");
const context = canvas.getContext('2d');


const animXp = document.getElementById('animation-xp');
const xpWin = document.getElementById('xpnotif');
const frWord = document.getElementById('frensh-word');

let box = 56

const pressMessage = document.getElementById('press-message');
const score = document.getElementById('xp')
var xpTotal = 0

score.innerHTML = xpTotal + ' Xp'

var snake = [{ x: 4*box, y:4*box}];

snake[0] = { x: 4*box, y:4*box}
var word = []
var wordStyle = []
var nbrOfRock = 0
const totalLetterArea = document.getElementById('word');

const image = document.getElementById('source')

nbrLettreTrouve = 0;    
function updateWord(){
    totalLetterArea.innerHTML = '';
    wordStyle.forEach((element,index) => {
        if (element != 'rock') {
            if(index < nbrLettreTrouve){
                totalLetterArea.innerHTML += `<span class="letter">${element}</span>`
            } else {
                totalLetterArea.innerHTML += `<span class="letter"></span>`
            };
        }
    });
}
var isEventListener = false
var letterPositions = [{x: 0, y:0}];
var co2python = ['vide']
// alreadyPos = false
async function getPosition() {
    wordStyle = []
    r = await fetch(`/dashboard/games/snake/${session_id}/getWord`)
    response = await r.json();
    letterPositions = response.result.coo
    frWord.innerHTML = response.result.frensh
    for (let i = 0; i < letterPositions.length; i++) {
        word.push(letterPositions[i].letter);
        wordStyle.push(letterPositions[i].letter)
    }
    for (let index = 0; index < word.length; index++) {
        if (word[index] == 'rock') {
            nbrOfRock ++;
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
    evt.preventDefault();
    evt.stopPropagation();
}, false);
window.addEventListener("touchend", function mobiletouch(evt) {
    var touches = evt.changedTouches[0];
    var betweenX = touches.pageX - startX;
    var betweenY = touches.pageY - startY;

    if (!Number.isInteger(snakeY/56) || !Number.isInteger(snakeX/56)) {
        setTimeout(() => {
            mobiletouch(evt)
        }, 40);
    } else {
    
        if (Math.abs(betweenX) > 50 || Math.abs(betweenY) > 50) {
            if (Math.abs(betweenX) > Math.abs(betweenY) + 10) {
                if (betweenX > 0) d = 'RIGHT'
                else d = 'LEFT'
            } else {
                if (betweenY > 0) d = 'DOWN'
                else d = 'UP'
            }
        }

    }
}, false);
document.addEventListener('keydown', direction);
function direction(event) {

    if (!Number.isInteger(snakeY/56) || !Number.isInteger(snakeX/56)) {
        setTimeout(() => {
            direction(event)
        }, 40);
    } else {
        let key = event.keyCode;
        if(key == 37 && d != "RIGHT"){
            d = "LEFT";;
        }
        if(key == 39 && d != "LEFT"){
            d = "RIGHT";
        }
        if(key == 38 && d !="DOWN"){
            d = "UP";
        } 
        if(key == 40 && d !="UP"){
            d = "DOWN";
        }
    }

}
var fin = 0
function draw() {
    // let cool = setInterval(() => {
        if(isEventListener == true){
            // clearInterval(cool)
            context.clearRect(0, 0, 504, 504)
            if (d != undefined) {
                pressMessage.style.display= 'none'
            } else{
                pressMessage.style.display= 'block'
            }
            context.fillStyle = "#ffffff80";
            let background_x = 0
            let background_y = 0
            for (let i = 0; i < 9; i++) {
                for (let j = 0; j < 9; j++) {
                    context.fillRect(background_x + 8,background_y + 8,40,40)
                    // context.beginPath()
                    // context.lineWidth = "10"
                    // context.strokeStyle = "brown"
                    // context.rect(background_x,background_y,55,55)
                    // context.stroke()
                    background_x += 56
                    // if(context.fillStyle == "#c1c286"){
                    //     context.fillStyle = "#84855c"
                    // } else if (context.fillStyle == '#84855c') {
                    //     context.fillStyle = "#c1c286"
                    // }
                    
                }
                background_x = 0
                background_y += 56
            }
            var letterIndex = 0;
            letterPositions.forEach(e => {
                if (e.letter == 'rock') {
                    context.drawImage(image, letterPositions[letterIndex].x - 10, letterPositions[letterIndex].y - 22, 40, 25)
                } else {
                context.fillStyle = "#373D20";
                context.font = "30px League Spartan";
                context.fillText(e.letter, letterPositions[letterIndex].x, letterPositions[letterIndex].y); 
                }
            letterIndex++;
            });
            for(let i = 0; i < snake.length; i++){
                if(i == 0){
                    context.fillStyle = "#BCBD8B";
                    context.beginPath();
                    context.lineWidth="2";
                    context.arc(snake[i].x + 28, snake[i].y + 28, 13, 0, 2 * Math.PI)
                    context.fill();
                }
                else {
                    context.fillStyle = "#373D20"
                    context.fillRect(snake[i].x + 15,snake[i].y + 15, box-30, box-30);
                }
            var e = 8 * (nbrLettreTrouve + 1)
            if(snake.length != e+1 && d != undefined){
                snake.push(1)
            }
            
            context.fillStyle = "#BCBD8B";
            context.beginPath();
            context.lineWidth="2";
            context.arc(snake[0].x + 28, snake[0].y + 28, 13, 0, 2 * Math.PI)
            context.fill();
            }
            if(d == "LEFT"){ 
                snakeX -= Math.floor(box/8)
            }
            if(d == "RIGHT") snakeX += Math.floor(box/8);
            if(d == "UP") snakeY -= Math.floor(box/8);
            if(d == "DOWN") snakeY += Math.floor(box/8);
            var letterFind = false
            var l = false
            for(let i = 0; i < letterPositions.length; i++){
                if(snakeX == letterPositions[i].x - 19  && snakeY == letterPositions[i].y - 37){
                    if (letterPositions[i].letter != word[0]) {
                        l = true
                    } else{
                        if (co2python[0] =='vide') {
                            co2python.shift()
                        }
                        co2python.push(letterPositions[i].x,letterPositions[i].y)
                        letterFind = true;
                        word.shift();
                        letterPositions.splice(i, 1);
                        nbrLettreTrouve ++;
                    }
                }
            }
            if(!letterFind){
                snake.pop()    
            }
            let newHead = {
                x: snakeX,
                y: snakeY
                } ;
            
            
            if(snakeX < 0 || snakeY < 0 || snakeX > 8*box || snakeY > 8*box || collision(newHead, snake) || l){
                if (fin == 0) {
                    clearInterval(game)
                    checkingCoo()
                    fin+=1
                }
            };
            if((word.length - nbrOfRock) == 0){
                if (fin == 0) {
                    clearInterval(game)
                    checkingCoo()
                    fin+=1
                }
            } 
            snake.unshift(newHead);
            updateWord();
        }
    // }, 50);
}
async function checkingCoo() {
    r = await fetch(`/dashboard/games/snake/${session_id}/${co2python}/check_coo`)
    response = await r.json()
    console.log(response)
    if (response.code == 500) {
        window.location.href = '/dashboard/errors/500';
    }
    xpTotal = response.result.xpTot
    score.innerHTML = xpTotal + ' Xp'
    if (response.message == 'Le jeu est terminé!'){
        end_game(response.result.xp, response.result.time, response.result.lost_lives)
    } else if (response.message == 'ok') {
        animXp.style.animation = 'Xpanim 1s ease-in-out forwards';
        word = []
        var xp = response.result.xp
        xpWin.innerHTML = `+${xp}`
        setTimeout(() => {
            isEventListener = false
            snake = [{ x: 4*box, y:4*box}]
            nbrLettreTrouve = 0
            co2python = ['vide']
            snakeX = snake[0].x;
            snakeY = snake[0].y;
            nbrOfRock = 0
            animXp.style.animation = 'disapear 0.5s ease-in-out forwards';
            getPosition() 
            d = undefined
            game = setInterval(draw,45)
            fin = 0
        }, 1000);
    }
}
function collision(head, array){
    for(let g = 0;g < array.length; g++){
        if(head.x == array[g].x && head.y == array[g].y){
            return true;
        }
    }
    return false;
}


getPosition();
var game = setInterval(draw, 45);



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