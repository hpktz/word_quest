async function search_word(e) {
    e.preventDefault();

    const defContainerHtml = await (await fetch('/dashboard/create/word-box')).text();
    const defContainerEmptyHtml = await (await fetch('/dashboard/create/empty-word-box')).text();

    const searchInput = document.querySelector('.search-bar').value.toLowerCase();
    const searchRequest = await fetch(`/dashboard/create/search/${searchInput}`);

    try {
        const searchResponse = await searchRequest.json();

        if (searchResponse.code === 200) {
            const definitionsContainer = document.querySelector('.words-container');
            definitionsContainer.innerHTML = "";

            for (let i = 0; i < searchResponse.result.length; i++) {
                definitionsContainer.innerHTML += defContainerHtml;

                const wordBox = document.getElementsByClassName('word-box')[i];
                wordBox.setAttribute('onclick', `ad_to_list(this)`);
                wordBox.setAttribute('data-word_id', `${searchResponse.result[i].id}`);
                
                document.getElementsByClassName('type')[i].innerHTML = searchResponse.result[i].type;
                document.getElementsByClassName('translation')[i].innerHTML = searchResponse.result[i].french_translation;

                if (searchResponse.result[i].examples.length > 0) {
                    document.getElementsByClassName('example')[i].innerHTML = `${searchResponse.result[i].examples[0]} - ${searchResponse.result[i].french_translation_examples[0]}`;
                }
            }
        } else {
            document.querySelector('.words-container').innerHTML = defContainerEmptyHtml;
        }
    } catch (error) {
        console.log(error);
        document.querySelector('.words-container').innerHTML = defContainerEmptyHtml;
    }
}

function check_key(e) {
    if (e.keyCode === 13) {
        search_word(e);
    }
}