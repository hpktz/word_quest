const session_id = document.getElementsByTagName('body')[0].dataset.session_id;

// const duoBox = document.getElementById('duo')
// duoBox.style.top = `${Ypos}px`
// setInterval(() => {
//     Ypos += speed;
//     duoBox.style.top = `${Ypos}px`
// }, 25);
const game = document.getElementById('game')
var lives = document.querySelectorAll('.lives-zone')


const infos = document.getElementById('infos');
var current_indice = 0
var AllDuos = []
var answers = []
function newDuo(list) {
    var indiceDuo = current_indice
    var time = Date.now();
    let counter = 0;
    console.log(list[indiceDuo])
    var duringOfFalling = Math.floor(Math.random() * 2000 + 5000)
    var duo = document.createElement('div');
    duo.classList.add('duo');
    duo.innerHTML = `${list[indiceDuo].duo[0]}/${list[indiceDuo].duo[1]}`;
    var rotate = Math.floor(Math.random() * 45 - 15)
    var height = infos.clientHeight
    game.appendChild(duo)
    var Xpos = Math.floor(Math.random() * 70 + 8)
    duo.style.left = `${Xpos}%`
    var startY = Math.floor(Math.random() * (window.innerHeight/2) + height)
    setTimeout(() => {
        duo.style.transform = `rotateZ(${rotate}deg) scale(1)`
    }, 200);
    
    duo.style.top = `${startY}px`
    var speed = Math.floor(Math.random() * 4 +1)
    duo.onclick = function checking() {
        clearInterval(timing)
        answers.push(list[indiceDuo].indice);
        if (list[indiceDuo].checking == true){
            console.log('True')
            this.style.border = 'none'
            this.style.background = '#717744';
            setTimeout(() => {
                this.style.transform = `rotateZ(${rotate}deg) scale(0.01)`
                setTimeout(() => {
                    this.remove()
                }, 200);
            }, 200);
        } else if (list[indiceDuo].checking == false){
            console.log('Faux')
            if (lives.length != 0) {
                lives[lives.length - 1].style.transform = 'scale(0.01)'
            }
            this.style.border = 'none'
            this.style.background = '#940e0e';
            setTimeout(() => {
                this.style.transform = `rotateZ(${rotate}deg) scale(0.01)`
                if (lives.length != 0) {
                    lives[lives.length - 1].remove()
                } 
                lives = document.querySelectorAll('.lives-zone')
                if (lives.length == 0) {
                    clearInterval(appear);
                    check(answers);
                }
                setTimeout(() => {
                    this.remove();
                }, 200);
            }, 200);
        }
    }
    var timing = setInterval(() => {
        let current_time = Date.now();
        startY += speed;
        duo.style.top = `${startY}px`;
        counter++;
        if ((current_time - time) > duringOfFalling) {
            duo.style.transform = `rotateZ(${rotate}deg) scale(0.01)`
            if (list[indiceDuo].checking) {
                clearInterval(timing)
                if (lives.length != 0) {
                    lives[lives.length - 1].remove()
                } 
                lives = document.querySelectorAll('.lives-zone')
                answers.push('false')
                if (lives.length == 0) {
                    clearInterval(appear);
                    console.log(answers)
                    check(answers);
                }
            }
        }
    }, 40);
    current_indice ++;
}

function fall(speed, box, startY) {
    startY += speed;
    box.style.top = `${startY}px`;
}


async function check(list) {
    try {
        r = await fetch(`/dashboard/games/fallingword/${session_id}/${list}/checkAnswers`);
        response = await r.json();
        if (response.code == 201) {
            // End the game
            clearInterval(appear)
            end_game(response.result.xp, response.result.time, response.result.lost_lives);
        }
    } catch (error) {
        window.location.href = '/dashboard/errors/500';
    }
}

const popup = document.querySelectorAll('.pop-up')[0];

async function getAllDuos() {
    var r = await fetch(`/dashboard/games/fallingword/${session_id}/getDuo`)
    var response = await r.json();
    AllDuos = response.result;
    begin = setInterval(() => {
        if (popup.className !='start-pop-up pop-up active') {
            clearInterval(begin)
            appear = setInterval(() => {
            newDuo(AllDuos);
            }, 1200);
        }
    }, 50);
}
getAllDuos();






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
            if (answers.length == 0) {
                answers = 'vide'
            }
            const response = await fetch(`/dashboard/games/fallingword/${session_id}/${answers}/checktime`);
            const data = await response.json();
            console.log(data);
            // If the game is over
            if (data.code == 201) {
                // End the game
                clearInterval(appear)
                end_game(data.result.xp, data.result.time, data.result.lost_lives);
            }
        } catch (error) {
            window.location.href = '/dashboard/errors/500';
        }
    }
}, 1000);

timer;