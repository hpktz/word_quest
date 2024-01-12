async function ad_to_list(el) {
    try {
        const wordId = el.getAttribute('data-word_id');
        const wordsBox = document.querySelector(`.list-container`);
        const wordInListHtml = await (await fetch('/dashboard/create/word-in-list')).text();
        const wordsContainer = document.querySelector('.words-container');
        const defContainerEmptyHtml = await (await fetch('/dashboard/create/empty-word-box')).text();

        const request = await fetch(`/dashboard/create/add/${wordId}`);
        const response = await request.json();
        if (response.code === 200) {
            if (wordsBox.dataset.items_count === '0') {
                wordsBox.innerHTML = '';
            }
            wordsBox.innerHTML += wordInListHtml;
            wordInList = document.getElementsByClassName('word-in-list-box')[document.getElementsByClassName('word-in-list-box').length - 1];
            wordInList.id = response.result.id;
            wordInList.getElementsByClassName('word')[0].innerHTML = '<span title="'+response.result.french_translation+'">'+response.result.word+'</span>';
            wordInList.getElementsByClassName('type')[0].innerHTML = response.result.type;
            wordInList.getElementsByClassName('trash-logo-clickable-el')[0].setAttribute('onclick', 'remove_from_list(this,event, "' + response.result.id + '")');
            
            wordsBox.dataset.items_count = parseInt(wordsBox.dataset.items_count) + 1;
            wordsContainer.innerHTML = defContainerEmptyHtml;
            document.getElementsByClassName('empty-word-box')[0].getElementsByClassName('text')[0].innerHTML = 'Recherchez un autre mot si vous le souhaitez.';
        } else {
            open_alert('Problème', 'Une erreur est survenue. Veuillez réessayer plus tard.');
        }
    } catch (error) {
        open_alert('Problème', 'Une erreur est survenue. Veuillez réessayer plus tard.');
    }

}

async function remove_from_list(el, e, wordId) {
    e.preventDefault();
    try {
        const wordsBox = document.querySelector(`.list-container`);
        const wordInListHtml = document.getElementById(wordId);
        wordInListHtml.getElementsByClassName('load')[0].classList.add('active');

        const request = await fetch(`/dashboard/create/remove/${wordId}`);
        const response = await request.json();
        if (response.code === 200) {
            wordsBox.removeChild(wordInListHtml);
            wordsBox.dataset.items_count = parseInt(wordsBox.dataset.items_count) - 1;
            if (wordsBox.dataset.items_count === '0') {
                wordsBox.innerHTML = '<div class="no-word-in-list">Vous n&apos;avez pas de mot dans votre liste</div>';
            }
        } else {
            open_alert('Problème', 'Une erreur est survenue. Veuillez réessayer plus tard.');
        }
    } catch (error) {
        console.log(error);        
        open_alert('Problème', 'Une erreur est survenue. Veuillez réessayer plus tard.');
    }
}

async function create_list() {
    try {
        const listInfos = document.getElementById('list-infos');
        const body = {
            name: listInfos.name.value,
            desc: listInfos.desc.value,
            time: listInfos.time.value,
            xp: listInfos.xp.value,
            game: listInfos.game.value,
            reminder: listInfos.reminder.checked,
            stats: listInfos.stats.checked,
            public: listInfos.public.checked,
        }

        const request = await fetch('/dashboard/create/create-list', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body)
        });
        const response = await request.json();
        const errorMess = document.getElementsByClassName('error-message')[0];
        if (response.code === 200) {
            window.location.href = '/dashboard?new_list=true';
        } else if (response.code === 400) {
            errorMess.innerHTML = response.message;
        } else {
            open_alert('Problème', 'Un problème est survenu lors de la création de la liste. Veuillez réessayer plus tard.');
        }
    } catch (error) {
        console.log(error);
        open_alert('Problème', 'Un problème est survenu lors de la création de la liste. Veuillez réessayer plus tard.');
    }
}