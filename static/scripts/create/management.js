async function ad_to_list(el) {
    try {
        const wordId = el.getAttribute('data-word_id');
        const wordsBox = document.querySelector(`.list-container`);
        const wordInListHtml = await (await fetch('/dashboard/create/word-in-list')).text();
        const request = await fetch(`/dashboard/create/add/${wordId}`);
        const response = await request.json();
        if (response.code === 200) {
            wordsBox.innerHTML += wordInListHtml;
            wordInList = document.getElementsByClassName('word-in-list-box')[document.getElementsByClassName('word-in-list-box').length - 1];
            wordInList.getElementsByClassName('word')[0].innerHTML = response.result.word;
            wordInList.getElementsByClassName('type')[0].innerHTML = response.result.type;
            wordInList.getElementsByClassName('trash-logo-clickable-el')[0].setAttribute('onclick', 'remove_from_list(this, ' + response.result.id + ')');
        } else {
            alert('An error occured. Please try again later.');
        }
    } catch (error) {
        console.log(error);
        alert('An error occured. Please try again later.');
    }

}