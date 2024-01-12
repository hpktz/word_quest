function search(el) {
    var search = el.value;

    const searchResults = document.querySelector('.search-results');
    searchResults.innerHTML = "";

    const listsBoxContainer = document.getElementsByClassName('list-box');
    if (search.length > 0) {
        var result = [];
        for (let i = 0; i < listsBoxContainer.length; i++) {
            if (listsBoxContainer[i].dataset.list_name.toLowerCase().includes(search.toLowerCase())) {
                result.push({
                    id: listsBoxContainer[i].dataset.list_id,
                    title: listsBoxContainer[i].dataset.list_name
                });
            }
        }
        if (result.length > 0) {
            for (let i = 0; i < result.length; i++) {
                var matchPart = result[i].title.toLowerCase().match(search.toLowerCase())[0];
                var matchIndex = result[i].title.toLowerCase().indexOf(matchPart);
                var matchLength = matchPart.length;
                var match = result[i].title.substring(matchIndex, matchIndex + matchLength);
                var title = result[i].title.replace(match, `<strong>${match}</strong>`);

                var element = null;
                for (let j = 0; j < listsBoxContainer.length; j++) {
                    if (listsBoxContainer[j].dataset.list_id == result[i].id) {
                        element = listsBoxContainer[j];
                    }
                }

                const container = document.createElement('p');
                container.classList.add('content');
                container.addEventListener('click', function(event) {
                    open_game_trail(element, event);
                });
                container.innerHTML = ">&nbsp;&nbsp;" + title;
                searchResults.appendChild(container);
            }
        } else {
            searchResults.innerHTML = "<p class='no-content'>Pas de résultat</p>";
        }
    }
}