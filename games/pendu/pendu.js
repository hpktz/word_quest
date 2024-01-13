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



const addIndice = document.getElementById('add-indice');
const indiceContainer = document.getElementById('indice-container');

let nbrIndiceDiscover = 0

// ---------------ZONE A REMPLACER PAR LES MOTS DE L'UTILISATEUR------------------------------------------------------------------------------------------------------------
const words = ['maison','tour','chateau','entourloupette'];
// -------------------------------------------------------------------------------------------------------------------------------------------------------------------------
const Wordslength = words.length
const finding = document.getElementById('word-finded')
var wordFind = 0
const recap = document.getElementById('recap');

var a = 0;
var XpTotal = 0;
var xpwin = 5;
var nbrFaute = 0;

var goodLetter = [''];
var badLetters = [];

// Ajout des Indices en appuyant sur le + -------------------------------------------------------------------------------------
var indices = [
    {title:"Indice Rigolo" ,indice: "eh regarde comme cet indice est fou"},
    {title:"Hippoindice" ,indice: "eh regarde comme cet indice est hippodinguo"},
    {title:"Yo c'est Billy" ,indice: "un apagnan sucrée au sucre"},
]

function newIndice() {
    var indice = document.createElement("div");
    var indiceTitle = document.createElement("p");
    var indiceContent = document.createElement("p");
    indice.classList.add('indice');
    indiceTitle.classList.add('name-indice');
    indiceContent.classList.add('indice-content');
    indiceTitle.innerText = indices[nbrIndiceDiscover].title;
    indiceContent.innerText = indices[nbrIndiceDiscover].indice;
    indice.appendChild(indiceTitle);
    indice.appendChild(indiceContent);
    indiceContainer.appendChild(indice);
    indice.style.animation = 'indicanim 1s ease-in-out forwards'
}

addIndice.addEventListener('click', () => {
    newIndice();
    nbrIndiceDiscover ++;
    xpwin = xpwin - 1
    if(nbrIndiceDiscover == 3){
        addIndice.style.display = 'none'
    }
})


function selectedWord() {
    let selectWord = words[Math.floor(Math.random() * words.length)];
    words.splice(words.indexOf(selectWord),1)
    return selectWord
}
// Affiche le mot caché
let word = selectedWord()
function afficheMot() {
    
    wordEl.innerHTML = `
        ${word
            .split('')
            .map(
                // le ? permet de faire un if et le : permet de faire un else
                lettre => `
                    <span class="letter">
                        ${goodLetter.includes(lettre) ? lettre :
                        '' }
                    </span>
                `
            )
            .join('')
        
        }
    
    `;
    
    const internalWord = wordEl.innerText.replace(/\n/g, '');
    // le (/\n/g, '') va permettre de remplacer tout (g = global) les retour à la ligne par '' c'est à dire supprimer les retour à la ligne

    if(internalWord == word.toUpperCase()) {
        if(words.length == 0){
            finish();
        } else{
            nextWord();
        }
        wordFind += 1
        xpNotif.innerHTML = '+' + String(xpwin);
        animXp.style.animation = 'Xpanim 1s ease-in-out forwards'
        XpTotal += xpwin
        xpCounter.innerHTML = String(XpTotal) + 'Xp';
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
        if(words.length == 0){
            finish();    
        } else {
            xpNotif.innerHTML = '+0';
            animXp.style.animation = 'Xpanim 1s ease-in-out forwards'
            nextWord()
        }
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
setTimeout(() => {
    window.addEventListener('keydown', e => {
        if(badLetters.length < figurePart.length){
            if(e.keyCode >= 65 && e.keyCode <= 90 || e.keyCode == 54){
                const letter = e.key;

                if(word.includes(letter)){

                    if(!goodLetter.includes(letter)){
                        goodLetter.push(letter);

                        afficheMot();
                    } else {
                        printNotification();
                    }
                } else {
                    if(!badLetters.includes(letter)){
                        badLetters.push(letter);
                        nbrFaute += 1;
                        if(nbrFaute >=2 && nbrFaute <4){
                            xpwin = 3
                        } else if(nbrFaute == 4){
                            xpwin = 2
                        } else if(nbrFaute == 5){
                            xpwin = 1
                        }else if(nbrFaute == 6){
                            xpwin = 0
                        }
                        updateBadLetter(letter);
                    } else {
                        printNotification(letter);
                    }
                }
            }
        }
    })
}, 5200);

replayBtn.addEventListener('click', () => {
    location.reload()
})
   

function nextWord(){
    
    setTimeout(() => {
        nbrIndiceDiscover = 0;
        indiceContainer.innerHTML = "";
        addIndice.style.display = 'flex'
        badLetter.innerHTML = null;
        figurePart.forEach((e) => {
            e.style.display = 'none';
            e.style.stroke = '#717744';
        })
        popup.style.display = 'none';
        word = selectedWord();
        goodLetter = [''];
        badLetters = [];
        nbrFaute = 0;
        xpwin = 5;
        nbrFaute = 0;
        animXp.style.animation = 'disapear 0.5s ease-in-out forwards';
        afficheMot();
    }, 1000);
}

function finish() {
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
}
afficheMot();


const retryBtn = document.getElementById('retry');

retryBtn.addEventListener('click', () => {
    location.reload()
})

