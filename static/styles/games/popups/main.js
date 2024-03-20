const victoryAudioUrl = '/static/sounds/victory-sound-effect.mp3';
const victoryAudio = new Audio(victoryAudioUrl);
victoryAudio.volume = 1;
victoryAudio.load();
const failureAudioUrl = '/static/sounds/failure-sound-effect.mp3';
const failureAudio = new Audio(failureAudioUrl);
failureAudio.volume = 1;
failureAudio.load();

/**
 * 
 * This function is used to start the game
 * 
 * @function start_game
 * @returns {void} - The result of the function
 */

const start_countdown = setInterval(() => {
    const counter = document.getElementById('counter');
    counter.textContent = parseInt(counter.textContent) - 1;
    if (counter.textContent == 0) {
        clearInterval(start_countdown);
        document.querySelector('.start-pop-up').classList.remove('active');
    }
}, 1000);

/**
 * 
 * This function is used to end the game
 * 
 * @function end_game
 * @param {number} xp - The experience points earned by the user
 * @param {number} time - The time spent by the user
 * @param {number} life - The number of lives lost by the user
 * 
 * @returns {void} - The result of the function
 */

function end_game(xp, time, life) {
    const end_pop_up = document.querySelector('.end-pop-up');
    end_pop_up.classList.add('active');
    const leaveButton = document.getElementById('leave-button');
    const nextButton = document.getElementById('final-path-button');
    const body = document.querySelector('body');
    for (let i = 0; i < body.children.length; i++) {
        if (body.children[i].className != "end-pop-up pop-up active") {
            body.children[i].style.pointerEvents = "none";
        }
    }

    clearInterval(timer);
    if (life > 0) {
        try {
            leaveButton.dataset.url = leaveButton.dataset.url + "False&xp=" + xp + "&lives=" + life;
        } catch (error) {
            nextButton.dataset.url = nextButton.dataset.url + "False&xp=" + xp + "&lives=" + life;
        }
        possiblesMessages = [
            "Vous pouvez faire mieux !",
            "Retentez votre chance pour améliorer votre score !",
            "Vous avez perdu une bataille, mais pas la guerre !",
            "Relevez vous et retentez votre chance !",
            "Vous avez perdu, mais vous pouvez faire mieux !"
        ];
        failureAudio.play();
    } else {
        try {
            leaveButton.dataset.url = leaveButton.dataset.url + "True&xp=" + xp + "&lives=" + life;
        } catch (error) {
            nextButton.dataset.url = nextButton.dataset.url + "True&xp=" + xp + "&lives=" + life;
        }
        possiblesMessages = [
            "Félicitations ! Vous avez gagné !",
            "Bravo ! Vous avez réussi !",
            "Vous avez gagné !",
            "Vous êtes un champion !",
            "Vous avez gagné ! Vous êtes le meilleur !"
        ];
        victoryAudio.play();
    }

    const message = possiblesMessages[Math.floor(Math.random() * possiblesMessages.length)];
    document.getElementById('end-message').innerHTML = message;
    // Display the experience points, the time and the number of lives lost by the user
    var xp_interval_nb = (1 / xp) * 1000;
    var xp_count = 0;
    var xp_interval = setInterval(() => {
        document.getElementById('data-xp').innerHTML = xp_count;
        xp_count++;
        if (xp_count > xp) {
            clearInterval(xp_interval);
        }
    }, xp_interval_nb);

    var life_count = 0;
    var life_interval = setInterval(() => {
        document.getElementById('data-life').innerHTML = life_count;
        life_count++;
        if (life_count > life) {
            clearInterval(life_interval);
        }
    }, 200);

    var time_interval_nb = (1 / time) * 1000;
    var time_count = 0;
    var time_interval = setInterval(() => {
        document.getElementById('data-time').innerHTML = time_count;
        time_count++;
        if (time_count >= time) {
            clearInterval(time_interval);
        }
    }, time_interval_nb);
}

/**
 * 
 * This function is used to redirect the user to another page
 * 
 * @function button
 * @returns {void} - The result of the function
 */
const button = document.querySelectorAll('.button');
button.forEach(btn => {
    btn.addEventListener('click', () => {
        btn.innerHTML = "<div class='loader'></div>";
        window.location.href = btn.dataset.url;
    });
});

/**
 * 
 * This function is used to skip the introduction
 * 
 * @function skipButton
 * @returns {void} - The result of the function
 */
const skipButton = document.getElementById('skip-intro');
skipButton.addEventListener('click', () => {
    document.querySelector('.start-pop-up').classList.remove('active');
    clearInterval(start_countdown);
});

/**
 * Reload the page when the back button is pressed.
 * 
 * @event pageshow
 * @param {Event} event - The event object.
 * @returns {void}
 */
window.addEventListener('pageshow', function(event) {
    if (event.persisted) {
        window.location.reload();
    }
});