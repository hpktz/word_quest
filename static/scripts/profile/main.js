function has_pressed_enter(event) {
    if (event.keyCode == 13) {
        search_user();
    }
}

async function search_user() {
    let search_input = document.getElementsByClassName("search-input")[0];
    let search_result = document.getElementsByClassName("search-result")[0];
    search_result.innerHTML = "<div class='loader'></div>";
    let search_text = search_input.value;
    if (search_text.length > 0) {
        try {
            const request = await fetch("/dashboard/profile/user/search/" + search_text);
            const response = await request.json();
            if (response.code == 200) {
                let users = response.result;
                let html = "";
                for (let i = 0; i < users.length; i++) {
                    html += "<a href='/dashboard/profile/user/" + users[i][0] + "' class='result-box'>";
                    html += "<img src='/static/imgs/profiles/" + users[i][2] + ".png' class='result-picture' alt='profile-picture'>";
                    html += "<div class='result-texts'>";
                    html += "<div class='name'>" + users[i][1] + "</div>";
                    html += "<div class='xp'>" + users[i][3] + " XP</div>";
                    html += "</div>";
                    html += "</a>";
                }
                search_result.innerHTML = html;
                for (let i = 0; i < users.length; i++) {
                    let el = document.getElementsByClassName("result-box")[i];
                    el.onclick = function(event) {
                        redirect(this, event);
                    }
                }
            } else {
                search_result.innerHTML = "<div class='info'>Aucun utilisateur trouvé.</div>"
            }
        } catch (error) {
            console.log(error);
            search_result.innerHTML = "<div class='info'>Une erreur s'est produite, veuillez réessayer plus tard.</div>"
        }
    } else {
        search_result.innerHTML = "";
    }
}

async function copy_list(el, event) {
    event.preventDefault();
    let id = el.dataset.id;
    el.innerHTML = "<div class='loader'></div>"
    el.removeAttribute("onclick");
    await new Promise(r => setTimeout(r, 1000));
    try {
        let request = await fetch("/dashboard/list/copy/" + id);
        let response = await request.json();
        if (response.code == 200) {
            el.innerHTML = "<img src='/static/icons/done-30-grey.png' class='not-clickable-zone' alt='logo'>";
        } else {
            el.innerHTML = "<img src='/static/icons/issue-100-red.png' class='not-clickable-zone' alt='logo'>";
        }
    } catch (error) {
        el.innerHTML = "<img src='/static/icons/issue-100-red.png' class='not-clickable-zone' alt='logo'>";
    }
}

async function subscribe(el) {
    let container = document.getElementsByClassName("subscription-container")[0];
    let id = el.dataset.id;
    let request = await fetch("/dashboard/profile/user/subscribe/" + id);
    let response = await request.json();
    try {
        if (response.code == 200) {
            container.innerHTML = `<div class="subscription"><div class="button"><div class="text"
                onclick="unsubscribe(this)" data-id="${id}">Se désabonner</div></div><div class="text">
                    A l'instant</div></div>`;
        }
    } catch (error) {
        console.log(error);
        open_alert("Erreur", "Une erreur s'est produite, veuillez réessayer plus tard.");
    }
}

async function unsubscribe(el) {
    let container = document.getElementsByClassName("subscription-container")[0];
    let id = el.dataset.id;
    try {
        let request = await fetch("/dashboard/profile/user/unsubscribe/" + id);
        let response = await request.json();
        if (response.code == 200) {
            container.innerHTML = `<div class="subscribe-button" onclick="subscribe(this)" data-id="${id}">
                <div class="text">S'abonner</div>
                </div>`;
        }
    } catch (error) {
        console.log(error);
        open_alert("Erreur", "Une erreur s'est produite, veuillez réessayer plus tard.");
    }
}

function switch_friend_list() {
    let menu_items = document.getElementsByClassName("item_sub");
    let contents = document.getElementsByClassName("content_sub");
    for (let i = 0; i < menu_items.length; i++) {
        menu_items[i].classList.toggle("active");
        contents[i].classList.toggle("active");
    }
}