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
        levelInfoSubmitButton.innerHTML = "<a href='" + gameInfos[0].url + "/" + gameInfos[0].list_id + "' onclick='open_game(this, event)'>Rejouer</a>";
    } else if (gameInfos[0].status == "blocked") {
        levelInfoTitle.innerHTML = "Niveau bloqué";
        levelInfoText.innerHTML = "Terminez le niveau précédent pour débloquer ce niveau";
        levelInfoSubmitButton.innerHTML = "<p style='color:white;'>Bloqué</p>";
    } else {
        levelInfoSubmitButton.classList.add('start')
        levelInfoTitle.innerHTML = gameInfos[0].name;
        levelInfoText.innerHTML = gameInfos[0].short_desc;
        levelInfoSubmitButton.innerHTML = "<a href='" + gameInfos[0].url + "/" + gameInfos[0].list_id + "' onclick='open_game(this, event)'>Jouer</a>";
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
async function open_game_trail(el, event) {
    if (event.target.classList.contains('delete-zone')) {
        return;
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
                'Content-Type': 'application/json'
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
function open_lives(el) {
    const livesContainer = document.getElementsByClassName('lives-pop-up')[0];
    if (window.matchMedia("(max-width: 670px)").matches) {
        livesContainer.style.top = (el.offsetTop + 85) + "px";
        livesContainer.style.left = "calc(50% - 140px)";
        livesContainer.classList.add('active');

        const mainInfos = document.getElementsByClassName('main-infos')[0];
        mainInfos.classList.add('active');
    } else {
        livesContainer.style.top = (el.offsetTop + 65) + "px";
        console.log(el.offsetLeft);
        livesContainer.style.left = (el.offsetLeft + 75) + "px";
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
    const start_date = new Date(counter.dataset.time);
    const end_date = new Date(start_date.getTime() + 15 * 60 * 1000);

    // if the user has all his lives, the lives counter is updated and the function is stopped    
    if (parseInt(lives) == 5) {
        counter.innerHTML = "Vous avez toutes vos vies";
        counter.dataset.time = new Date();
        document.getElementById('life-purchase-button').style.display = "none";
        return;
    }

    var interval = setInterval(function() {
        // if there is a change in the number of lives, the lives counter is updated and the function is stopped
        if (counter.dataset.lives != lives) {
            lives_counter();
            return clearInterval(interval);
        }

        var now = new Date();
        var diff = end_date - now;

        // if the time is up, the lives counter is updated and the function is stopped
        if (diff < 0) {
            counter.dataset.lives = parseInt(lives) + 1;
            document.getElementById('lives-info').innerHTML = parseInt(lives) + 1;
            counter.dataset.time = new Date();
            const heartContainer = document.getElementsByClassName('heart-container')[0];
            heartContainer.getElementsByClassName('img')[lives].src = "/static/imgs/3d-red-heart.png";
            lives_counter();
            return clearInterval(interval);
        }
        var minutes = Math.floor(diff / 60000);
        var seconds = ((diff % 60000) / 1000).toFixed(0);

        counter.innerHTML = minutes + ":" + (seconds < 10 ? '0' : '') + seconds;
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
async function purchase_lives(el, event) {
    event.preventDefault();
    // request to purchase lives
    const response = await fetch('/dashboard/lives/purchase');
    document.getElementById('life-purchase-button').innerHTML = "<div class='loader'></div>";
    try {
        const data = await response.json();
        // if the request is successful, the lives counter is updated, and the UI is updated
        if (data.code == 200) {
            const counter = document.getElementById('lives-counter');
            const lives = counter.dataset.lives;
            const time = counter.dataset.time;
            counter.dataset.lives = parseInt(lives) + 1;
            counter.dataset.time = time;

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
            setTimeout(function() {
                userInfos.getElementsByClassName('box')[0].classList.remove('pulse');
                userInfos.getElementsByClassName('box')[2].classList.remove('pulse');
                document.getElementById('life-purchase-button').innerHTML = "Acheter (200 gemmes)";
            }, 2000);
        } else {
            // if the request is not successful, an alert box is displayed
            document.getElementById('life-purchase-button').innerHTML = "Acheter (200 gemmes)";
            document.getElementById('life-purchase-button').classList.add('pulse');
            setTimeout(function() {
                document.getElementById('life-purchase-button').classList.remove('pulse');
            }, 250);
        }
    } catch (e) {
        console.log(e);
        open_alert("Erreur", "Une erreur est survenue, veuillez réessayer plus tard")
    }
}

window.onload = lives_counter();