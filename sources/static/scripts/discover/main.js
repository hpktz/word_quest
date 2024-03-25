const main = document.querySelector('.discover-main-container');
const popUp = document.getElementById('list-pop-up');

/**
 * 
 * This function is used to switch between the lists created by the community and by Word Quest.
 * 
 * @function switch_list
 * @param {HTMLElement} el - The element that triggered the function.
 * @param {Event} event - The event object.
 * @returns {void}
 * 
 */
const switchs = document.querySelectorAll('.switch');
switchs.forEach((el) => {
    el.addEventListener('change', (e) => switch_list(el, e));
});

function switch_list(el, event) {
    let list = document.querySelectorAll('.list-to-switch');
    list.forEach((el) => {
        el.classList.remove('active');
    });
    let index = el.switch.value - 1;
    list[index].classList.add('active');
    setInterval(() => {
        main.dispatchEvent(new Event('scroll'));
    }, 250);
}

/**
 * 
 * This function is used to copy a list. (by sending a POST request to the server)
 * 
 * @function copy_list
 * @param {HTMLElement} el - The element that triggered the function.
 * @param {Event} event - The event object.
 * @returns {void}
 * 
 */
const copyButtons = document.querySelectorAll('.copy-button');
copyButtons.forEach((el) => {
    el.addEventListener('click', (e) => copy_list(el, e));
});
async function copy_list(el, event) {
    event.preventDefault();
    let id = el.dataset.id;
    el.innerHTML = "<div class='loader'></div>";
    // Remove the event listener to avoid multiple requests
    el.style.pointerEvents = "none";
    // Add a delay to make the loader visible
    await new Promise(r => setTimeout(r, 1000));
    try {
        // Send a POST request to the server
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

/**
 * 
 * This function is used to like a list. (by sending a POST request to the server)
 * 
 * @function like
 * @param {HTMLElement} el - The element that triggered the function.   
 * @param {Event} event - The event object.
 * @returns {void}
 * 
 */
const heartContainers = document.querySelectorAll('.heart-container');
heartContainers.forEach((el) => {
    el.addEventListener('click', (e) => like(el, e));
});
async function like(el, event) {
    event.preventDefault();
    el.classList.toggle('active');
    let id = el.dataset.id;
    try {
        let request = await fetch("/dashboard/list/like/" + id, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": document.getElementById('csrf_token').value // Send the CSRF token to improve security
            }
        });
        let response = await request.json();
        if (response.code != 200) {
            el.classList.toggle('active');
        }
    } catch (error) {
        el.classList.toggle('active');
    }
}

/**
 * 
 * This function is used to search for a list. (by sending a GET request to the server)
 * 
 * @function redirect
 * @param {HTMLElement} el - The element that triggered the redirect.
 * @param {Event} event - The event object associated 
 * @returns {void}
 * 
 */
const searchForm = document.getElementById('search-form');
searchForm.addEventListener('submit', (e) => search_list(searchForm, e));

async function search_list(el, event) {
    event.preventDefault();
    let search = el.search.value;
    let container = document.querySelector('.search-results');
    container.innerHTML = "<div class='loader'></div>";
    try {
        // Send a GET request to the server
        let request = await fetch("/dashboard/list/search/" + search);
        let response = await request.json();
        if (response.code == 200) {
            container.innerHTML = "";
            console.log(response.data);
            response.data.forEach((el) => {
                let a = document.createElement('a');
                a.onclick = async function() {
                    try {
                        event.preventDefault();
                        popUp.classList.add('active');
                        document.getElementById('list-title-pop-up').innerText = el.list_title;

                        document.getElementById('list-content-pop-up').innerHTML = "<div class='loader'><div class='load'></div></div>";
                        const response = await fetch('/dashboard/profile/list/' + el.list_id + '');
                        const list = await response.text();
                        document.getElementById('list-content-pop-up').innerHTML = list;
                        const copyButton = document.getElementById("copy-button");
                        if (copyButton) {
                            copyButton.addEventListener("click", function() {
                                copy_list_frompopup(copyButton);
                            });
                        }
                        const seeMoreButton = document.getElementById("see-more-button");
                        const listContainerPopup = document.getElementsByClassName("list-container-popup")[0];
                        if (seeMoreButton) {
                            seeMoreButton.addEventListener("click", function() {
                                see_more(seeMoreButton, listContainerPopup);
                            });
                        }
                        const closePopUp = document.getElementById('close-list-pop-up-button');
                        closePopUp.addEventListener('click', function(event) {
                            close_pop_up(event);
                        });
                    } catch (error) {
                        console.log(error);
                    }
                }
                a.classList.add('search-result-container');
                words = "";
                for (let i = 0; i < 3; i++) {
                    words += el.first_three_words[i].word + ", ";
                }
                words += "..."
                a.innerHTML = "<div class='name'>" + el.list_title + "</div><div class='creator'>" + el.user_name + "</div><div class='list'>" + words + "</div>";
                container.appendChild(a);
            });
        } else {
            container.innerHTML = "<div class='text'>Aucune liste n'a été trouvée</div>";
        }
    } catch (error) {
        console.log(error);
        container.innerHTML = "<div class='text'>Aucune liste n'a été trouvée</div>";
    }
}

/**
 * 
 * This function is used to detect if an element is visible on the screen.
 * 
 * @function is_visible
 * @param {HTMLElement} el - The element to check.
 * @returns {boolean} True if the element is visible, false otherwise.
 * 
 */
main.addEventListener('scroll', function() {
    let elements = document.querySelectorAll('.list-container');
    elements.forEach((el) => {
        var top = el.getBoundingClientRect().top;
        var bottom = el.getBoundingClientRect().bottom;
        var left = el.getBoundingClientRect().left;
        var right = el.getBoundingClientRect().right;
        if (top < window.innerHeight && bottom > 0 && left < window.innerWidth && right > 0) {
            el.classList.add('visible');
        } else {
            el.classList.remove('visible');
        }
    });
});


window.onload = function() {
    const lists = document.getElementsByClassName('list-container-box');
    for (let i = 0; i < lists.length; i++) {
        lists[i].addEventListener('click', function(event) {
            display_pop_up(lists[i], event);
        });
    }
}

/**
 * 
 * This function is used to display a pop-up when a list is clicked.
 * 
 * @function display_pop_up
 * @param {HTMLElement} el - The element that triggered the function.
 * @param {Event} event - The event object.
 * @returns {void}
 * 
 */
async function display_pop_up(el, event) {
    if (event.target.classList.contains('not-clickable-zone')) {
        return;
    }
    try {
        event.preventDefault();
        document.getElementById('list-content-pop-up').innerHTML = "<div class='loader-container'><div class='load'></div></div>";
        let elCenterX = el.getBoundingClientRect().left + el.offsetWidth / 2;
        let elCenterY = el.getBoundingClientRect().top + el.offsetHeight / 2;
        popUp.style.transition = "0s";
        popUp.style.opacity = 0;
        popUp.style.left = elCenterX + "px";
        popUp.style.top = elCenterY + "px";
        popUp.style.width = el.offsetWidth + "px";
        popUp.style.height = el.offsetHeight + "px";
        popUp.style.transform = "translate(-50%, -50%)";
        popUp.style.zIndex = -1;
        el.style.transform = "scale(0.5)";
        await new Promise(r => setTimeout(r, 50));
        popUp.style.transition = "0.5s";
        popUp.style.opacity = 1;
        popUp.style.transform = "translate(-50%, -50%) scale(1)";
        popUp.style.zIndex = 1;
        el.style.transform = "scale(1)";
        
        const listUrl = el.href;
        const response = await fetch(listUrl);
        const list = await response.text();
        
        await new Promise(r => setTimeout(r, 250));
        popUp.removeAttribute('style');
        popUp.classList.add('active');
        const listTitle = el.getElementsByClassName('title')[0].innerText;
        document.getElementById('list-title-pop-up').innerText = listTitle;
        document.getElementById('list-content-pop-up').innerHTML = list;
        const copyButton = document.getElementById("copy-button");
        if (copyButton) {
            copyButton.addEventListener("click", function() {
                copy_list_frompopup(copyButton);
            });
        }
        const seeMoreButton = document.getElementById("see-more-button");
        const listContainerPopup = document.getElementsByClassName("list-container-popup")[0];
        if (seeMoreButton) {
            seeMoreButton.addEventListener("click", function() {
                see_more(seeMoreButton, listContainerPopup);
            });
        }
        const closePopUp = document.getElementById('close-list-pop-up-button');
        closePopUp.addEventListener('click', function(event) {
            close_pop_up(event);
        });
    } catch (error) {
        popUp.classList.remove('active');
        console.log(error);
    }
}

const likeFilterButton = document.getElementsByClassName('show-liked-filter')[0];
likeFilterButton.addEventListener('click', function() {
    show_liked_filter(likeFilterButton);
});

/**
 * 
 * This function is used to display the lists liked by the user.
 * 
 * @function show_liked_filter
 * @param {HTMLElement} el - The element that triggered the function.
 * @returns {void}
 * 
 */
function show_liked_filter(el) {
    var lists = document.getElementsByClassName('list-container-box');
    lists = Array.from(lists);
    if (el.classList.contains('active')) {
        el.classList.remove('active');
        lists.forEach(function(list) {
            list.style.display = "block";
        });
        document.getElementsByClassName('trend-list')[0].getElementsByClassName('no-list')[0].style.display = "none";
        document.getElementsByClassName('word-quest-list')[0].getElementsByClassName('no-list')[0].style.display = "none";
    } else {
        el.classList.add('active');
        var countRecommandation = 0;
        var countWordQuest = 0;
        lists.forEach(function(list) {
            var heartContainer = list.getElementsByClassName('heart-container')[0];
            if (heartContainer.classList.contains('active')) {
                list.style.display = "block";
                if (list.parentElement.classList.contains('trend-list')) {
                    countRecommandation++;
                } else {
                    countWordQuest++;
                }
            } else {
                list.style.display = "none";
            }
        });
        if (countRecommandation == 0) {
            document.getElementsByClassName('trend-list')[0].getElementsByClassName('no-list')[0].style.display = "block";
        }
        if (countWordQuest == 0) {
            document.getElementsByClassName('word-quest-list')[0].getElementsByClassName('no-list')[0].style.display = "block";
        }
    }
}