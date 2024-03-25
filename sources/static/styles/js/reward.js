const chestSoundUrl = '/static/sounds/chest-sound-effect.mp3';
const chestSound = new Audio(chestSoundUrl);
chestSound.volume = 0.2;
chestSound.load();

const chest = document.querySelector('.chest-container');
const overlay = document.querySelector('.overlay');
const body = document.querySelector('body');
chest.addEventListener('click', () => {
    chestSound.play();
    overlay.classList.add('active');
    chest.classList.add('active');
    body.classList.add('active');

    setTimeout(() => {
        const rewardAmount = document.getElementById('reward-amount');
        const amount = rewardAmount.innerHTML;
        rewardAmount.innerHTML = 0;
        var count = 0;
        var delay = 3000 / amount;
        console.log(delay);
        var interval = setInterval(() => {
            count++;
            rewardAmount.innerHTML = count;
            if (count === parseInt(amount)) {
                clearInterval(interval);
            }
        }, delay);
    }, 2000);

    setTimeout(() => {
        window.location.href = "/dashboard/quests";
    }, 9000);
});