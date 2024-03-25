if (window.location.pathname != '/dashboard/help') {
    const prev = document.getElementById('prev');
    const next = document.getElementById('next');
    const carousel = document.querySelector('.carousel');

    prev.addEventListener('click', () => scroll('prev'));
    next.addEventListener('click', () => scroll('next'));

    function scroll(direction) {
        const carouselSize = carousel.clientWidth;
        const carouselChildren = carousel.children;
        let childInViewPort = 0;
        for (let i = 0; i < carouselChildren.length; i++) {
            if (carouselChildren[i].getBoundingClientRect().x < carouselSize) {
                childInViewPort = i;
            }
        }
        console.log(childInViewPort);
        if (childInViewPort === 1 && direction === 'prev') {
            prev.classList.add('disabled');
            next.classList.remove('disabled');
        } else if (childInViewPort === carouselChildren.length - 2 && direction === 'next') {
            next.classList.add('disabled');
            prev.classList.remove('disabled');
        } else {
            prev.classList.remove('disabled');
            next.classList.remove('disabled');
        }
        console.log(carouselSize, childInViewPort, carouselSize * (childInViewPort - 1));
        if (direction === 'prev' && childInViewPort > 0) {
            carousel.scrollTo({
                left: carouselSize * (childInViewPort - 1),
                behavior: 'smooth'
            });
        }
        if (direction === 'next' && childInViewPort < carouselChildren.length - 1) {
            carousel.scrollTo({
                left: carouselSize * (childInViewPort + 1),
                behavior: 'smooth'
            });
        }
    }
}

const a = document.getElementsByTagName('a');
for (let i = 0; i < a.length; i++) {
    a[i].addEventListener('click', (e) => {
        e.preventDefault();
        const entryAnimation = document.getElementsByClassName('entry-animation');
        for (let i = 0; i < entryAnimation.length; i++) {
            entryAnimation[i].classList.add('exit-animation');
        }
        setTimeout(() => {
            window.location.href = a[i].href;
        }, 500);
    });
}


/**
 * Reload the page when the back button is pressed.
 * 
 * @event pageshow
 * @param {Event} event - The event object.
 * @returns {void}
 */
window.addEventListener('pageshow', function(event) {
    if (event.persisted) {
        window.location.reload();
    }
});