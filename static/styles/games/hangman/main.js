const wordEl = document.getElementById('word');
const badLetter = document.getElementById('bad-letter');
const replayBtn = document.getElementById('play-button');
const popup = document.getElementById('popup-content');
const notif = document.getElementById('notification-content');
const finalMessage = document.getElementById('final-message');
const figurePart = document.querySelectorAll('.figure-part');
const remarque = document.getElementById('remarque');

const xpCounter = document.getElementById('xp');
const xpNotif = document.getElementById('xpnotif');
const animXp = document.getElementById('animation-xp');
const xpFinal = document.getElementById('XP-final');
const loader = document.getElementById('loader')


const addIndice = document.getElementById('add-indice');
const indiceContainer = document.getElementById('indice-container');

let nbrIndiceDiscover = 0


var Wordslength = 0
const finding = document.getElementById('word-finded')
var wordFind = 0
const recap = document.getElementById('recap');
const keyboard = document.querySelectorAll('.key-letter');

var a = 0;
var XpTotal = 0;
var nbrFaute = 0;
var xpwin = 5;

var goodLetters = [''];
var badLetters = [];

// Ajout des Indices en appuyant sur le + -------------------------------------------------------------------------------------
var indices = [
    { title: "Indice Rigolo", indice: "eh regarde comme cet indice est fou" },
    { title: "Hippoindice", indice: "eh regarde comme cet indice est hippodinguo" },
    { title: "Yo c'est Billy", indice: "un apagnan sucrée au sucre" },
]

async function newIndice() {
    try {
        const getIndice = await fetch('/dashboard/games/hangman/session/askhint');

        var currentIndice = await getIndice.json();
        xpwin = currentIndice["result"]['xp']

        var indice = document.createElement("div");
        var indiceTitle = document.createElement("p");
        var indiceContent = document.createElement("p");
        indice.classList.add('indice');
        indiceTitle.classList.add('name-indice');
        indiceContent.classList.add('indice-content');
        indiceTitle.innerText = currentIndice["result"]["title"];
        indiceContent.innerText = currentIndice["result"]["indice"];
        indice.appendChild(indiceTitle);
        indice.appendChild(indiceContent);
        indiceContainer.appendChild(indice);
        indice.style.animation = 'indicanim 1s ease-in-out forwards';
        addIndice.style.display = 'none'
        if (currentIndice["result"]["title"] == 'Le mot en francais'){
        indice.style.animation = 'indicanim 1s ease-in-out forwards'
        addIndice.style.display = "none"
        if (currentIndice["result"]["title"] == 'Le mot en francais') {
            addIndice.innerHTML = "Plus d'indice";
            addIndice.style.pointerEvents = 'none'
            addIndice.style.width = 'auto'
            addIndice.style.height = 'auto'
        }
        setTimeout(() => {
            indice.style.animation = 'depophint 0.5s ease-in-out forwards';
            setTimeout(() => {
                indice.style.display = 'none'
                addIndice.style.display = 'flex'
                indice.style.display = 'none'
            }, 600);
        }, 3000);  
        }
    } catch (error) {

    }
}


addIndice.addEventListener('click', async() => {
    newIndice();
    if (nbrIndiceDiscover == 3) {
        addIndice.innerHTML = `Plus d'indices`

    }
})

var word = '';
async function getWord() {

    try {
        const getWord = await fetch(`/dashboard/games/hangman/session/ask_word`);

        var selectWord = await getWord.json();
        word = selectWord["result"];

        console.log(selectWord["xptot"])
        if (word['word'] != undefined) {
            keyboard.forEach(e => {
                e.style.background = '#ccd77c';
                e.style.color = '#433831'
            });
            Wordslength++;
            addIndice.style.pointerEvents = 'auto'
            addIndice.innerHTML = '<img src="/static/icons/plus-30-white.png" alt="">'
            wordEl.innerHTML = `
                ${word['word']
                    .split('')
                    .map(
                        // le ? permet de faire un if et le : permet de faire un else
                        lettre => `
                            <span class="letter">
                                ${goodLetters.includes(lettre) ? lettre :
                                '' }
                            </span>
                        `
                    )
                    .join('')
                
                }`;
            const internalWord = wordEl.innerText.replace(/\n/g, '');
                if(internalWord == word['word'].toUpperCase()) {
                wordFind += 1
                xpNotif.innerHTML = '+' + String(xpwin);
                animXp.style.animation = 'Xpanim 1s ease-in-out forwards'
                XpTotal += xpwin
                xpCounter.innerHTML = String(XpTotal) + 'Xp';
                nextWord();
                }
        }
        else{
            finish();
        }
    } catch(error){
        finish();
    }
}

function afficheMot() {
    
    wordEl.innerHTML = `
        ${word['word']
            .split('')
            .map(
                // le ? permet de faire un if et le : permet de faire un else
                lettre => `
                    <span class="letter">
                        ${goodLetters.includes(lettre) ? lettre :
                        '' }
                    </span>
                `
            )
            .join('')

    }`;
    
    const internalWord = wordEl.innerText.replace(/\n/g, '');

    if(internalWord == word['word'].toUpperCase()) {
        wordFind += 1
        xpNotif.innerHTML = '+' + String(xpwin);
        animXp.style.animation = 'Xpanim 1s ease-in-out forwards'
        badLetters = 0
        XpTotal += xpwin
        xpCounter.innerHTML = String(XpTotal) + 'Xp';
        nextWord();
    }
}

function updateBadLetter(letter) {
    // afficher les mauvaises lettre
    badLetter.innerHTML = badLetter.innerHTML + `<span> ${letter}</span>` + ','
    
    // Afficher le bonhomme
    figurePart.forEach((partie, index) => {
        const erreurs = badLetters.length;
        if(index < erreurs) {
            partie.style.display = 'block'
        } else {
            partie.style.display = 'None'
        }
    })

    //Verifier si on a perdu

    if(badLetters.length == figurePart.length){
        figurePart.forEach((e) => {
            e.style.stroke = "red"
        })
        xpNotif.innerHTML = '+0';
        animXp.style.animation = 'Xpanim 1s ease-in-out forwards'
        nextWord()
    }
}

// affiche notif

function printNotification() {
    notif.classList.add('afficher');
    
    setTimeout(() => {
        notif.classList.remove('afficher');
    }, 2000);
}

// Event listeners
var isEventListener = true

setTimeout(() => {
    window.addEventListener('keydown', async e => {
        try{
            if (isEventListener) {
                if(badLetters.length < figurePart.length){

                    if(e.keyCode >= 65 && e.keyCode <= 90 || e.keyCode == 54){
                        isEventListener = false
                        loader.style.display = 'flex'
                        const check = await fetch(`/dashboard/games/hangman/session/check_letter/${e.key}`);
                        loader.style.display = 'none'
                        var checked = await check.json();
                        letter = e.key
                        keyboard.forEach(el => {
                            if(el.innerHTML == letter){
                                el.style.background = 'grey';
                                el.style.color = 'white';
                            }
                        });

                        if(checked["result"] == "already touch"){
                            printNotification();
                        }
                        else if(checked["result"]["True"]){
                            goodLetters = checked["result"]["good"]
                            afficheMot();
                        }
                        else{
                            badLetters = checked["result"]["bad"];
                            xpwin = checked["result"]["xp"];
                            updateBadLetter(letter);
                        }
                        isEventListener = true
                    }
                }
            }
        } catch(error){
            finish();
        }
    })
}, 5200);
keyboard.forEach(e => {
    e.addEventListener('click',async () => {
        try{    
            if (isEventListener) {
                if(badLetters.length < figurePart.length){
                    isEventListener = false
                    loader.style.display = 'flex'
                    const check = await fetch(`/dashboard/games/hangman/session/check_letter/${e.innerHTML}`);
                    loader.style.display = 'none'
                    var checked = await check.json();

                    if(checked["result"] == "already touch"){
                        printNotification();
                    }
                    else if(checked["result"]["True"]){
                        goodLetters = checked["result"]["good"]
                        afficheMot();
                        e.style.background = 'grey';
                        e.style.color = 'white';
                    }
                    else{
                        badLetters = checked["result"]["bad"];
                        xpwin = checked["result"]["xp"];
                        updateBadLetter(e.innerHTML);
                        e.style.background = 'grey';
                        e.style.color = 'white';
                    }
                    isEventListener = true
                    }
                }
        } catch(error){
            finish();
        }
        }
    )
});

replayBtn.addEventListener('click', () => {
    location.reload()
})
   

function nextWord(){
    setTimeout(async () => {
        try{
            indiceContainer.innerHTML = "";
            addIndice.style.display = 'flex'
            badLetter.innerHTML = null;
            figurePart.forEach((e) => {
                e.style.display = 'none';
                e.style.stroke = '#717744';
            })
            popup.style.display = 'none';
            const resetletters = await fetch(`/dashboard/games/hangman/session/reset`);

            reset = await resetletters.json()
            goodLetters = reset["result"]["good"];
            badLetters = reset["result"]["bad"];
            nbrFaute = 0;
            xpwin = 5;
            nbrFaute = 0;
            animXp.style.animation = 'disapear 0.5s ease-in-out forwards';
            getWord(); 
        } catch(error) {
            finish();
        }
    }, 1000);
}

async function finish(xp = XpTotal) {
    try {
        const request = await fetch(`/dashboard/games/hangman/session/finish`);
        const response = await request.json();
        setTimeout(() => {
            let xpinterval = setInterval(() => {
                if(a == XpTotal){
                    clearInterval(xpinterval);
                    a -= 1
                }
                a += 1
                xpFinal.innerHTML = '+' + String(a) + 'XP';    
            }, (1200/XpTotal));
            if (time < 0) {
                remarque.innerText = 'le temps est écoulé...';
            } else if(Wordslength*5 == XpTotal){
                remarque.innerText = 'Wouah! Parfait!';
            } else if(Wordslength*5 > XpTotal && XpTotal >= Wordslength*3){
                remarque.innerText = 'Bravo !';
            } else if(Wordslength*3 > XpTotal && XpTotal >= Wordslength*2){
                remarque.innerText = 'Mmmm...';
            } else {
                remarque.innerText = 'Dommage... Réessaye';
            }
            recap.style.display='flex'
            finding.innerHTML = String(wordFind) + '/' + String(Wordslength)
        }, 100);
    } catch (error) {
        window.location.href = '/dashboard'
    }
}
getWord();

const retryBtn = document.getElementById('retry');

retryBtn.addEventListener('click', () => {
    location.reload()
})




// RESPONSIVE -------------------------------------

const all = document.getElementById('all');
const figureContent = document.getElementById('svg');
const exit = document.getElementById('exit');
const separationLine = document.getElementById('sep');
const hints = document.getElementById('hint');
const other = document.getElementById('other');
const keyLetter = document.querySelectorAll('.key-letter');
const keyb = document.getElementById('keyboard');

setInterval(() => {
    if(window.innerWidth < window.innerHeight){
        all.classList.add('tablet-all')
        figureContent.classList.add('tablet-svg'); 
        exit.classList.add('tablet-exit'); 
        separationLine.classList.add('tablet-sep'); 
        hints.classList.add('tablet-hint'); 
        other.classList.add('tablet-other');
        keyLetter.forEach(e => {
            e.classList.add('tablet-kl'); 
        });
        keyb.classList.add('tablet-kb');
        if (document.getElementById('newhint') != null) {
            document.getElementById('newhint').classList.add('tablet-idc');
        }
    }
    else{
        all.classList.remove('tablet-all')
        figureContent.classList.remove('tablet-svg'); 
        exit.classList.remove('tablet-exit'); 
        separationLine.classList.remove('tablet-sep'); 
        hints.classList.remove('tablet-hint'); 
        other.classList.remove('tablet-other'); 
        keyLetter.forEach(e => {
            e.classList.remove('tablet-kl'); 
        });
        keyb.classList.remove('tablet-kb')
        if (document.getElementById('newhint') != null) {
            hint.classList.remove('tablet-idc');
        }
        
    }
    
}, 200);