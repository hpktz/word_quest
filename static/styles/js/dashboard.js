function open_game_info(el) {
    var gameInfos = el.dataset.game_infos;
    gameInfos = gameInfos.replace(/'/g, '"');
    gameInfos = JSON.parse(gameInfos);

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

    setTimeout(function() {
        const overlay = document.getElementsByClassName('overlay-load-game')[0];
        var rect = levelInfoSubmitButton.getBoundingClientRect();

        var middleX = rect.left + (rect.width / 2);
        var middleY = rect.top + (rect.height / 2);

        overlay.style.left = middleX + "px";
        overlay.style.top = middleY + "px";
    }, 301);
}

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

async function open_game_trail(el, event) {
    console.log(event.target);
    if (event.target.classList.contains('delete-zone')) {
        return;
    }

    if (is_open()) {
        const arrow = document.getElementsByClassName('close-logo')[0].children[0];
        responsive(arrow, event);
    }

    const body = document.querySelector('body');
    body.setAttribute('class', 'phone-trail-opened')

    const trailContainer = document.getElementsByClassName('games-trail')[0];
    trailContainer.classList.add('active');

    const listsContainer = document.getElementsByClassName('list-box');
    var position = 0;
    for (let i = 0; i < listsContainer.length; i++) {
        if (listsContainer[i] == el) {
            position = i;
        }
    }

    const id = el.dataset.list_id;
    const color = position % 3;
    const response = await fetch(`/dashboard/games/${id}`);
    const data = await response.text();
    const gamesTrail = document.getElementsByClassName('games-trail')[0];
    gamesTrail.innerHTML = data;
    gamesTrail.dataset.color = color;

    const listsBoxContainer = document.getElementsByClassName('list-box');
    for (let i = 0; i < listsBoxContainer.length; i++) {
        listsBoxContainer[i].classList.remove('selected');
    }
    el.classList.add('selected');
}

function close_game_trail(el, event) {
    event.preventDefault();
    const trailContainer = document.getElementsByClassName('games-trail')[0];
    trailContainer.classList.remove('active');
    setTimeout(function() {
        const body = document.querySelector('body');
        body.classList.remove('phone-trail-opened')
    }, 1000);
}

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

function delete_list(el, event, id) {
    event.preventDefault();

    const deleteListPopUp = document.getElementsByClassName('delete-list')[0];
    deleteListPopUp.classList.add('active');
    var link = "/dashboard/delete/" + id;
    document.getElementById('delete-list-redirect').setAttribute('href', link);
}

function close_delete_list(el, event) {
    event.preventDefault();

    const deleteListPopUp = document.getElementsByClassName('delete-list')[0];
    deleteListPopUp.classList.remove('active');
}

function open_lives(el) {
    const livesContainer = document.getElementsByClassName('lives-pop-up')[0]; 
    livesContainer.style.top = (el.offsetTop + 40) + "px";
    livesContainer.style.left = (el.offsetLeft-230) + "px";
    el.classList.add('active');
}

function close_lives(el, e) {
    e.preventDefault();
    if (e.target.classList.contains('lives-zone')) {
        return;
    }
    const livesBox = document.getElementById('lives-box');
    livesBox.classList.remove('active');
    const livesContainer = document.getElementsByClassName('lives-pop-up')[0]; 
    livesContainer.style.top = "-300px";
}

async function lives_counter() {
    const counter = document.getElementById('lives-counter');
    const lives = counter.dataset.lives;
    const start_date = new Date(counter.dataset.time);
    const end_date = new Date(start_date.getTime() + 15 * 60 * 1000);

    
    if (parseInt(lives) == 5) {
        counter.innerHTML = "Vous avez toutes vos vies";
        counter.dataset.time = new Date();
        document.getElementById('life-purchase-button').style.display = "none";
        return;
    }

    var interval = setInterval(function() {
        if (counter.dataset.lives != lives) {
            lives_counter();
            return clearInterval(interval);
        }
        var now = new Date();
        var diff = end_date - now;
        console.log(diff);
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

    interval;
}

async function purchase_lives(el, event) {
    event.preventDefault();
    const response = await fetch('/dashboard/lives/purchase');
    try {
        const data = await response.json();
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

            const gemsInfo = document.getElementById('gems-info');
            gemsInfo.innerHTML = data.gems;
            userInfos.getElementsByClassName('box')[0].classList.add('pulse');
            setTimeout(function() {
                userInfos.getElementsByClassName('box')[0].classList.remove('pulse');
                userInfos.getElementsByClassName('box')[2].classList.remove('pulse');
            }, 2000);
        } else {
            open_alert("Achat impossible", "Vous n'avez peut-être pas assez de points pour acheter des vies");
        }
    } catch (e) {
        console.log(e);
        open_alert("Erreur", "Une erreur est survenue, veuillez réessayer plus tard")
    }
}

window.onload = lives_counter();