/**
 * Performs a word search and displays the search results on the page. (by sending a request to the server)
 *  -> This function is called when the user clicks on the search button.
 *  -> This function shows a loader while the search is being performed.
 *  -> This function displays the search results in a word box.
 * 
 * @async
 * @function search_word
 * @param {Event} e - The event object.
 * @returns {Promise<void>} - A promise that resolves once the search results are displayed.
 * @throws {Error} - If an error occurs during the search process.
 */
const searchButton = document.getElementById('search-button');
const languageSwitch = document.getElementById('language-switch');
searchButton.addEventListener('click', (e) => search_word(e));
async function search_word(e) {
    e.preventDefault();

    const definitionsContainer = document.querySelector('.words-container');
    definitionsContainer.innerHTML = '<div class="load"><div class="loader"></div></div>';

    // get the html of the word box
    const defContainerHtml = await (await fetch('/dashboard/create/word-box')).text();
    const defContainerEmptyHtml = await (await fetch('/dashboard/create/empty-word-box')).text();

    const searchInput = document.querySelector('.search-bar').value.toLowerCase();
    // get the search results (by making a request to the server)

    const language = languageSwitch.language.value;
    const searchRequest = await fetch(`/dashboard/create/search/${language}/${searchInput}`);

    try {
        const searchResponse = await searchRequest.json();
        if (searchResponse.code === 200) {
            definitionsContainer.innerHTML = "";
            // display the search results by replacing the loader with the word box
            // and by changing the content of the word box
            for (let i = 0; i < searchResponse.result.length; i++) {
                definitionsContainer.innerHTML += defContainerHtml;

                const wordBox = document.getElementsByClassName('word-box')[i];
                wordBox.setAttribute('data-word_id', `${searchResponse.result[i].id}`);

                document.getElementsByClassName('type')[i].innerHTML = searchResponse.result[i].type;
                document.getElementsByClassName('translation')[i].innerHTML = language == 'en' ? searchResponse.result[i].french_translation : searchResponse.result[i].word;

                if (searchResponse.result[i].examples.length > 0) {
                    if (language == 'en') {
                        document.getElementsByClassName('example')[i].innerHTML = `${searchResponse.result[i].examples[0]} - ${searchResponse.result[i].french_translation_examples[0]}`;
                    } else {
                        document.getElementsByClassName('example')[i].innerHTML = `${searchResponse.result[i].french_translation_examples[0]} - ${searchResponse.result[i].examples[0]}`;
                    }
                }
            }
        } else {
            // if there is no search result, the word box is replaced by the "no word box" message
            document.querySelector('.words-container').innerHTML = defContainerEmptyHtml;
        }
    } catch (error) {
        // if an error occurs during the search process, the word box is replaced by the "no word box" message
        document.querySelector('.words-container').innerHTML = defContainerEmptyHtml;
    }
}

/**
 * Checks if the enter key was pressed.
 * -> If the enter key was pressed, the search_word function is called.
 * 
 * @function check_key
 * @param {Event} e - The event object.
 * @returns {void}
 */
const searchBar = document.getElementById('search-bar');
searchBar.addEventListener('keypress', (e) => check_key(e));

function check_key(e) {
    if (e.keyCode === 13) {
        search_word(e);
    }
}