const session_id = document.getElementsByTagName('body')[0].dataset.session_id;
const csrf_token = document.getElementById('csrf_token').value;
const game = document.getElementById('game')
var lives = document.querySelectorAll('.lives-zone')


const infos = document.getElementById('infos');
var current_indice = 0
var AllDuos = []
var answers = []
var gamePlay = true


/**
 * 
 * This function is used to display one duo French/English on the window
 * 
 * @function newDuo
 * @param {Object} list The list of all duos French/English
 * 
 * @returns {void} - The result of the function
 */
function newDuo(list) {

    // Give an index, a time of begin and a falling duration to each duo
    var indiceDuo = current_indice
    var time = Date.now();
    let counter = 0;
    var duringOfFalling = Math.floor(Math.random() * 2000 + 5000)

    // Create a div with the duo inside
    var duo = document.createElement('div');
    duo.classList.add('duo');
    duo.innerHTML = `${list[indiceDuo].duo[0]}/${list[indiceDuo].duo[1]}`;
    var rotate = Math.floor(Math.random() * 45 - 15)
    var height = infos.clientHeight
    game.appendChild(duo)

    // set a x position and an y position for each duo
    var Xpos = Math.floor(Math.random() * 70 + 8)
    duo.style.left = `${Xpos}%`
    var startY = Math.floor(Math.random() * (window.innerHeight / 2) + height)
    setTimeout(() => {
        duo.style.transform = `rotateZ(${rotate}deg) scale(1)`
    }, 200);

    duo.style.top = `${startY}px`
    var speed = Math.floor(Math.random() * 4 + 1)

    // Check if the duo is correct on click
    duo.onclick = function checking() {
        clearInterval(timing)

        // Add the indice of the duo to answers
        answers.push(list[indiceDuo].indice);

        // Check if the answers choosen is correct
        if (list[indiceDuo].checking == true) {
            this.style.border = 'none'
            this.style.background = '#717744';
            setTimeout(() => {
                this.style.transform = `rotateZ(${rotate}deg) scale(0.01)`
                setTimeout(() => {
                    this.remove()
                }, 200);
            }, 200);
        } else if (list[indiceDuo].checking == false) {
            // Takes a life
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

                // Ends the game if the user has no life left
                if (lives.length == 0) {
                    clearInterval(appear);
                    if (gamePlay) {
                        check(answers);
                    }
                }
                setTimeout(() => {
                    this.remove();
                }, 200);
            }, 200);
        }
    }

    // Drops the duo
    var timing = setInterval(() => {
        let current_time = Date.now();
        startY += speed;
        duo.style.top = `${startY}px`;
        counter++;

        // Check if the falling duration is over
        if ((current_time - time) > duringOfFalling) {
            duo.style.transform = `rotateZ(${rotate}deg) scale(0.01)`

            // Check if the duo was a good or a bad duo
            if (list[indiceDuo].checking) {
                clearInterval(timing)
                if (lives.length != 0) {
                    lives[lives.length - 1].remove()
                }
                lives = document.querySelectorAll('.lives-zone')
                answers.push('false')
                if (lives.length == 0) {
                    clearInterval(appear);
                    if (gamePlay) {
                        check(answers);
                    }
                }
            }
        }
    }, 40);
    current_indice++;
}

/**
 * 
 * This function is used to check if the response obtained in JavaScript is the same as the response in python
 * 
 * @function check
 * @param {Object} list The list of user responses
 * 
 * @returns {void} - The result of the function
 */
async function check(list) {
    try {
        // Send a request to the python to check the answers
        r = await fetch(`/dashboard/games/fallingword/${session_id}/checkAnswers`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRF-TOKEN': csrf_token
            },
            body: JSON.stringify({ answers: list })
        });
        response = await r.json();

        // End the game if the response of request is ok
        if (response.code == 201) {
            clearInterval(appear)
            let duo = document.querySelectorAll('.duo');
            duo.forEach(element => {
                element.remove();
            });
            gamePlay = false;
            end_game(response.result.xp, response.result.time, response.result.lost_lives);
        }
    } catch (error) {
        window.location.href = '/dashboard/errors/500';
    }
}

const popup = document.querySelectorAll('.pop-up')[0];


/**
 * 
 * This function is used to get all Duos French/English and start the game
 * 
 * @function check
 * @param {Object} list The list of user responses
 * 
 * @returns {void} - The result of the function
 */
async function getAllDuos() {
    // Reclaims all python duos
    var r = await fetch(`/dashboard/games/fallingword/${session_id}/getDuo`)
    var response = await r.json();
    AllDuos = response.result;

    // Create one duo every 1,2s
    begin = setInterval(() => {
        if (popup.className != 'start-pop-up pop-up active') {
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
            const response = await fetch(`/dashboard/games/fallingword/${session_id}/checktime`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRF-TOKEN': csrf_token
                },
                body: JSON.stringify({ answers: answers })
            });
            const data = await response.json();
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