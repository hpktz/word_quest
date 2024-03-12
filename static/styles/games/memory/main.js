const session_id = document.body.dataset.session_id;
const successAudioUrl = '/static/sounds/success-sound-effect.mp3';
const successAudio = new Audio(successAudioUrl);
successAudio.volume = 1;
successAudio.load();
const flipCardAudioUrl = '/static/sounds/flip-card-sound-effect.mp3';
const flipCardAudio = new Audio(flipCardAudioUrl);
flipCardAudio.volume = 1;
flipCardAudio.load();

async function getCard() {
    const getCards = await fetch(`/dashboard/games/memory/${session_id}/getCard`);
    var cardContent = await getCards.json();

    console.log(cardContent);

    nbrCards = cardContent['result']['nbr_cards'];

    for (var i = 0; i < nbrCards; i++) {
        let box = document.createElement('div');
        box.className = 'item';
        box.id = i
        document.getElementById('game').appendChild(box);
        setTimeout(() => {
            box.onclick = async function() {
                flipCardAudio.play();
                var boxId = this.id;
                document.querySelectorAll('.item').forEach(element => {
                    element.style.pointerEvents = 'none'
                });
                const check_word = await fetch(`/dashboard/games/memory/${session_id}/check_word/${boxId}`);
                var checked = await check_word.json();
                this.innerText = checked['result']['innerHTML']
                this.classList.add('box_open');
                document.querySelectorAll('.item').forEach(element => {
                    if (element.classList[1] != '.box_open') {
                        element.style.pointerEvents = 'auto'
                    }
                });
                if (document.querySelectorAll('.box_open').length == 2) {
                        element.style.pointerEvents = 'none'
                    setTimeout(() => {
                        document.querySelectorAll('.item').forEach(element => {
                            if (element.classList[1] == 'box_open') {
                                element.style.pointerEvents = 'none'
                            } else {
                                element.style.pointerEvents = 'auto'
                            }

                        });
                        if (checked['result']['checking']) {
                            document.querySelectorAll('.box_open').forEach(element => {
                                element.classList.add('box_match')
                                successAudio.play();
                            });

                            document.querySelectorAll('.box_open')[1].classList.remove('box_open')
                            document.querySelectorAll('.box_open')[0].classList.remove('box_open')
                            flipCardAudio.play();
                        } else {
                            document.querySelectorAll('.box_open').forEach(element => {
                                element.style.pointerEvents = 'auto'
                            });
                            document.querySelectorAll('.box_open')[1].innerHTML = ""
                            document.querySelectorAll('.box_open')[0].innerHTML = ""
                            document.querySelectorAll('.box_open')[1].classList.remove('box_open')
                            document.querySelectorAll('.box_open')[0].classList.remove('box_open')
                            flipCardAudio.play();
                        }
                        document.querySelectorAll('.item').forEach(element => {
                            if (element.classList[1] == 'box_match') {
                                element.style.pointerEvents = 'none'
                            }
                        });
                    }, 500);
                }
                if (checked.code == 201) {
                    end_game(checked.result.xp, checked.result.time, checked.result.lost_lives)
                }
            }
        }, 5000);
    }
}

getCard();

/**
 * 
 * This function is used to display the end pop-up
 * 
 * @function timer
 * @param {Event} event - The event that triggered the function
 * 
 * @returns {void} - The result of the function
 */
var timer = setInterval(async() => {
    // Get the time element
    const time = document.getElementById('time');
    // Decrease the time by 1
    time.innerHTML = parseInt(time.innerHTML) - 1;

    // If the timer is over
    if (time.textContent == 0) {
        clearInterval(timer);
        try {
            // Check the status of the game
            const response = await fetch(`/dashboard/games/memory/${session_id}/check_status`);
            const data = await response.json();
            console.log(data);
            // If the game is over
            if (data.code == 201) {
                // End the game
                end_game(data.result.xp, data.result.time, data.result.lost_lives);
            }
        } catch (error) {
            window.location.href = '/dashboard/errors/500';
        }
    }
}, 1000);

timer;



// for (var i = 0; i < cardContent.length; i++) {
//     let box = document.createElement('div');
//     box.className = 'item';
//     box.innerHTML = shuf_emoji[i];
//     document.getElementById('game').appendChild(box);

//     box.onclick = function() {
//     this.classList.add('box_open')



//         if(document.querySelectorAll('.box_open').length > 1){
//             setTimeout(function(){
//                 if(document.querySelectorAll('.box_open')[0].innerHTML ==
//                 document.querySelectorAll('.box_open')[1].innerHTML){
//                     document.querySelectorAll('.box_open')[0].classList.add
//                     ('box_match')
//                     document.querySelectorAll('.box_open')[1].classList.add
//                     ('box_match')


//                     document.querySelectorAll('.box_open')[1].classList.remove
//                     ('box_open')
//                     document.querySelectorAll('.box_open')[0].classList.remove
//                     ('box_open')
//                     if(document.querySelectorAll('.box_match').length == cardContent.length){
//                         document.getElementById('win').classList.add('display-block-win')
//                     }
//                 }
//                 else{

//                     document.querySelectorAll('.box_open')[1].classList.remove
//                     ('box_open')
//                     document.querySelectorAll('.box_open')[0].classList.remove
//                     ('box_open')
//                 }
//             }, 400);
//         }

//     }
//     document.getElementById('game').appendChild(box);
// }




const recap = document.getElementById('recap');
const remarque = document.getElementById('remarque')


function finish() {
    recap.style.display = 'flex'
    if (time < 0) {
        remarque.innerText = 'Le temps est écoulé...'
    }
}