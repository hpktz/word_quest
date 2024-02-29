/**
 * 
 * This function is responsible for opening and closing the menu on mobile devices
 * 
 * @function header_menu_phone
 * @returns {void}
 * 
 */
function header_menu_phone() {
    let menu = document.getElementsByClassName('header-phone-button')[0];
    let header = document.getElementsByTagName('header')[0];
    if (menu.classList.contains('active')) {
        menu.classList.remove('active');
        header.classList.remove('active');
    } else {
        menu.classList.add('active');
        header.classList.add('active');
    }
}

/**
 * 
 * This function is responsible for changing the carousel image
 * 
 * @function switch_carousel
 * @param {HTMLElement} el - The element that was clicked
 * @param {string} pos - The wanted position
 * @returns {void}
 * 
 */

function switch_carousel(el, pos) {
    let slidesContainer = document.getElementsByClassName('carousel-container')[0];
    slidesContainer.setAttribute('class', 'carousel-container ' + pos);

    let items = document.querySelectorAll('.menu-container .item');
    items.forEach(item => {
        item.classList.remove('active');
    });
    el.classList.add('active');
}

/**
 * 
 * This function is responsible for changing the second carousel image
 * 
 * @function change_slide
 * @param {HTMLElement} el - The element that was clicked
 * @param {string} pos - The wanted position
 * @returns {void}
 * 
 */
function change_slide(el, pos) {
    let slidesContainer = document.getElementsByClassName('carousel-container')[1];
    slidesContainer.setAttribute('class', 'carousel-container ' + pos);

    let items = document.querySelectorAll('.carousel-infos .item');
    items.forEach(item => {
        item.classList.remove('active');
    });
    el.classList.add('active');
}

/**
 * 
 * This function is responsible for changing the second carousel image automatically
 * 
 * @function 
 * @returns {void}
 * 
 */
setInterval(() => {
    // Get the current position
    let slidesContainer = document.getElementsByClassName('carousel-container')[1];
    let pos = slidesContainer.getAttribute('class').split(' ')[1];
    pos = pos.replace('pos', '');

    // Change the position
    if (Number(pos) === 3) {
        pos = 1
    } else {
        pos = Number(pos) + 1;
    }
    pos = 'pos' + pos;

    // Check the next item
    let items = document.querySelectorAll('.carousel-infos .item');
    let activeItem = document.querySelector('.carousel-infos .item.active');
    let activeItemIndex = Array.prototype.indexOf.call(items, activeItem);
    let nextItemIndex = activeItemIndex + 1;
    // If the next item is the last one, go back to the first one
    if (nextItemIndex > items.length - 1) {
        nextItemIndex = 0;
    }
    let nextItem = items[nextItemIndex];
    // Call the function to change the slide
    change_slide(nextItem, pos);
}, 5000);