/**
 * Performs a search based on the provided input value. (by checking the value of each list box)
 *  -> If the request is successful, the search results are displayed on the page.
 * 
 * @function search
 * @param {HTMLInputElement} el - The input element containing the search value.
 * @returns {void}
 */
const searchBar = document.getElementById('search-bar');
searchBar.addEventListener('keyup', function() {
    search(searchBar);
});

function search(el) {
    var search = el.value;

    const searchResults = document.querySelector('.search-results');
    searchResults.innerHTML = "";

    const listsBoxContainer = document.getElementsByClassName('list-box');
    if (search.length > 0) {
        var result = [];
        // browse the list boxes
        for (let i = 0; i < listsBoxContainer.length; i++) {
            // if the list box contains the search value
            if (listsBoxContainer[i].dataset.list_name.toLowerCase().includes(search.toLowerCase())) {
                // add the list box to the result array
                result.push({
                    id: listsBoxContainer[i].dataset.list_id,
                    title: listsBoxContainer[i].dataset.list_name
                });
            }
        }
        if (result.length > 0) {
            for (let i = 0; i < result.length; i++) {
                // highlight the search value in the result
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
                // when the user clicks on the search result, the corresponding list box is displayed
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