const successAudioUrl = '/static/sounds/success-sound-effect.mp3';
const successAudio = new Audio(successAudioUrl);
successAudio.volume = 1;
successAudio.load();
const failAudioUrl = '/static/sounds/wrong-sound-effect.mp3';
const failAudio = new Audio(failAudioUrl);
failAudio.volume = 1;
failAudio.load();

/**
 * 
 * This function is used to check the word entered by the user (by sending a request to the server)
 *  -> Code 200: The word is correct
 *  -> Code 201: The game is over
 *  -> Code 404: The word is incorrect
 *  -> Error: The server is not responding -> Redirect the user to the 500 error page
 * 
 * @function check_word
 * @param {HTMLFormElement} form - The form containing the word entered by the user
 * @param {Event} event - The event that triggered the function
 * 
 * @returns {Promise<void>} - The result of the request 
 */
const form = document.getElementById('check-form');
form.addEventListener('submit', (event) => check_word(form, event));

async function check_word(form, event) {
    // Cancel the default action, if needed
    event.preventDefault();

    // Get the word entered by the user
    const word = form.word.value;
    const body = document.querySelector('body');
    const word_list = document.getElementsByClassName('words_list')[0];

    // Activate the loader
    form.submit.innerHTML = "<div class='loader'></div>"
    try {
        // Send a request to the server
        const response = await fetch(`/dashboard/games/typefast/${body.dataset.session_id}/check_word/${word}`);
        const data = await response.json();

        // If the word is correct
        if (data.code == 200) {
            if (!word_list.querySelector('.word')) {
                word_list.innerHTML = '';
            }
            document.getElementById('score').textContent = parseInt(document.getElementById('score').textContent) + 1;
            word_list.innerHTML += `<div class="word">${word}</div>`;
            form.word.value = '';
            successAudio.play();
            form.submit.innerHTML = "Vérifier";
        } else if (data.code == 201) { // If the game is over
            document.getElementById('score').textContent = parseInt(document.getElementById('score').textContent) + 1;
            word_list.innerHTML += `<div class="word">${word}</div>`;
            form.word.value = '';
            form.submit.innerHTML = "Vérifier";
            successAudio.play();
            end_game(data.result.xp, data.result.time, data.result.lost_lives);
        } else { // If the word is incorrect
            // Activate the error animation
            form.submit.innerHTML = "Vérifier";
            form.submit.classList.add("pulse");
            failAudio.play();
            setTimeout(() => {
                form.submit.classList.remove("pulse");
            }, 250);
        }
    } catch (error) {
        console.log(error);
        // window.location.href = '/dashboard/errors/500';
    }
}

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
            const response = await fetch(`/dashboard/games/typefast/${document.querySelector('body').dataset.session_id}/check_status`);
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