const text = document.getElementById('countdown-game');


var time =  1000;
function countDown() {
    const minute = Math.floor(time / 60);
    const seconds = time%60;
    if (minute >= 1){
        text.innerText = minute + 'm ' + seconds + 's';
    }
    else{
        text.innerText = seconds + ' s';
    }
    time = time - 1;
}
countDown();

const begin = document.getElementById('begin');
i = 4
begin.innerText = 'Prêt ?'
const begining = setInterval(() => {
    if(i != 1){
        begin.innerText = i-1
    }
    if(i == 1){
        begin.innerText = 'Go !'
    }
    if(i == 0){
        clearInterval(begining)
        document.getElementById('begining').classList.add('display-none')
        const counter = setInterval(() => {
            countDown();
            if (time < 10){
                text.classList.add('timer-animation');
            }
            if (time < 0){
                clearInterval(counter);
                finish()
            }
            if(document.getElementById('recap').style.display == "flex"){
                clearInterval(counter);
            }
            var retry = document.getElementById('retry');

            retry.onclick = function() {
                location.reload();
            }


        }, 1000);
    }
    i = i - 1

}, 1000);




