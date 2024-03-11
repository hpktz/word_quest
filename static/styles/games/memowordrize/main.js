const sessionID = document.getElementsByTagName('body')[0].dataset.session_id;
const pathContainer = document.getElementsByClassName('path-container')[0];
const items = document.getElementsByClassName('item');

const listeningHtml = '<div class="music-listener"><div class="bar"></div><div class="bar"></div><div class="bar"></div><div class="bar"></div><div class="bar"></div></div>';
const microphoneHtml = '<div class="micro-listener"><div class="point"></div></div>';

// window.onload = async function() {
//     if (pathContainer.dataset.current_path) {
//         // replace ' with " to parse the string
//         var charArray = pathContainer.dataset.current_path.replace(/'/g, '"');
//         var charArray = charArray.replace(/None/g, 'null');
//         var charArray = charArray.replace(/True/g, 'true');
//         var charArray = charArray.replace(/False/g, 'false');
//         var charArray = JSON.parse(charArray);
//         for (var i = 0; i < items.length; i++) {
//             items[i].removeEventListener('click', try_case);
//             items[i].classList.add('disabled');
//         }

//         charArray.forEach(async(char, index) => {
//             var toPlay = `/dashboard/games/memowordrize/${sessionID}/audio/${char.id}`;
//             var audio = new Audio(toPlay);
//             await new Promise(resolve => {
//                 audio.addEventListener('ended', resolve);
//                 audio.play();
//             });
//         });
//     }
// };

const infoButton = document.getElementById('show-path');
infoButton.addEventListener('click', see_path);

async function see_path() {
    try {
        const response = await fetch(`/dashboard/games/memowordrize/${sessionID}/see_path`);
        const data = await response.json();
        for (var i = 0; i < items.length; i++) {
            items[i].removeEventListener('click', try_case);
            items[i].classList.add('disabled');
        }
        var charArray = data.result.path;
        for (var i = 0; i < charArray.length - 1; i++) {
            var item = document.getElementById("item-" + charArray[i].position);
            item.classList.add('active');
            item.innerHTML = listeningHtml;
            var toPlay = `/dashboard/games/memowordrize/${sessionID}/audio/${charArray[i].id}`;
            var audio = new Audio(toPlay);
            await playAudioAndWait(audio);
            await new Promise(resolve => setTimeout(resolve, 200));
            item.classList.remove('active');
            item.innerHTML = "";
        };
        for (var i = 0; i < charArray.length - 1; i++) {
            var item = document.getElementById("item-" + charArray[i].position);
            item.classList.add('active');
            await new Promise(resolve => setTimeout(resolve, 100));
        }
        await new Promise(resolve => setTimeout(resolve, 1000));
        const activatedItems = document.querySelectorAll('.item.active');
        for (var i = 0; i < activatedItems.length; i++) {
            activatedItems[i].classList.remove('active');
            await new Promise(resolve => setTimeout(resolve, 100));
        }
    } catch (error) {
        console.error('Error:', error);
    }
}

async function playAudioAndWait(audio) {
    return new Promise(resolve => {
        audio.play();
        audio.addEventListener('ended', resolve);
    });
}

function try_case() {
    return;
}