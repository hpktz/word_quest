const session_id = document.body.dataset.session_id;
const successAudioUrl = '/static/sounds/success-sound-effect.mp3';
const successAudio = new Audio(successAudioUrl);
successAudio.volume = 1;
successAudio.load();
const failAudioUrl = '/static/sounds/fail-sound-effect.mp3';
const failAudio = new Audio(failAudioUrl);
failAudio.volume = 0.4;
failAudio.load();

/**
 * 
 * This function is used to display the player animation
 * 
 * @function play
 * @param {Element} element - The container of the animation
 * 
 * @returns {void} - The result of the function
 */
async function play(element) {
    const audio_el = document.getElementById('audio-container');
    audio_el.classList.add('active');
    const audio = new Audio(element.dataset.audio_link);
    audio.play();
    audio.onended = () => {
        audio_el.classList.remove('active');
    }
}
window.onload = () => {
    if (document.getElementById('audio-container')) {
        document.getElementById('audio-container').onclick = () => {
            play(document.getElementById('audio-container'));
        }
    }
}


/**
 *
 * This function is used to add an event listener to the answers
 * -> Redirect to the check_answer function
 * 
 * @function answers
 * @param {Element} answer - The answer element
 * 
 * @returns {void} - The result of the function
 */
const answers = document.querySelectorAll('.answer');
answers.forEach(answer => {
    answer.addEventListener('click', () => {
        check_answer(answer.id.split('-')[1]);
    });
});

/**
 * 
 * This function is used to check the answer (by sending a request to the server)
 * -> If the answer is correct, the function will display the next question
 * -> If the answer is incorrect, the function will display the correct answer
 * -> If the game is over, the function will display the end pop-up
 * 
 * @function check_answer
 * @param {String} answer 
 * 
 * @returns {void} - The result of the function
 */
async function check_answer(answer) {
    try {
        const answer_html = document.getElementById('answer-' + answer);
        const answer_content = answer_html.innerHTML;
        answer_html.innerHTML = "<div class='loader'></div>"
        answers.forEach(answer => {
            answer.style.pointerEvents = 'none';
        });
        const response = await fetch(`/dashboard/games/quiz/${session_id}/check/${answer}`);
        const data = await response.json();
        if (data.code == 200 || data.code == 201) {
            answer_html.innerHTML = answer_content;
            if (data.message == "correct" ||
                data.result.last_position == answer) {
                document.getElementById('data-score').textContent = data.result.score;
                document.getElementById('answer-' + answer).classList.add('correct');
                successAudio.play();
            } else {
                document.getElementById('answer-' + answer).classList.add('wrong');
                document.getElementById('answer-' + data.result.last_position).classList.add('correct');
                failAudio.play();
            }
            document.querySelector('.progress-inner').style.width = `${((parseInt(data.result.total) - parseInt(data.result.remaining))/parseInt(data.result.total)*100)}%`;
            setTimeout(() => {
                document.getElementById("question").innerHTML = data.result.html;
                if (document.getElementById('audio-container')) {
                    document.getElementById('audio-container').onclick = () => {
                        play(document.getElementById('audio-container'));
                    }
                }
                for (let i = 0; i < answers.length; i++) {
                    answers[i].innerHTML = data.result.answers[i];
                    answers[i].classList.remove('correct');
                    answers[i].classList.remove('wrong');
                }
                answers.forEach(answer => {
                    answer.style.pointerEvents = 'auto';
                });
            }, 1000);
        } else {
            window.location.href = '/dashboard/errors/500';
        }
        if (data.code == 201) {
            console.log(data.result.time);
            end_game(data.result.xp, data.result.time, data.result.lost_lives);
        }
    } catch (error) {
        console.log(error);
        window.location.href = '/dashbaord/errors/500';
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
            const response = await fetch(`/dashboard/games/quiz/${document.querySelector('body').dataset.session_id}/check_status`);
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