const chest = document.querySelector('.chest-container');
const overlay = document.querySelector('.overlay');
chest.addEventListener('click', () => {
    overlay.classList.add('active');
    chest.classList.add('active');

    setTimeout(() => {
        window.location.href = "/dashboard/quests";
    }, 6000);
});