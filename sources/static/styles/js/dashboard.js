const mainSection = document.getElementsByClassName('main-infos')[0];
mainSection.addEventListener('click', function(event) {
    close_boxes(this, event);
});

const listsContainer = document.getElementById('lists-container');
listsContainer.addEventListener('click', function(event) {
    close_boxes(this, event);
});

const gamesTrail = document.getElementsByClassName('games-trail')[0];
gamesTrail.addEventListener('click', function(event) {
    close_boxes(this, event);
});

/**
 * Opens the game information and updates the UI based on the provided game information.
 * 
 * @function open_game_info
 * @param {HTMLElement} el - The element that triggered the function.
 * @returns {void}
 */
function open_game_info(el) {
    // get the game information
    var gameInfos = el.dataset.game_infos;
    gameInfos = gameInfos.replace(/'/g, '"');
    gameInfos = JSON.parse(gameInfos);

    // update the UI based on the game information
    for (let i = 0; i < document.getElementsByClassName('level').length; i++) {
        document.getElementsByClassName('level')[i].classList.remove('selected');
    }
    el.classList.add('selected');

    var levelInfosPopUpContainer = document.getElementsByClassName('level-infos-pop-up-container')[0];
    levelInfosPopUpContainer.dataset.position = gameInfos[0].ord;
    levelInfosPopUpContainer.classList.add('level-info-entry');
    setTimeout(function() {
        levelInfosPopUpContainer.classList.remove('level-info-entry');
    }, 301);

    // update the UI based on the game information
    var levelInfoTitle = levelInfosPopUpContainer.getElementsByClassName('title')[0];
    var levelInfoText = levelInfosPopUpContainer.getElementsByClassName('text')[0];
    var levelInfoSubmitButton = levelInfosPopUpContainer.getElementsByClassName('submit-button')[0];
    if (gameInfos[0].completed == 1) {
        levelInfoSubmitButton.classList.add('start')
        levelInfoTitle.innerHTML = gameInfos[0].name;
        levelInfoText.innerHTML = gameInfos[0].short_desc;
        let a = document.createElement('a');
        a.href = gameInfos[0].url + "/" + gameInfos[0].list_id;
        a.innerHTML = "Rejouer";
        a.onclick = function(event) {
            open_game(this, event);
        }
        levelInfoSubmitButton.innerHTML = "";
        levelInfoSubmitButton.appendChild(a);
    } else if (gameInfos[0].status == "blocked") {
        levelInfoTitle.innerHTML = "Niveau bloqué";
        levelInfoText.innerHTML = "Terminez le niveau précédent pour débloquer ce niveau";
        levelInfoSubmitButton.classList.remove('start');
        levelInfoSubmitButton.innerHTML = "<p style='color:white;'>Bloqué</p>";
    } else {
        levelInfoSubmitButton.classList.add('start')
        levelInfoTitle.innerHTML = gameInfos[0].name;
        levelInfoText.innerHTML = gameInfos[0].short_desc;
        let a = document.createElement('a');
        a.href = gameInfos[0].url + "/" + gameInfos[0].list_id;
        a.innerHTML = "Jouer";
        a.onclick = function(event) {
            open_game(this, event);
        }
        levelInfoSubmitButton.innerHTML = "";
        levelInfoSubmitButton.appendChild(a);
    }

    // update the position of the game information popup
    setTimeout(function() {
        const overlay = document.getElementsByClassName('overlay-load-game')[0];
        var rect = levelInfoSubmitButton.getBoundingClientRect();

        var middleX = rect.left + (rect.width / 2);
        var middleY = rect.top + (rect.height / 2);

        overlay.style.left = middleX + "px";
        overlay.style.top = middleY + "px";
    }, 301);
}

/**
 * Opens a game (opening a loading popup).
 * 
 * @function open_game
 * @param {HTMLElement} el - The element that triggered the event.
 * @param {Event} event - The event object.
 * @returns {void}
 */
function open_game(el, event) {
    event.preventDefault();
    const live_amount = document.getElementById('lives-info').innerHTML;
    const el_inner = el.innerHTML;
    if (parseInt(live_amount) == 0) {
        el.innerHTML = "Vous n'avez plus de vies";
        el.classList.add('pulse');
        setTimeout(function() {
            el.classList.remove('pulse');
        }, 250);
        setTimeout(function() {
            el.innerHTML = el_inner;
        }, 2000);
        return;
    }

    const overlay = document.getElementsByClassName('overlay-load-game')[0];
    overlay.style.top = "0px";
    overlay.style.left = "0px";
    overlay.classList.add('active');

    setTimeout(function() {
        if (el.classList.contains('submit-button')) {
            const href = el.querySelector('a').getAttribute('href');
            window.location.href = href;
        } else {
            const href = el.getAttribute('href');
            window.location.href = href;
        }
    }, 2000)
}

/**
 * Opens the game trail and loads the game data for the selected game list. (by making a request to the server)
 * 
 * @async
 * @function open_game_trail
 * @param {HTMLElement} el - The element representing the selected game list.
 * @param {Event} event - The event object triggered by the user action.
 * @returns {Promise<void>} - A promise that resolves when the game trail is opened and the game data is loaded.
 */
const listBoxes = document.getElementsByClassName('list-box');
for (let i = 0; i < listBoxes.length; i++) {
    listBoxes[i].addEventListener('click', function(event) {
        open_game_trail(this, event);
    });
}

async function open_game_trail(el, event = undefined) {
    if (event) {
        if (event.target.classList.contains('delete-zone')) {
            return;
        }
    }

    // close all the different popups
    if (is_open()) {
        const arrow = document.getElementsByClassName('close-logo')[0].children[0];
        responsive(arrow, event);
    }

    const body = document.querySelector('body');
    body.setAttribute('class', 'phone-trail-opened')

    const trailContainer = document.getElementsByClassName('games-trail')[0];
    trailContainer.classList.add('active');
    trailContainer.innerHTML = "<div class='loader'></div>";

    const listsContainer = document.getElementsByClassName('list-box');
    var position = 0;
    for (let i = 0; i < listsContainer.length; i++) {
        if (listsContainer[i] == el) {
            position = i;
        }
    }

    const id = el.dataset.list_id;
    const color = position % 3;
    // get the game trail from the server
    try {
        const response = await fetch(`/dashboard/games/${id}`);
        const data = await response.text();
        const gamesTrail = document.getElementsByClassName('games-trail')[0];
        gamesTrail.innerHTML = data;
        gamesTrail.dataset.color = color;
        gamesTrail.getElementsByClassName('game-trail')[0].addEventListener('click', function(event) {
            close_level_popup(this, event);
        });
        gamesTrail.getElementsByClassName('close-game-rail-button')[0].addEventListener('click', function(event) {
            close_game_trail(this, event);
        });
        var levelBoxes = gamesTrail.getElementsByClassName('level-box');
        for (let i = 0; i < levelBoxes.length; i++) {
            levelBoxes[i].addEventListener('click', function(event) {
                open_game_info(this);
            });
        }
    } catch (e) {
        open_alert("Erreur", "Une erreur est survenue, veuillez réessayer plus tard");
    }

    // update the UI based on the game trail
    const listsBoxContainer = document.getElementsByClassName('list-box');
    for (let i = 0; i < listsBoxContainer.length; i++) {
        listsBoxContainer[i].classList.remove('selected');
    }
    el.classList.add('selected');
}

/**
 * Closes the game trail.
 * 
 * @function close_game_trail
 * @param {HTMLElement} el - The element that triggered the event.
 * @param {Event} event - The event object.
 * @returns {void}
 */
function close_game_trail(el, event) {
    event.preventDefault();
    const trailContainer = document.getElementsByClassName('games-trail')[0];
    trailContainer.classList.remove('active');
    setTimeout(function() {
        const body = document.querySelector('body');
        body.classList.remove('phone-trail-opened')
    }, 1000);
}

/**
 * Closes the level popup if the click event target is the popup container.
 * 
 * @function close_level_popup
 * @param {HTMLElement} el - The element representing the level popup container.
 * @param {Event} event - The click event object.
 * @returns {void}
 */
function close_level_popup(el, event) {
    if (event.target === el) {
        var levelInfosPopUpContainer = document.getElementsByClassName('level-infos-pop-up-container')[0];
        levelInfosPopUpContainer.dataset.position = 0;
        levelInfosPopUpContainer.classList.add('level-info-entry');

        var level = document.getElementsByClassName('level');
        for (let i = 0; i < level.length; i++) {
            level[i].classList.remove('selected');
        }
    }
}

/**
 * Opens the manage list pop-up and loads the list data for the selected list. (by making a request to the server)
 *  -> This function is only used to open the manage list pop-up and load the list data.
 * 
 * @function manage_list
 * @param {HTMLElement} el - The element that triggered the event.
 * @param {Event} event - The event object.
 * @param {number} id - The ID of the list to be deleted.
 */
const manageListButtons = document.getElementsByClassName('manage-list-button');
for (let i = 0; i < manageListButtons.length; i++) {
    manageListButtons[i].addEventListener('click', function(event) {
        manage_list(this, event, this.dataset.list_id);
    });
}
async function manage_list(el, event, id) {
    event.preventDefault();

    const deleteListPopUp = document.getElementsByClassName('manage-list')[0];
    deleteListPopUp.classList.add('active');
    const manageListContent = document.getElementById('manage-list-content');
    manageListContent.innerHTML = "<div class='loader'></div>";
    try {
        const response = await fetch(`/dashboard/manage/${id}`);
        const data = await response.text();
        await new Promise(resolve => setTimeout(resolve, 300));
        if (response.status != 200) {
            close_manage_list(el, event);
            open_alert("Erreur", "Une erreur est survenue, veuillez réessayer plus tard");
        } else {
            manageListContent.innerHTML = data;
            manageListContent.getElementsByClassName('manage-list-form')[0].addEventListener('submit', function(event) {
                update_list(this, event);
            });
        }
    } catch (e) {
        close_manage_list(el, event);
        open_alert("Erreur", "Une erreur est survenue, veuillez réessayer plus tard");
    }
}

/**
 * Closes the manage list pop-up.
 * 
 * @function close_manage_list
 * @param {HTMLElement} el - The element that triggered the event.
 * @param {Event} event - The event object.
 * @returns {void}
 */
const closeManageListButton = document.getElementById('close-manage-list-button');
closeManageListButton.addEventListener('click', function(event) {
    close_manage_list(this, event);
});

function close_manage_list(el, event) {
    event.preventDefault();

    const manageListContent = document.getElementById('manage-list-content');
    manageListContent.innerHTML = "";
    const deleteListPopUp = document.getElementsByClassName('manage-list')[0];
    deleteListPopUp.classList.remove('active');
}

async function update_list(el, event) {
    event.preventDefault();

    const list_id = el.dataset.id;
    const list_data = {
        name: el.listname.value,
        description: el.listdesc.value,
        time: el.time.value,
        xp: el.xp.value,
        game: el.game.value,
        reminder: el.reminder.checked,
        stats: el.stats.checked,
        public: el.public.checked
    }
    el.button.innerHTML = "<div class='loader'></div>";
    try {
        const response = await fetch(`/dashboard/manage/update/${list_id}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': el.csrf_token.value
            },
            body: JSON.stringify(list_data)
        });
        const data = await response.json();
        if (data.code == 200) {
            el.button.innerHTML = "Modifié";
            document.getElementById('alert-message-container').innerHTML = '<div class="success-mess">Mofifcation sauvegardées avec succès</div>';
            const list_box = document.getElementsByClassName('list-box');
            for (let i = 0; i < list_box.length; i++) {
                if (list_box[i].dataset.list_id == list_id) {
                    list_box[i].getElementsByClassName('title')[0].innerHTML = list_data.name;
                    break;
                }
            }
            setTimeout(function() {
                el.button.innerHTML = "Modifier";
                close_manage_list(el, event);
            }, 1000);
        } else {
            el.button.innerHTML = "Modifier";
            el.button.classList.add('pulse')
            document.getElementById('alert-message-container').innerHTML = `<div class="alert-mess">${data.message}</div>`;
            setTimeout(function() {
                el.button.classList.remove('pulse');
            }, 250);
        }
    } catch (e) {
        console.log(e);
        el.button.innerHTML = "Modifier";
        el.button.classList.add('pulse');
        document.getElementById('alert-message-container').innerHTML = '<div class="alert-mess">Une erreur est survenue, veuillez réessayer plus tard</div>';
        setTimeout(function() {
            el.button.classList.remove('pulse');
        }, 250);
    }
}

/**
 * Opens the lives pop-up and positions it relative to the given element.
 * 
 * @function open_lives
 * @param {HTMLElement} el - The element that triggered the opening of the lives pop-up.
 * @returns {void}
 */
const livesContainer = document.getElementById('lives-box')
if (livesContainer) {
    livesContainer.addEventListener('click', function(event) {
        open_lives(this, event);
    });
}

function open_lives(el) {
    const livesContainer = document.getElementsByClassName('lives-pop-up')[0];
    if (window.matchMedia("(max-width: 670px)").matches) {
        livesContainer.style.top = "65px";
        livesContainer.style.left = "calc(50% - 140px)";
        livesContainer.classList.add('active');

        const mainInfos = document.getElementsByClassName('main-infos')[0];
        mainInfos.classList.add('active');
    } else {
        livesContainer.style.top = "70px";
        livesContainer.style.left = "calc(100% - 325px)";
        el.classList.add('active');
    }
}

/**
 * Closes the lives pop-up box.
 * 
 * @function close_lives
 * @param {HTMLElement} el - The element that triggered the event.
 * @param {Event} e - The event object.
 * @returns {void}
 */
function close_lives(el, e) {
    e.preventDefault();
    if (e.target.classList.contains('lives-zone')) {
        return;
    }
    const livesBox = document.getElementById('lives-box');
    livesBox.classList.remove('active');
    const livesContainer = document.getElementsByClassName('lives-pop-up')[0];
    livesContainer.style.top = "-300px";
    livesContainer.classList.remove('active');
    const mainInfos = document.getElementsByClassName('main-infos')[0];
    mainInfos.classList.remove('active');
}

/**
 * Updates the lives counter and displays the remaining time for the next life.
 *  -> This function is only used to update the UI. 
 *     (the amount of lives is updated by the server when the user purchases lives or when he refreshes the page)
 * 
 * @async
 * @function lives_counter
 * @returns {void}
 */
async function lives_counter() {
    const counter = document.getElementById('lives-counter');
    const lives = counter.dataset.lives;
    const start_date = counter.dataset.time;
    const end_date = counter.dataset.end_time;

    // if the user has all his lives, the lives counter is updated and the function is stopped  
    if (parseInt(lives) == 5) {
        counter.innerHTML = "Vous avez toutes vos vies";
        counter.dataset.time = counter.dataset.time;
        document.getElementById('life-purchase-button').style.display = "none";
        return;
    }

    var interval = setInterval(function() {
        // if there is a change in the number of lives, the lives counter is updated and the function is stopped
        if (counter.dataset.lives != lives) {
            lives_counter();
            return clearInterval(interval);
        }

        var now = counter.dataset.time;
        var diff = end_date - now;

        // if the time is up, the lives counter is updated and the function is stopped
        if (diff < 0) {
            counter.dataset.lives = parseInt(lives) + 1;
            document.getElementById('lives-info').innerHTML = parseInt(lives) + 1;
            counter.dataset.end_time = parseInt(counter.dataset.end_time) + 900;
            const heartContainer = document.getElementsByClassName('heart-container')[0];
            heartContainer.getElementsByClassName('img')[lives].src = "/static/imgs/3d-red-heart.png";
            lives_counter();
            return clearInterval(interval);
        }
        var minutes = Math.floor(diff / 60);
        var seconds = ((diff % 60)).toFixed(0);

        counter.innerHTML = minutes + ":" + (seconds < 10 ? '0' : '') + seconds;
        counter.dataset.time = parseInt(counter.dataset.time) + 1;
        if (document.getElementById('gems-info').dataset.value < 200) {
            document.getElementById('life-purchase-button').classList.add('disabled');
        }
    }, 1000);

    // start the countdown
    interval;
}

/**
 * Purchase lives function. (by sending a request to the server)
 * 
 * @async
 * @function purchase_lives
 * @param {HTMLElement} el - The element that triggered the event.
 * @param {Event} event - The event object.
 * @returns {Promise<void>} - A promise that resolves when the function completes.
 */
const lifePurchaseButton = document.getElementById('life-purchase-button');
if (lifePurchaseButton) {
    lifePurchaseButton.addEventListener('click', function(event) {
        purchase_lives(this, event);
    });
}
async function purchase_lives(el, event) {
    event.preventDefault();
    // request to purchase lives
    el.innerHTML = "<div class='loader'></div>";
    const response = await fetch('/dashboard/lives/purchase', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': document.getElementById('csrf_token_purchase').value
        }
    });
    try {
        const data = await response.json();
        // if the request is successful, the lives counter is updated, and the UI is updated
        if (data.code == 200) {
            const counter = document.getElementById('lives-counter');
            const lives = counter.dataset.lives;
            const time = counter.dataset.time;
            counter.dataset.lives = parseInt(lives) + 1;
            counter.dataset.time = time;
            counter.dataset.end_time = parseInt(time) + 900;

            const heartContainer = document.getElementsByClassName('heart-container')[0];
            heartContainer.getElementsByClassName('img')[lives].src = "/static/imgs/3d-red-heart.png";

            const userInfos = document.getElementsByClassName('user-infos')[0];
            const livesInfo = document.getElementById('lives-info');
            livesInfo.innerHTML = parseInt(lives) + 1;
            userInfos.getElementsByClassName('box')[2].classList.add('pulse');

            // UI animation
            const gemsInfo = document.getElementById('gems-info');
            gemsInfo.innerHTML = data.gems;
            userInfos.getElementsByClassName('box')[0].classList.add('pulse');
            el.innerHTML = "Acheter (200 gemmes)";
            setTimeout(function() {
                userInfos.getElementsByClassName('box')[0].classList.remove('pulse');
                userInfos.getElementsByClassName('box')[2].classList.remove('pulse');
            }, 500);
        } else {
            // if the request is not successful, an alert box is displayed
            el.innerHTML = "Acheter (200 gemmes)";
            el.classList.add('pulse');
            setTimeout(function() {
                el.classList.remove('pulse');
            }, 250);
        }
    } catch (e) {
        console.log(e);
        open_alert("Erreur", "Une erreur est survenue, veuillez réessayer plus tard")
    }
}

window.onload = lives_counter();
/**
 * 
 * This function is used to generate a link to share a list
 * 
 * @function copy_list
 * @param {HTMLElement} el - The element that triggered the event.
 * @param {Event} event - The event object.
 * @param {number} list_id - The ID of the list to be shared.
 * 
 * @returns {void}
 */
const copyListButtons = document.getElementsByClassName('copy-list-button');
for (let i = 0; i < copyListButtons.length; i++) {
    copyListButtons[i].addEventListener('click', function(event) {
        copy_list(this, event, this.dataset.list_id);
    });
}
async function copy_list(el, event, list_id) {
    event.preventDefault();

    const copy_box = document.getElementsByClassName('copy-list')[0];
    copy_box.classList.add('active');
    document.getElementById('link').innerHTML = "<div class='loader'></div>";

    try {
        const response = await fetch(`/dashboard/list/get_link/${list_id}`);
        const data = await response.json();

        if (data.code != 200) {
            document.getElementById('link').innerHTML = "Erreur";
        } else {
            document.getElementById('link').dataset.link = window.location.protocol + "//" + window.location.hostname + data.link;
            document.getElementById('link').innerHTML = window.location.protocol + "//" + window.location.hostname + data.link;
        }
    } catch (e) {
        document.getElementById('link').innerHTML = "Erreur";
    }
}

/**
 * 
 * This function is used to copy the link to the clipboard
 * 
 * @function copy_link
 * @param {HTMLElement} el - The element that triggered the event.
 * @param {Event} event - The event object.
 * 
 * @returns {void}
 */
const copyLinkButtons = document.getElementById('copy-link-button');
copyLinkButtons.addEventListener('click', function(event) {
    copy_link(this, event);
});

function copy_link(el, event) {
    event.preventDefault();
    let link = document.getElementById("link");
    let copy_button = el;
    let text = link.dataset.link;
    if (text.length > 0) {
        navigator.clipboard.writeText(text).then(function() {
            copy_button.innerHTML = "Copié !";
        }, function() {
            copy_button.innerHTML = "Erreur";
        });
        setTimeout(function() {
            copy_button.innerHTML = "Copier";
            close_share_list(el, event);
        }, 2000);
    }
}

/**
 * 
 * This function is used to close the share list pop-up
 * 
 * @function close_share_list
 * @param {HTMLElement} el - The element that triggered the event.
 * @param {Event} event - The event object.
 * 
 * @returns {void}
 */
const closeCopyListButtons = document.getElementById('close-copy-list-button');
closeCopyListButtons.addEventListener('click', function(event) {
    close_share_list(this, event);
});

function close_share_list(el, event) {
    event.preventDefault();
    const copy_box = document.getElementsByClassName('copy-list')[0];
    copy_box.classList.remove('active');

    document.getElementById('link').dataset.link = "";
    document.getElementById('link').innerHTML = "";
}

/**
 * 
 * This function is used to animate following get elements in the url
 * 
 */
window.onload = async function() {
    setTimeout(function() {
        // Get the new list
        const newList = document.getElementsByClassName('new-list');
        if (newList.length > 0) {
            // Remove the new-list class
            newList[0].classList.remove('new-list');
            // Delete the URL parameters
            var url = window.location.href;
            var urlParts = url.split('?');
            window.history.replaceState({}, document.title, urlParts[0]);
        }
    }, 1500);

    // Get the gems, xp and lives info
    const gemsInfo = document.getElementById('gems-info');
    const xpInfo = document.getElementById('xp-info');
    const livesInfo = document.getElementById('lives-info');

    // Update the UI based on the gems
    gemsInfo.innerHTML = gemsInfo.dataset.value;

    // Check if there are URL parameters
    var params = new URLSearchParams(window.location.search);
    // If there are URL parameters
    if (params.has('end_lesson')) {
        if (params.has('xp') && params.has('lives')) {
            let xp = parseInt(params.get('xp'));
            let lives = parseInt(params.get('lives'));

            // Delete the URL parameters
            var url = window.location.href;
            var urlParts = url.split('?');
            window.history.replaceState({}, document.title, urlParts[0]);

            // Update the UI based on the xp and lives
            if (xp > 0) {
                xpInfo.parentElement.classList.add('pulse');
            }
            if (lives > 0) {
                livesInfo.parentElement.classList.add('pulse');
            }

            let actual_xp = parseInt(xpInfo.dataset.value) - xp;
            let actual_lives = parseInt(livesInfo.dataset.value) + lives;

            let total_xp = actual_xp + xp;
            let total_lives = actual_lives - lives;

            // Calculate the time between each xp and lives update
            let delay_xp = 1500 / xp;
            let delay_lives = 1500 / lives;

            xpInfo.innerHTML = actual_xp;
            livesInfo.innerHTML = actual_lives;

            // Increase the counter of xp and lives
            if (xp > 0) {
                var interval_xp = setInterval(() => {
                    actual_xp++;
                    xpInfo.innerHTML = actual_xp;
                    if (actual_xp === total_xp) {
                        clearInterval(interval_xp);
                        xpInfo.parentElement.classList.remove('pulse');
                    }
                }, delay_xp);
            }
            if (lives > 0) {
                var interval_lives = setInterval(() => {
                    actual_lives--;
                    livesInfo.innerHTML = actual_lives;
                    if (actual_lives === total_lives) {
                        clearInterval(interval_lives);
                        livesInfo.parentElement.classList.remove('pulse');
                    }
                }, delay_lives);
            }
        }

        // Open the game trail
        const listContainer = document.querySelector('[data-list_id="' + params.get('list_id') + '"]');
        await open_game_trail(listContainer);

        if (window.matchMedia("(max-width: 670px)").matches) {
            await new Promise(resolve => setTimeout(resolve, 750));
        }

        // Get the path of the user's list
        const pathPart = document.getElementsByClassName('path');
        var position = null;
        if (params.has('success') && params.get('success') == "True") {
            for (let i = 0; i < pathPart.length; i++) {
                if (pathPart[i].classList.contains('completed') == false) {
                    if (i > 0) {
                        position = i;
                        // Add the animation class to path that allow access to the next level
                        pathPart[i - 1].classList.add('animation');
                        break;
                    }
                }
            }
        }

        if (position == null && params.has('success') && params.get('success') == "True") {
            const gameTrail = document.getElementsByClassName('game-trail')[0];
            gameTrail.setAttribute('class', 'game-trail victory');
            setTimeout(function() {
                gameTrail.classList.remove('victory');
            }, 5000);
            const victorySound = new Audio('/static/sounds/victory-sound-effect.mp3');
            victorySound.play();
            return;
        }

        // Get the level box
        // Add animation to the level box
        if (params.has('success') && params.get('success') == "True") {
            const levelBox = document.getElementsByClassName('level-box')[position];
            levelBox.classList.remove('waiting');
            levelBox.classList.add('blocked');

            await new Promise(resolve => setTimeout(resolve, 500));
            levelBox.classList.remove('blocked');
            levelBox.classList.add('waiting');

            await new Promise(resolve => setTimeout(resolve, 500));
            levelBox.click();
        }
    } else {
        xpInfo.innerHTML = xpInfo.dataset.value;
        livesInfo.innerHTML = livesInfo.dataset.value;
    }
}


const closeGiftPupUpButton = document.getElementById('close-gift-pop-up-button');
if (closeGiftPupUpButton) {
    closeGiftPupUpButton.addEventListener('click', function(event) {
        close_gift_pop_up(this, event);
    });
}

function close_gift_pop_up(el, event) {
    event.preventDefault();
    document.getElementById('gift-pop-up-background').classList.remove('active');
    document.getElementById('gift-pop-up').classList.remove('active');
}