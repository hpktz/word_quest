

const cardContent = ["1","1","2","2","3","3","4","4","5","5","6","6","7","7","8","8"]

// var shuf_emoji = cardContent.sort(() => (Math.random()));
const shuf_emoji = cardContent.sort(() => Math.random() - .5);

for (var i = 0; i < cardContent.length; i++) {
    let box = document.createElement('div');
    box.className = 'item';
    box.innerHTML = shuf_emoji[i];
    document.getElementById('game').appendChild(box);
    
    box.onclick = function() {
    this.classList.add('box_open')
    
    
    
        if(document.querySelectorAll('.box_open').length > 1){
            setTimeout(function(){
                if(document.querySelectorAll('.box_open')[0].innerHTML == 
                document.querySelectorAll('.box_open')[1].innerHTML){
                    document.querySelectorAll('.box_open')[0].classList.add
                    ('box_match')
                    document.querySelectorAll('.box_open')[1].classList.add
                    ('box_match')

                    document.querySelectorAll('.box_open')[1].classList.remove
                    ('box_open')
                    document.querySelectorAll('.box_open')[0].classList.remove
                    ('box_open')
                    if(document.querySelectorAll('.box_match').length == cardContent.length){
                        document.getElementById('win').classList.add('display-block-win')
                    }
                } 
                else{
                    
                    document.querySelectorAll('.box_open')[1].classList.remove
                    ('box_open')
                    document.querySelectorAll('.box_open')[0].classList.remove
                    ('box_open')
                }
            }, 400);
        }
    
    }
    document.getElementById('game').appendChild(box);
}


const recap = document.getElementById('recap');
const remarque = document.getElementById('remarque')

function finish() {
    recap.style.display = 'flex'
    if(time < 0){
        remarque.innerText = 'Le temps est écoulé...'
    }
}


let retry = document.getElementById('retry');

retry.onclick = function() {
    location.reload();
}