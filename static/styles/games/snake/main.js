const session_id = document.body.dataset.session_id;

const canvas = document.querySelector("canvas");


const context = canvas.getContext('2d');

let box = 56

let snake = [{ x: 4*box, y:4*box}];

snake[0] = { x: 4*box, y:4*box}
// place le serpent au centre

// var words = ["MAISON","CHATEAU","UNEFFICIENT"];
// var word = words[2].split('');
var word = []
var wordStyle = []
const totalLetterArea = document.getElementById('word');

nbrLettreTrouve = 0;    
function updateWord(){
    
    totalLetterArea.innerHTML = '';
    wordStyle.forEach((element,index) => {
        if(index < nbrLettreTrouve){
            totalLetterArea.innerHTML += `<span class="letter">${element}</span>`
        } else {
            totalLetterArea.innerHTML += `<span class="letter"></span>`
        };
    });
}
var isEventListener = false
var letterPositions = [{x: 0, y:0}];
var co2python = []
// alreadyPos = false
async function getPosition() {
    r = await fetch(`/dashboard/games/snake/${session_id}/getCard`)
    response = await r.json();
    letterPositions = response.result
    for (let i = 0; i < letterPositions.length; i++) {
        word.push(letterPositions[i].letter);
        wordStyle.push(letterPositions[i].letter)
    }
    isEventListener = true
}
let score = 0;

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
            if (Math.abs(betweenX) > Math.abs(betweenY)) {
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
    // for (let index = 0; index < 20; index++) {
    //     if (!Number.isInteger(snakeX/56)) {
    //         console.log(snakeX)
    //     }
        
    // } 
    // (!Number.isInteger(snakeX/56) ) {
    //     console.log(snakeX)
    //     snakeX = snakeX;
    // }

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

    // let key = event.keyCode;
    // if(key == 37 && d != "RIGHT"){

    //     d = "LEFT";;
    // } else if(key == 38 && d !="DOWN"){
    //     d = "UP";
    // } else if(key == 39 && d != "LEFT"){
    //     d = "RIGHT";
    // } else if(key == 40 && d !="UP"){
    //     let t = snakeX%56
    //     console.log(t)
    //     d = "DOWN";
    // }  

}
function draw() {
    let cool = setInterval(() => {
        if(isEventListener == true){
            clearInterval(cool)
    
            context.clearRect(0, 0, 504, 504)
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
                context.fillStyle = "red";
                context.font = "30px League Spartan";
                context.fillText(e.letter, letterPositions[letterIndex].x, letterPositions[letterIndex].y);
                letterIndex++; 
            });
            for(let i = 0; i < snake.length; i++){
                if(i == 0){
                    context.fillStyle = "#BCBD8B";
                    context.beginPath();
                    context.lineWidth="2";
                    context.arc(snake[i].x + 28, snake[i].y + 28, 13, 0, 2 * Math.PI)
                    // console.log(snake[i].x, snake[i].y)
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
                    console.log(wordStyle)
                    if (letterPositions[i].letter != word[0]) {
                        l = true
                    } else{
                        // co2python.push({x: letterPositions[i].x, y: letterPositions[i].y})
                        co2python.push(letterPositions[i].x,letterPositions[i].y)
                        score++;
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
                clearInterval(game);
                // defeat();
            };
            if(word.length == 0){
                checkingCoo()
                // setTimeout(() => {
                //     console.log(co2python)
                    
                // }, 200);
            }
            snake.unshift(newHead);
            
            updateWord();

            context.fillStyle = "red";
            context.font = "30px Arial";
            context.fillText(score, 2*box, 1.6*box);
        }
    }, 50);
}
async function checkingCoo() {
    console.log(co2python)
    r = await fetch(`/dashboard/games/snake/${session_id}/${co2python}/check_coo`)
    response = await r.json()
    console.log(response)
}
function collision(head, array){
    for(let g = 0;g < array.length; g++){
        if(head.x == array[g].x && head.y == array[g].y){
            return true;
        }
    }
    return false;
}


getPosition()
var game = setInterval(draw, 40);
    




