const session_id = document.body.dataset.session_id;

async function getCard() {
    const getCards = await fetch(`/dashboard/games/memory/${session_id}/getCard`);
    var cardContent = await getCards.json();

    console.log(cardContent);

    shuf_emoji = cardContent['result']['nbr_cards'];

    for (var i = 0; i < shuf_emoji; i++) {
        let box = document.createElement('div');
        box.className = 'item';
        box.id = i
        document.getElementById('game').appendChild(box);

        box.onclick = async function() {
            this.classList.add('box_open');
            console.log(document.querySelectorAll('.box_open'));
            var boxId = this.id;
            
            const check_word = await fetch(`/dashboard/games/memory/${session_id}/check_word/${boxId}`);
            var checked = await check_word.json();
            
            this.innerText = checked['result']['innerHTML'] 



        }
    }
}

getCard();

const cardContent = ["1","1","2","2","3","3","4","4","5","5","6","6","7","7","8","8"]



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
    if(time < 0){
        remarque.innerText = 'Le temps est écoulé...'
    }
}
