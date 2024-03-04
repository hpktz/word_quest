const copyButton = document.getElementById("copy-button");
if (copyButton) {
    copyButton.addEventListener("click", function() {
        copy_list(copyButton);
    });
}
async function copy_list(el) {
    el.innerHTML = "<div class='loader'></div>"
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