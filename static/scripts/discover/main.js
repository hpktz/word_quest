const main = document.querySelector('.discover-main-container');

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
            response.data.forEach((el) => {
                let a = document.createElement('a');
                a.href = "/dashboard/profile/list/" + el.id;
                a.onclick = function(event) {
                    redirect(this, event);
                }
                a.classList.add('search-result-container');
                words = "";
                for (let i = 0; i < el.first_three_words.length; i++) {
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