async function copy_list_frompopup(el) {
    el.innerHTML = "<div class='loader' style='width: 14px; height: 14px;'></div>"
    var id = el.dataset.id;
    try {
        let response = await fetch(`/dashboard/list/copy/${id}`);
        let data = await response.json();
        if (data.code == 200) {
            el.innerHTML = "Liste copiée"
            el.onclick = null
            el.style.cursor = "default"
            el.style.backgroundColor = "#555"
        } else {
            el.classList.add("pulse")
            setTimeout(() => {
                el.classList.remove("pulse")
            }, 250)
        }
    } catch (error) {
        el.classList.add("pulse")
        setTimeout(() => {
            el.classList.remove("pulse")
        }, 250)
    }
}

function close_pop_up(e) {
    e.preventDefault();
    document.getElementById('list-content-pop-up').innerHTML = "";
    popUp.classList.remove('active');
}

async function see_more(seeMoreButton, listContainerPopup) {
    seeMoreButton.classList.toggle("active");
    listContainerPopup.classList.toggle("active");
}