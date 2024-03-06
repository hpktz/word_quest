const session_id = document.body.dataset.session_id;

const canvas = document.querySelector("canvas");


const context = canvas.getContext('2d');

let box = 20

let snake = [{ x: 10*box, y:10*box}];

snake[0] = { x: 10*box, y:10*box}
// place le serpent au centre


words = ["MAISON","CHATEAU"];
var word = words[1].split('');
const wordStyle = words[1].split('');
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

letterPositions = [{x: 0, y:0}];
alreadyPos = false
function getPosition(list) {
            let xpos = Math.floor(Math.random() * 20) * box;
            let ypos = Math.floor(Math.random() * 18 + 1) * box;
            console.log(xpos,ypos)
                
            for (let j = 0; j < list.length; j++) {
                console.log(list[j].x, list[j].y)
                    if (xpos == list[j].x || ypos == list[j].y) {
                        alreadyPos = false
                        break
                    } else {
                        alreadyPos = true
                    }

            }
            
            if(alreadyPos){
                list.push({
                        x: xpos,
                        y: ypos                        
                    }); 
                return list
            }            
            else if(!alreadyPos){
                getPosition(list);
            }
        }
        
for(let i = 0; i < word.length; i++){
    console.log(getPosition(letterPositions))
}
letterPositions.shift();


let score = 0;

let d;

document.addEventListener('keydown', direction);

function direction(event) {
    let key = event.keyCode;
    if(key == 37 && d != "RIGHT"){
        d = "LEFT";;
    } else if(key == 38 && d !="DOWN"){
        d = "UP";
    } else if(key == 39 && d != "LEFT"){
        d = "RIGHT";
    } else if(key == 40 && d !="UP"){
        d = "DOWN";
    }
}



function draw() {
    context.clearRect(0, 0, 400, 400)

    letterIndex = 0;
    word.forEach(e => {
        context.fillStyle = "red";
        context.font = "30px League Spartan";
        context.fillText(e, letterPositions[letterIndex].x, letterPositions[letterIndex].y);
        letterIndex++; 
    });
    for(let i = 0; i < snake.length; i++){
        if(i == 0){
            context.fillStyle = "#604f43";
            context.beginPath();
            context.lineWidth="2";
            if(d == "LEFT") context.arc(snake[i].x + 10, snake[i].y + 10, 13, 0, 2 * Math.PI);
            if(d == "RIGHT") context.arc(snake[i].x  + 10, snake[i].y + 10, 13, 0, 2 * Math.PI);
            if(d == "UP") context.arc(snake[i].x + 10, snake[i].y + 10, 13, 0, 2 * Math.PI);
            if(d == "DOWN") context.arc(snake[i].x + 10, snake[i].y + 10, 13, 0, 2 * Math.PI);
            if(d == undefined) context.arc(snake[i].x + 10, snake[i].y + 10, 13, 0, 2 * Math.PI);
            
            context.fill();
        } else {
            context.fillStyle = "#766153"
            context.fillRect(snake[i].x,snake[i].y, box, box);
        }
        
        
    }
    

   

    let snakeX = snake[0].x;
    let snakeY = snake[0].y;

    if(d == "LEFT") snakeX -= box;
    if(d == "RIGHT") snakeX += box;
    if(d == "UP") snakeY -= box;
    if(d == "DOWN") snakeY += box;
    var letterFind = false
    var l = false
    for(let i = 0; i < letterPositions.length; i++){
        if(snakeX == letterPositions[i].x  && snakeY == letterPositions[i].y - 20){
            score++;
            letterFind = true;
            
            word.splice(word.indexOf(word[i]),1);
            letterPositions.splice(i,1);
            nbrLettreTrouve ++;
            if(word[0] != wordStyle[nbrLettreTrouve]){
                l = true
            }
        }
    }
    if(!letterFind){
        snake.pop()    
    }
    
    let newHead = {
            x: snakeX,
            y: snakeY
        };    
    
    
    if(snakeX < 0 || snakeY < 0 || snakeX > 19*box || snakeY > 19*box || collision(newHead, snake) || l){
        clearInterval(game);
        // defeat();
    };
    if(word.length == 0){
        setTimeout(() => {
            alert('win')
            
        }, 200);
    }
    snake.unshift(newHead);
    
    updateWord();

    context.fillStyle = "red";
    context.font = "30px Arial";
    context.fillText(score, 2*box, 1.6*box);
}
function collision(head, array){
    for(let g = 0;g < array.length; g++){
        if(head.x == array[g].x && head.y == array[g].y){
            return true;
        }
    }
    return false;
}

let game = setInterval(draw, 100);




