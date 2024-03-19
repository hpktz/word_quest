const wordEl = document.getElementById('word');
const badLetter = document.getElementById('bad-letter');
const replayBtn = document.getElementById('play-button');
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

// Ajout des Indices en appuyant sur le + -------------------------------------------------------------------------------------
var indices = [
    { title: "Indice Rigolo", indice: "eh regarde comme cet indice est fou" },
    { title: "Hippoindice", indice: "eh regarde comme cet indice est hippodinguo" },
    { title: "Yo c'est Billy", indice: "un apagnan sucrée au sucre" },
]

async function newIndice() {
    try {
        const getIndice = await fetch(`/dashboard/games/hangman/${sessionID}/askhint`);
        var currentIndice = await getIndice.json();
        if (currentIndice.code == 200) {
            xpwin = currentIndice["result"]['xp']

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

function showWord(data, letter) {
    if (data.result.finished == true) {
        successAudio.play();
        for (let i = 0; i < document.querySelectorAll('.letter').length; i++) {
            if (document.querySelectorAll('.letter')[i].innerHTML == '') {
                document.querySelectorAll('.letter')[i].innerHTML = letter;
            }
        }
        wordFind += 1
        xpNotif.innerHTML = '+' + String(data.result.xp_won);
        animXp.style.animation = 'Xpanim 1s ease-in-out forwards'
        badLetters = [];
        XpTotal += data.result.xp_won
        xpCounter.innerHTML = String(data.result.total_xp) + 'Xp';
        nextWord(data);
    } else {
        for (let i = 0; i < data.result.letter_position.length; i++) {
            document.querySelectorAll('.letter')[data.result.letter_position[i]].innerHTML = letter;
        }
    }
}

function updateBadLetter(data, letter) {
    // afficher les mauvaises lettre
    const keyLetter = document.querySelectorAll('.key-letter');
    for (let i = 0; i < keyLetter.length; i++) {
        if (keyLetter[i].innerHTML == letter) {
            keyLetter[i].style.background = '#8d0000';
            keyLetter[i].style.color = 'white';
        }
    }

    if (data.result.finished == true) {
        failAudio.play();
        figurePart.forEach((e) => {
            e.style.stroke = "red"
        })
        xpNotif.innerHTML = '+' + String(data.result.xp_won);
        animXp.style.animation = 'Xpanim 1s ease-in-out forwards';
        figurePart.forEach((partie, index) => {
            partie.style.display = 'block'
        })
        for (let i = 0; i < document.querySelectorAll('.letter').length; i++) {
            if (document.querySelectorAll('.letter')[i].innerHTML == '') {
                document.querySelectorAll('.letter')[i].innerHTML = data.result.last_word[i];
                document.querySelectorAll('.letter')[i].style.color = 'red';
            }
        }
        nextWord(data)
    } else {
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

// affiche notif

function printNotification() {
    notif.classList.add('afficher');

    setTimeout(() => {
        notif.classList.remove('afficher');
    }, 2000);
}

// Event listeners
var isEventListener = true

window.addEventListener('keydown', async e => {
    try {
        if (isEventListener) {
            console.log(figurePart, badLetters)
            if (badLetters.length < figurePart.length) {

                if (e.keyCode >= 65 && e.keyCode <= 90 || e.keyCode == 54) {
                    isEventListener = false
                    loader.style.display = 'flex'
                    const check = await fetch(`/dashboard/games/hangman/${sessionID}/check_letter/${e.key}`);
                    loader.style.display = 'none'
                    var checked = await check.json();
                    letter = e.key
                    if (checked.code == 200) {
                        if (checked.message == "already touch") {
                            printNotification();
                        } else if (checked.result.correct == true) {
                            goodLetters = checked.result.good
                            keyboard.forEach(el => {
                                if (el.innerHTML == letter) {
                                    el.style.background = '#373d20';
                                    el.style.color = 'white';
                                }
                            });
                            showWord(checked, letter);
                        } else {
                            badLetters = checked.result.bad;
                            xpwin = checked.result.xp;
                            updateBadLetter(checked, letter);
                        }
                        isEventListener = true
                    } else if (checked.code == 201) {
                        for (let i = 0; i < document.querySelectorAll('.letter').length; i++) {
                            if (document.querySelectorAll('.letter')[i].innerHTML == '') {
                                document.querySelectorAll('.letter')[i].innerHTML = letter;
                            }
                        }
                        end_game(checked.result.xp, checked.result.time, checked.result.lost_lives)
                    }
                }
            }
        }
    } catch (error) {
        window.location.href = '/dashboard/errors/500';
    }
})

keyboard.forEach(e => {
    e.addEventListener('click', async() => {
        try {
            if (isEventListener) {
                isEventListener = false
                loader.style.display = 'flex'
                const check = await fetch(`/dashboard/games/hangman/${sessionID}/check_letter/${e.innerHTML}`);
                loader.style.display = 'none'
                var checked = await check.json();

                if (checked.code == 200) {
                    if (checked.message == "already touch") {
                        printNotification();
                    } else if (checked.result.correct == true) {
                        goodLetters = checked.result.good
                        showWord(checked, e.innerHTML);
                        e.style.background = '#373d20';
                        e.style.color = 'white';
                    } else {
                        badLetters = checked.result.bad;
                        xpwin = checked.result.xp;
                        updateBadLetter(checked, e.innerHTML);
                    }
                    isEventListener = true
                } else if (checked.code == 201) {
                    for (let i = 0; i < document.querySelectorAll('.letter').length; i++) {
                        if (document.querySelectorAll('.letter')[i].innerHTML == '') {
                            document.querySelectorAll('.letter')[i].innerHTML = letter;
                        }
                    }
                    end_game(checked.result.xp, checked.result.time, checked.result.lost_lives)
                }
            }
        } catch (error) {
            window.location.href = '/dashboard/errors/500';
        }
    })
});

replayBtn.addEventListener('click', () => {
    location.reload()
})


function nextWord(data) {
    setTimeout(async() => {
        try {
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


            keyboard.forEach(e => {
                e.style.background = '#ccd77c';
                e.style.color = '#433831'
            });
            Wordslength++;
            xpCounter.innerHTML = String(data.result.total_xp) + 'Xp';
            addIndice.style.pointerEvents = 'auto'
            addIndice.innerHTML = '<img src="/static/icons/plus-60-white.png" alt="">'

            wordEl.innerHTML = "";
            for (let i = 0; i < data.result.len_word; i++) {
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