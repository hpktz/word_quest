const searchInput = document.getElementsByClassName("search-input")[0];
searchInput.addEventListener("keyup", function(event) {
    if (event.keyCode == 13) {
        search_user();
    }
});


/**
 * 
 * This fonction is used to search a user by his name (by sending a request to the server)
 * 
 * @function search_user
 * @returns {void}
 */
const searchButton = document.getElementById("search-button");
searchButton.addEventListener("click", search_user);
async function search_user() {
    let search_input = document.getElementsByClassName("search-input")[0];
    let search_result = document.getElementsByClassName("search-result")[0];

    // Display a loader to improve the user experience
    search_result.innerHTML = "<div class='loader'></div>";
    let search_text = search_input.value;

    // If the search input is not empty, we send a request to the server
    if (search_text.length > 0) {
        try {
            const request = await fetch("/dashboard/profile/user/search/" + search_text);
            const response = await request.json();
            // If the request is successful, we display the result
            if (response.code == 200) {
                let users = response.result;
                search_result.innerHTML = "";
                for (let i = 0; i < users.length; i++) {

                    // Construct the result box
                    var a = document.createElement('a');
                    a.href = '/dashboard/profile/user/' + users[i][0];
                    a.classList.add('result-box');
                    a.onclick = function(event) {
                        redirect(this, event);
                    }

                    var img = document.createElement('img');
                    img.src = '/static/imgs/profiles/' + users[i][2] + '.png';
                    img.classList.add('result-picture');
                    img.alt = 'profile-picture';
                    a.appendChild(img);

                    var div = document.createElement('div');
                    div.classList.add('result-texts');

                    var div_name = document.createElement('div');
                    div_name.classList.add('name');
                    div_name.innerHTML = users[i][1];
                    div.appendChild(div_name);

                    var div_xp = document.createElement('div');
                    div_xp.classList.add('xp');
                    div_xp.innerHTML = users[i][3] + ' XP';
                    div.appendChild(div_xp);

                    a.appendChild(div);
                    search_result.appendChild(a);
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

/**
 * 
 * This function is used to copy a list (by sending a request to the server)
 * 
 * @function copy_list
 * @param {HTMLElement} el - The button element
 * @param {Event} event - The event
 * @returns {void}
 * 
 */
const copyListButtons = document.getElementsByClassName("copy-list-button");
for (let i = 0; i < copyListButtons.length; i++) {
    copyListButtons[i].addEventListener("click", function(event) {
        copy_list(this, event);
    });
}
async function copy_list(el, event) {
    // Prevent the default behavior of the button
    event.preventDefault();
    let id = el.dataset.id;

    // Display a loader to improve the user experience
    el.innerHTML = "<div class='loader'></div>"
    el.removeAttribute("onclick");
    // Wait 1 second to display the loader
    await new Promise(r => setTimeout(r, 1000));
    try {
        // Send a request to the server
        let request = await fetch("/dashboard/list/copy/" + id);
        let response = await request.json();
        if (response.code == 200) { // If the request is successful
            el.innerHTML = "<img src='/static/icons/done-30-grey.png' class='not-clickable-zone' alt='logo'>";
        } else {
            el.innerHTML = "<img src='/static/icons/issue-100-red.png' class='not-clickable-zone' alt='logo'>";
        }
    } catch (error) {
        el.innerHTML = "<img src='/static/icons/issue-100-red.png' class='not-clickable-zone' alt='logo'>";
    }
}

/**
 * 
 * This function is used to subscribe to a user (by sending a request to the server)
 * 
 * @function subscribe
 * @param {HTMLElement} el - The button element
 * @returns {void}
 * 
 */
const subscribeButton = document.getElementById("subscribe-button");
if (subscribeButton) {
    subscribeButton.addEventListener("click", function() {
        subscribe(subscribeButton);
    });
}
async function subscribe(el) {
    let container = document.getElementsByClassName("subscription-container")[0];
    let id = el.dataset.id; // The id of the user to subscribe to
    try {
        // Send a request to the server
        let request = await fetch("/dashboard/profile/user/subscribe/" + id);
        let response = await request.json();
        if (response.code == 200) { // If the request is successful
            // Construct the unsubscription button
            let div = document.createElement("div");
            div.classList.add("subscription");
            div.onclick = function() {
                unsubscribe(this);
            }
            div.dataset.id = id;

            let div_button = document.createElement("div");
            div_button.classList.add("button");

            let div_text = document.createElement("div");
            div_text.classList.add("text");
            div_text.innerHTML = "Se désabonner";
            div_button.appendChild(div_text);
            div.appendChild(div_button);

            let div_text2 = document.createElement("div");
            div_text2.classList.add("text");
            div_text2.innerHTML = "A l'instant";
            div.appendChild(div_text2);

            container.innerHTML = "";
            container.appendChild(div);
        }
    } catch (error) {
        console.log(error);
        open_alert("Erreur", "Une erreur s'est produite, veuillez réessayer plus tard.");
    }
}

/**
 * 
 * This function is used to unsubscribe to a user (by sending a request to the server)
 * 
 * @function unsubscribe
 * @param {HTMLElement} el - The button element
 * @returns {void}
 * 
 */
const unsubscribeButton = document.getElementById("unsubscribe-button");
if (unsubscribeButton) {
    unsubscribeButton.addEventListener("click", function() {
        unsubscribe(unsubscribeButton);
    });
}
async function unsubscribe(el) {
    let container = document.getElementsByClassName("subscription-container")[0];
    let id = el.dataset.id; // The id of the user to unsubscribe to
    try {
        // Send a request to the server
        let request = await fetch("/dashboard/profile/user/unsubscribe/" + id);
        let response = await request.json();
        if (response.code == 200) {
            // Construct the subscription button
            let div = document.createElement("div");
            div.classList.add("subscribe-button");
            div.onclick = function() {
                subscribe(this);
            }
            div.dataset.id = id;

            let div_text = document.createElement("div");
            div_text.classList.add("text");
            div_text.innerHTML = "S'abonner";
            div.appendChild(div_text);

            container.innerHTML = "";
            container.appendChild(div);
        }
    } catch (error) {
        console.log(error);
        open_alert("Erreur", "Une erreur s'est produite, veuillez réessayer plus tard.");
    }
}

/**
 *
 * This function is used to improve the user experience. It displays the subscribers or the subscriptions of a user.
 * 
 * @function switch_sub
 * @returns {void}
 *  
 */
const firendList = document.getElementById("friend-list");
const friendListItems = firendList.getElementsByClassName("item");
for (let i = 0; i < friendListItems.length; i++) {
    friendListItems[i].addEventListener("click", function() {
        switch_friend_list();
    });
}

function switch_friend_list() {
    let menu_items = document.getElementsByClassName("item_sub");
    let contents = document.getElementsByClassName("content_sub");
    for (let i = 0; i < menu_items.length; i++) {
        menu_items[i].classList.toggle("active");
        contents[i].classList.toggle("active");
    }
}