const sessionID = document.getElementsByTagName('body')[0].dataset.session_id;
const successAudioUrl = '/static/sounds/success-sound-effect.mp3';
const successAudio = new Audio(successAudioUrl);
successAudio.volume = 1;
successAudio.load();
const failAudioUrl = '/static/sounds/fail-sound-effect.mp3';
const failAudio = new Audio(failAudioUrl);
failAudio.volume = 0.2;
failAudio.load();
const pathContainer = document.getElementsByClassName('path-container')[0];
const items = document.getElementsByClassName('item');
const wordsContainer = document.getElementById('words-container');

const listeningHtml = '<div class="music-listener"><div class="bar"></div><div class="bar"></div><div class="bar"></div><div class="bar"></div><div class="bar"></div></div>';
const microphoneHtml = '<div class="micro-listener"><div class="point"></div></div>';
const csrf_token = document.getElementById('csrf_token').value;

const infoButton = document.getElementById('show-path');
infoButton.addEventListener('click', see_path_call);

/**
 * 
 * This function is used to call the server to display the path
 * 
 * @function see_path_call
 * @returns {void} - The result of the function
 */
async function see_path_call() {
    try {
        // Get the tries amount
        const triesAmount = document.getElementById('tries-amount');
        // If the user has tries
        if (parseInt(triesAmount.innerHTML) > 0) {
            // Call the server to display the path
            const response = await fetch(`/dashboard/games/memowordrize/${sessionID}/see_path`);
            const data = await response.json();
            triesAmount.innerHTML = 3 - data.result.tries;
            await see_path(data); // Display the path
        } else {
            infoButton.classList.add('wrong');
            await new Promise(resolve => setTimeout(resolve, 1000));
            infoButton.classList.remove('wrong');
        }
    } catch (error) {
        window.location.href = '/dashboard/errors/500';
    }
}

/**
 * 
 * This function is used to display the path
 * 
 * @function see_path
 * @param {Object} data - The data returned by the server
 * @returns {void} - The result of the function
 */
async function see_path(data) {
    // Unset the button
    infoButton.classList.remove('pulse');
    infoButton.classList.add('disabled');
    infoButton.removeEventListener('click', see_path);
    // Display the loader
    wordsContainer.innerHTML = "<div class='loader'></div>";
    if (data.code === 200) {
        const triesAmount = document.getElementById('tries-amount');
        // Unset all the cases
        for (var i = 0; i < items.length; i++) {
            items[i].setAttribute('class', 'item disabled');
            items[i].innerHTML = "";
        }
        var charArray = data.result.path;
        for (var i = 0; i < charArray.length; i++) {
            // Display the path one by one
            var item = document.getElementById("item-" + charArray[i].position); // Activate the case
            item.classList.add('active');
            item.innerHTML = listeningHtml;
            var toPlay = `/dashboard/games/memowordrize/${sessionID}/audio/${charArray[i].id}`; // Get the audio to play
            var audio = new Audio(toPlay);
            await play_audio(audio); // Play the audio
            await new Promise(resolve => setTimeout(resolve, 200));
            item.classList.remove('active');
            item.innerHTML = "";
        };
        // Display the path without the audio (UX improvement)
        for (var i = 0; i < charArray.length; i++) {
            var item = document.getElementById("item-" + charArray[i].position);
            item.classList.add('active');
            await new Promise(resolve => setTimeout(resolve, 100));
        }
        // Hide the path
        await new Promise(resolve => setTimeout(resolve, 1000));
        const activatedItems = document.querySelectorAll('.item.active');
        for (var i = 0; i < activatedItems.length; i++) {
            activatedItems[i].classList.remove('active');
            await new Promise(resolve => setTimeout(resolve, 100));
        }

        // Change the button
        if (data.result.tries < 3) {
            infoButton.classList.remove('disabled');
            infoButton.addEventListener('click', see_path);
            triesAmount.innerHTML = 3 - data.result.tries;
        } else {
            triesAmount.innerHTML = 0;
        }

        // Enable the cases
        for (var i = 0; i < items.length; i++) {
            items[i].classList.remove('disabled');
        }

        // Display the words to put in the cases
        wordsContainer.innerHTML = "";
        for (var i = 0; i < data.result.words.length; i++) {
            var word = document.createElement('div');
            word.innerHTML = data.result.words[i];
            word.classList.add('word-draggable');
            word.addEventListener('mousedown', draggWord);
            word.addEventListener('touchstart', draggWord, { passive: true });
            wordsContainer.appendChild(word);
        }
    } else if (data.code == 201) {
        end_game(data.result.xp, data.result.time, data.result.lost_lives);
    } else {
        infoButton.classList.add('wrong');
        await new Promise(resolve => setTimeout(resolve, 1000));
        infoButton.classList.remove('wrong');
    }
}


/**
 * 
 * This function is used to play the audio
 * 
 * @function play_audio
 * @param {Element} audio - The audio to play
 * @returns {void} - The result of the function
 */
async function play_audio(audio) {
    // Send a promise to wait for the audio to end
    return new Promise((resolve, reject) => {
        let audioEnded = false;
        audio.play(); // Play the audio
        audio.addEventListener('ended', () => {
            audioEnded = true;
            resolve();
        }); // When the audio ends, resolve the promise

        // Otherwise, if the audio doesn't end, go to the next audio
        // It is a security to avoid the audio to be stuck
        setTimeout(() => {
            if (!audioEnded) {
                audio.pause();
                audio.currentTime = 0;
                resolve();
            }
        }, 5000);
    });
}

/**
 * 
 * This functionis used to try a case (by sending the word to the server)
 * 
 * @function try_case
 * @param {Element} draggableEl - The word to send
 * @param {Element} max - The element to compare with
 * @returns {void} - The result of the function
 */
async function try_case(draggableEl, max) {
    try {
        // Get the words container
        const wordsContainer = document.getElementById('words-container');
        const position = max.id.split('-')[1]; // Get the position of the word
        // Send the word to the server
        const response = await fetch(`/dashboard/games/memowordrize/${sessionID}/try_case`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrf_token
            },
            body: JSON.stringify({
                'position': position,
                'word': draggableEl.innerHTML
            })
        });

        // Get the response
        const data = await response.json();
        if (data.code === 200) {
            // Correct animations
            draggableEl.setAttribute('class', 'word-draggable correct'); // Set the class of the word to correct
            await new Promise(resolve => setTimeout(resolve, 500)); // Wait for 500ms

            // Put the word in the correct place with the correct size
            draggableEl.style.width = max.getBoundingClientRect().width + 'px';
            draggableEl.style.height = max.getBoundingClientRect().height + 'px';
            draggableEl.style.transform = 'translate(-50%, -50%) scale(1)';
            draggableEl.style.lineHeight = max.getBoundingClientRect().height + 'px';
            successAudio.play(); // Play the success audio
            max.classList.add('correct'); // Add the correct class to the case
            max.innerHTML = `<p class="word">${draggableEl.innerHTML}</p>`; // Set the innerHTML of the case to the word
            var parent = max.parentElement; // Get the parent of the case
            for (var i = 0; i < parent.children.length; i++) {
                // Unset the case in the same line
                if (!parent.children[i].classList.contains('correct')) {
                    parent.children[i].classList.add('disabled');
                }
            }
            await new Promise(resolve => setTimeout(resolve, 500));
            draggableEl.remove(); // Remove the moveable word
        } else if (data.code == 201) {
            // If the game is over, end the game
            end_game(data.result.xp, data.result.time, data.result.lost_lives);
        } else {
            // Wrong animations
            draggableEl.setAttribute('class', 'word-draggable wrong');
            await new Promise(resolve => setTimeout(resolve, 200));

            // Put the word in the wrong place with the correct size
            draggableEl.style.width = max.getBoundingClientRect().width + 'px';
            draggableEl.style.height = max.getBoundingClientRect().height + 'px';
            draggableEl.style.transform = 'translate(-50%, -50%) scale(1)';
            draggableEl.style.lineHeight = max.getBoundingClientRect().height + 'px';
            max.classList.add('wrong'); // Add the wrong class to the case
            failAudio.play(); // Play the fail audio
            await new Promise(resolve => setTimeout(resolve, 500));
            draggableEl.style.opacity = 0; // Hide the word
            draggableEl.style.width = 'auto';
            draggableEl.style.height = '35px';
            draggableEl.style.lineHeight = '35px';
            await new Promise(resolve => setTimeout(resolve, 250));
            wordsContainer.innerHTML = ""; // Remove the words
            await new Promise(resolve => setTimeout(resolve, 500));
            max.classList.remove('wrong'); // Remove the wrong class from the case
            max.classList.add('disabled'); // Add the disabled class to the case

            // Reset the case
            for (var i = 0; i < items.length; i++) {
                items[i].setAttribute('class', 'item');
                items[i].innerHTML = "";
            }

            // Display the word to put in the case
            for (var i = 0; i < data.result.words.length; i++) {
                var word = document.createElement('div');
                word.innerHTML = data.result.words[i];
                word.classList.add('word-draggable');
                word.addEventListener('mousedown', draggWord);
                word.addEventListener('touchstart', draggWord, { passive: true });
                wordsContainer.appendChild(word);
            }
        }
        // If the current path is finished
        if (data.result.finished) {
            // Reset the case
            for (var i = 0; i < items.length; i++) {
                items[i].setAttribute('class', 'item');
                items[i].innerHTML = "";
            }
            // Display the experience points
            var xpMessageContainer = document.getElementsByClassName('xp-message')[0];
            xpMessageContainer.classList.add('active');
            document.getElementById('xp-message-data').innerHTML = data.result.xp;
            await new Promise(resolve => setTimeout(resolve, 1250));
            xpMessageContainer.classList.remove('active');
            document.getElementById('xp').innerHTML = parseInt(document.getElementById('xp').innerHTML) + data.result.xp; // Update the experience points
            infoButton.classList.add('pulse');
            infoButton.blur();
            wordsContainer.innerHTML = '<div class="mess">Cliquez sur "Voir le parcours" pour continuer</div>';
        }
    } catch (error) {
        window.location.href = '/dashboard/errors/500';
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
            const response = await fetch(`/dashboard/games/memowordrize/${document.querySelector('body').dataset.session_id}/check_status`);
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

/***** DRAG SYSTEM ******/

var wordsDraggable = document.getElementsByClassName('word-draggable');
for (var i = 0; i < wordsDraggable.length; i++) {
    wordsDraggable[i].addEventListener('mousedown', draggWord); // For the mouse (PC version)
    wordsDraggable[i].addEventListener('touchstart', draggWord, { passive: true }); // For the touch (Mobile version)
}

// Set the variables
let offsetX, offsetY, isDragging = false;
var draggableEl = null;

/**
 * 
 * This function is used to set the variables when the user starts dragging the word
 * 
 * @function draggWord
 * @param {Event} event - The event that triggered the function
 * @returns {void} - The result of the function
 */
async function draggWord(event) {
    isDragging = true;
    // Set the variables
    if (event.type === 'touchstart') {
        offsetX = event.touches[0].clientX;
        offsetY = event.touches[0].clientY;
    } else {
        offsetX = event.clientX;
        offsetY = event.clientY;
    }
    event.target.style.cursor = 'grabbing';
    draggableEl = event.target;
};

document.addEventListener('mousemove', function(e) {
    // Move the word
    if (isDragging) {
        const x = e.clientX - offsetX;
        const y = e.clientY - offsetY;
        draggableEl.style.transform = `translate(${x}px, ${y}px)`;
    }
});

document.addEventListener('touchmove', function(e) {
    // Move the word
    if (isDragging) {
        const x = e.touches[0].clientX - offsetX;
        const y = e.touches[0].clientY - offsetY;
        draggableEl.style.transform = `translate(${x}px, ${y}px)`;
    }
}, { passive: true });

// When the user stops dragging the word
document.addEventListener('mouseup', endgraggWord);
document.addEventListener('touchend', endgraggWord);

/**
 * 
 * This function is used to put the word in the case if the user stops dragging the word
 * -> If the word is in a case, put the word in the case
 * -> If the word is not in a case, reset the word
 * 
 * @function endgraggWord
 * @returns {void} - The result of the function
 * 
 */
function endgraggWord() {
    if (isDragging) {
        isDragging = false;
        draggableEl.style.cursor = 'grab';
        let items = document.getElementsByClassName('item');
        // Check if the word is in a case and if it's the case, put the word in the case
        max = items[0]
        overlapPercent = 0;
        for (var i = 0; i < items.length; i++) {
            if (items[i].classList.contains('disabled') || items[i].classList.contains('correct') || items[i].classList.contains('wrong')) {
                continue;
            }
            // Calculate the percentage of overlap
            itemOverlap = get_overlap(draggableEl, items[i]);
            if (itemOverlap > overlapPercent) {
                overlapPercent = itemOverlap;
                max = items[i];
            }
        }
        if (overlapPercent == 0) {
            draggableEl.style.transform = `translate(0px, 0px)`;
            draggableEl = null;
        } else {
            // Put the word in the case
            itemCenterX = max.getBoundingClientRect().left + max.getBoundingClientRect().width / 2;
            itemCenterY = max.getBoundingClientRect().top + max.getBoundingClientRect().height / 2;
            draggableEl.style.position = 'absolute';
            draggableEl.style.transform = 'translate(-50%, -50%) scale(0.9)';
            draggableEl.style.left = `${itemCenterX}px`;
            draggableEl.style.top = `${itemCenterY}px`;
            try_case(draggableEl, max);
        }
    }
}

/**
 * 
 * This function is used to calculate the percentage of overlap between two elements
 * 
 * @param {*} element1 - The first element
 * @param {*} element2  - The second element
 * @returns 
 */
function get_overlap(element1, element2) {
    const rect1 = element1.getBoundingClientRect();
    const rect2 = element2.getBoundingClientRect();

    const overlapWidth = Math.min(rect1.right, rect2.right) - Math.max(rect1.left, rect2.left);
    const overlapHeight = Math.min(rect1.bottom, rect2.bottom) - Math.max(rect1.top, rect2.top);

    const area2 = (rect2.right - rect2.left) * (rect2.bottom - rect2.top);

    const overlapArea = Math.max(0, overlapWidth) * Math.max(0, overlapHeight);

    const overlapPercentage = (overlapArea / area2) * 100;
    return overlapPercentage;
}