const wordEl = document.getElementById('word');
const badLetter = document.getElementById('bad-letter');

const popup = document.getElementById('popup-content');
const notif = document.getElementById('notification-content');
const finalMessage = document.getElementById('final-message');
const figurePart = document.querySelectorAll('.figure-part');
const remarque = document.getElementById('remarque');

const xpCounter = document.getElementById('xp');
const xpNotif = document.getElementById('xpnotif');
const animXp = document.getElementById('animation-xp');
const xpFinal = document.getElementById('XP-final');
const loader = document.getElementById('loader')


const addIndice = document.getElementById('add-indice');
const indiceContainer = document.getElementById('indice-container');

const sessionID = document.getElementsByTagName('body')[0].dataset.session_id;

let nbrIndiceDiscover = 0


var Wordslength = 0
const finding = document.getElementById('word-finded')
var wordFind = 0
const recap = document.getElementById('recap');
const keyboard = document.querySelectorAll('.key-letter');

var a = 0;
var XpTotal = 0;
var nbrFaute = 0;
var xpwin = 5;

var goodLetters = [''];
var badLetters = [];

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
 * This function is used to display a hint (indice) to the user (by sending a request to the server)
 * 
 * @function newIndice
 * @returns {void} - The result of the function
 */
async function newIndice() {
    try {
        // Get the hint from the server
        const getIndice = await fetch(`/dashboard/games/hangman/${sessionID}/askhint`);
        var currentIndice = await getIndice.json();
        // If the hint is found
        if (currentIndice.code == 200) {
            xpwin = currentIndice["result"]['xp']

            // Display the hint to the user
            var indice = document.createElement("div");
            var indiceTitle = document.createElement("p");
            var indiceContent = document.createElement("p");
            indice.classList.add('indice');
            indiceTitle.classList.add('name-indice');
            indiceContent.classList.add('indice-content');
            indiceTitle.innerHTML = currentIndice["result"]["title"];
            indiceContent.innerHTML = currentIndice["result"]["hint"];
            indice.appendChild(indiceTitle);
            indice.appendChild(indiceContent);
            indiceContainer.appendChild(indice);
            indice.style.animation = 'indicanim 1s ease-in-out forwards';
            addIndice.style.display = 'none';
            setTimeout(() => {
                indice.style.animation = 'depophint 0.5s ease-in-out forwards';
                setTimeout(() => {
                    indice.style.display = 'none'
                    addIndice.style.display = 'flex'
                }, 600);
            }, 3000);
        } else {
            // Otherwise, inform the user that there are no more hints
            addIndice.innerHTML = `Plus d'indices`
            addIndice.style.pointerEvents = 'none'
        }
    } catch (error) {
        window.location.href = '/dashboard/errors/500';
    }
}


addIndice.addEventListener('click', async() => {
    newIndice();
})
/**
 * 
 * This function is used to display a letter in the word
 * 
 * @function showWord
 * @param {Object} data - The data sent by the server
 * @param {string} letter - The letter that the user has entered
 * @returns {void} - The result of the function
 * 
 */
function showWord(data, letter) {
    // If the word is finished
    if (data.result.finished == true) {
        successAudio.play(); // Play the success sound
        // Display all the letters of the word
        for (let i = 0; i < document.querySelectorAll('.letter').length; i++) {
            if (document.querySelectorAll('.letter')[i].innerHTML == '') {
                document.querySelectorAll('.letter')[i].innerHTML = letter;
            }
        }
        wordFind += 1
        // Display the number of words found
        xpNotif.innerHTML = '+' + String(data.result.xp_won);
        animXp.style.animation = 'Xpanim 1s ease-in-out forwards'
        badLetters = [];
        XpTotal += data.result.xp_won
        xpCounter.innerHTML = String(data.result.total_xp) + 'Xp';
        nextWord(data); // Go to the next word
    } else {
        // Otherwise, display the letter in the word
        for (let i = 0; i < data.result.letter_position.length; i++) {
            document.querySelectorAll('.letter')[data.result.letter_position[i]].innerHTML = letter;
        }
    }
}

/**
 * 
 * This function is used to update the letters and the hangman figure when it is wrong
 * 
 * @function updateBadLetter
 * @param {Object} data - The data sent by the server
 * @param {string} letter - The letter that the user has entered
 * @returns {void} - The result of the function
 */ 
function updateBadLetter(data, letter) {
    // Put the wrong letter in red
    const keyLetter = document.querySelectorAll('.key-letter');
    for (let i = 0; i < keyLetter.length; i++) {
        if (keyLetter[i].innerHTML == letter) {
            keyLetter[i].style.background = '#8d0000';
            keyLetter[i].style.color = 'white';
        }
    }

    // If the word is finished
    if (data.result.finished == true) {
        failAudio.play(); // Play the fail sound
        // Put the figure in red
        figurePart.forEach((e) => {
            e.style.stroke = "red"
        })
        // Display the xp won
        xpNotif.innerHTML = '+' + String(data.result.xp_won);
        animXp.style.animation = 'Xpanim 1s ease-in-out forwards';
        figurePart.forEach((partie, index) => {
            partie.style.display = 'block'
        })
        // Display the undiscovered letters
        for (let i = 0; i < document.querySelectorAll('.letter').length; i++) {
            if (document.querySelectorAll('.letter')[i].innerHTML == '') {
                document.querySelectorAll('.letter')[i].innerHTML = data.result.last_word[i];
                document.querySelectorAll('.letter')[i].style.color = 'red';
            }
        }
        nextWord(data); // Go to the next word
    } else {
        // Otherwise, update the hangman figure
        figurePart.forEach((partie, index) => {
            const erreurs = badLetters.length;
            if (index < erreurs) {
                partie.style.display = 'block'
            } else {
                partie.style.display = 'None'
            }
        })
    }
}

// Show a notification
function printNotification() {
    notif.classList.add('afficher');
    setTimeout(() => {
        notif.classList.remove('afficher');
    }, 2000);
}

// Event listeners
var isEventListener = true

// Each time a key is pressed
window.addEventListener('keydown', async e => {
    try {
        // If the event listener is active
        if (isEventListener) {
            // If the word is not finished
            if (badLetters.length < figurePart.length) {
                // If the key pressed is a letter
                if (e.keyCode >= 65 && e.keyCode <= 90 || e.keyCode == 54) {
                    isEventListener = false // Disable the event listener
                    loader.style.display = 'flex'
                    // Check the letter (by sending a request to the server)
                    const check = await fetch(`/dashboard/games/hangman/${sessionID}/check_letter/${e.key}`);
                    loader.style.display = 'none'
                    var checked = await check.json();
                    letter = e.key

                    // If the letter is correct
                    if (checked.code == 200) {
                        // If the letter has already been entered
                        if (checked.message == "already touch") {
                            printNotification();
                        } else if (checked.result.correct == true) {
                            // Update the good letters
                            goodLetters = checked.result.good
                            keyboard.forEach(el => {
                                if (el.innerHTML == letter) {
                                    el.style.background = '#373d20';
                                    el.style.color = 'white';
                                }
                            });
                            showWord(checked, letter);
                        } else {
                            // Update the bad letters
                            badLetters = checked.result.bad;
                            xpwin = checked.result.xp;
                            updateBadLetter(checked, letter);
                        }
                        isEventListener = true // Enable the event listener
                    } else if (checked.code == 201) { // If the word is finished
                        for (let i = 0; i < document.querySelectorAll('.letter').length; i++) {
                            if (document.querySelectorAll('.letter')[i].innerHTML == '') {
                                document.querySelectorAll('.letter')[i].innerHTML = letter;
                            }
                        }
                        // End the game
                        end_game(checked.result.xp, checked.result.time, checked.result.lost_lives)
                    }
                }
            }
        }
    } catch (error) {
        window.location.href = '/dashboard/errors/500';
    }
})

// Each time a key is clicked
keyboard.forEach(e => {
    e.addEventListener('click', async() => {
        try {
            // If the event listener is active
            if (isEventListener) {
                isEventListener = false // Disable the event listener
                loader.style.display = 'flex'
                // If the word is not finished
                const check = await fetch(`/dashboard/games/hangman/${sessionID}/check_letter/${e.innerHTML}`);
                loader.style.display = 'none'
                var checked = await check.json();

                // If the letter is correct
                if (checked.code == 200) {
                    // If the letter has already been entered
                    if (checked.message == "already touch") {
                        printNotification();
                    } else if (checked.result.correct == true) {
                        // Update the good letters
                        goodLetters = checked.result.good
                        showWord(checked, e.innerHTML);
                        e.style.background = '#373d20';
                        e.style.color = 'white';
                    } else {
                        // Update the bad letters
                        badLetters = checked.result.bad;
                        xpwin = checked.result.xp;
                        updateBadLetter(checked, e.innerHTML);
                    }
                    isEventListener = true // Enable the event listener
                } else if (checked.code == 201) {
                    // If the word is finished
                    for (let i = 0; i < document.querySelectorAll('.letter').length; i++) {
                        if (document.querySelectorAll('.letter')[i].innerHTML == '') {
                            document.querySelectorAll('.letter')[i].innerHTML = e.innerHTML;
                        }
                    }
                    // End the game
                    end_game(checked.result.xp, checked.result.time, checked.result.lost_lives)
                }
            }
        } catch (error) {
            window.location.href = '/dashboard/errors/500';
        }
    })
});

/**
 * 
 * This function is used to display the intarface for the next word
 * 
 * @function nextWord
 * @param {Object} data - The data sent by the server
 * @returns {void} - The result of the function
 * 
 */
function nextWord(data) {
    // Wait for the animation to finish
    setTimeout(async() => {
        try { 
            // Hide all the members of the hangman figure
            indiceContainer.innerHTML = "";
            addIndice.style.display = 'flex'
            figurePart.forEach((e) => {
                e.style.display = 'none';
                e.style.stroke = '#717744';
            })
            popup.style.display = 'none';
            goodLetters = [];
            badLetters = [];
            nbrFaute = 0;
            xpwin = 5;
            nbrFaute = 0;
            animXp.style.animation = 'disapear 0.5s ease-in-out forwards';

            // Unset the letters of the keyboard
            keyboard.forEach(e => {
                e.style.background = '#ccd77c';
                e.style.color = '#433831'
            });
            Wordslength++;

            // Update the number of words found
            xpCounter.innerHTML = String(data.result.total_xp) + 'Xp';
            addIndice.style.pointerEvents = 'auto'
            addIndice.innerHTML = '<img src="/static/icons/plus-60-white.png" alt="">'

            // Display the empty word
            wordEl.innerHTML = "";
            for (let i = 0; i < data.result.len_word; i++) {
                // Add a space if necessary
                if (data.result.spaces_positions.includes(i)) {
                    wordEl.innerHTML += '<span class="space"></span>';
                }
                wordEl.innerHTML += '<span class="letter"></span>';
            }
        } catch (error) {
            window.location.href = '/dashboard/errors/500';
        }
    }, 1000);
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
            const response = await fetch(`/dashboard/games/hangman/${document.querySelector('body').dataset.session_id}/check_status`);
            const data = await response.json();
            // If the game is over
            if (data.code == 201) {
                // End the game
                end_game(data.result.xp, data.result.time, data.result.lost_lives);
            }
        } catch (error) {
            //         window.location.href = '/dashboard/errors/500';
            console.log(error)
        }
    }
}, 1000);

timer;

// RESPONSIVE -------------------------------------

const all = document.getElementById('all');
const figureContent = document.getElementById('svg');
const exit = document.getElementById('exit');
const separationLine = document.getElementById('sep');
const hints = document.getElementById('hint');
const other = document.getElementById('other');
const keyLetter = document.querySelectorAll('.key-letter');
const keyb = document.getElementById('keyboard');

// Function to check if the height is greater than the width
setInterval(() => {
    if (window.innerWidth < window.innerHeight) {
        all.classList.add('tablet-all')
        figureContent.classList.add('tablet-svg');
        exit.classList.add('tablet-exit');
        separationLine.classList.add('tablet-sep');
        hints.classList.add('tablet-hint');
        other.classList.add('tablet-other');
        keyLetter.forEach(e => {
            e.classList.add('tablet-kl');
        });
        keyb.classList.add('tablet-kb');
        if (document.getElementById('newhint') != null) {
            document.getElementById('newhint').classList.add('tablet-idc');
        }
    } else {
        all.classList.remove('tablet-all')
        figureContent.classList.remove('tablet-svg');
        exit.classList.remove('tablet-exit');
        separationLine.classList.remove('tablet-sep');
        hints.classList.remove('tablet-hint');
        other.classList.remove('tablet-other');
        keyLetter.forEach(e => {
            e.classList.remove('tablet-kl');
        });
        keyb.classList.remove('tablet-kb')
        if (document.getElementById('newhint') != null) {
            hint.classList.remove('tablet-idc');
        }

    }
}, 200);