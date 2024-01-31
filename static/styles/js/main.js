/**
 * Redirects the user to a specified URL.
 *  -> Used to make page changes seamless.
 * 
 * @function redirect
 * @param {HTMLElement} el - The element that triggered the redirect.
 * @param {Event} event - The event object associated with the redirect.
 * @returns {void}
 */
function redirect(el, event) {
    event.preventDefault();
    // Animate the page change.
    if (event.target.classList.contains('not-clickable-zone')) {
        return;
    }
    const href = el.getAttribute('href');
    const body = document.querySelector('body');
    const main = document.querySelector('main');
    const header = document.querySelector('header');
    if (window.matchMedia("(min-width: 670px)").matches) {
        body.style.gridTemplateColumns = '95px 1fr';
        main.style.opacity = '0';
        main.style.transform = 'translateX(1000px) rotate(0deg)';

        const responseLogo = document.querySelector('.responsive-logo');
        responseLogo.style.transform = 'rotate(180deg)';
    } else {
        body.removeAttribute('class');
        main.style.opacity = '0';
        main.style.transform = 'translateX(1000px)'
        header.style.width = '75px';
    }
    // Wait for the animation to finish before redirecting.
    setTimeout(function() {
        document.getElementsByClassName('main-loader')[0].classList.add('active');
        window.location.href = href;
    }, 510);
}

/**
 * Checks if the body element has the 'open' class.
 * 
 * @function is_open
 * @returns {boolean} True if the body element has the 'open' class, false otherwise.
 */
function is_open() {
    const body = document.querySelector('body');

    return body.classList.contains('open');
}

/**
 * Toggles the responsive behavior of the element.
 * 
 * @function responsive
 * @param {HTMLElement} el - The element to apply the responsive behavior to.
 * @param {Event} event - The event object.
 * @returns {void}
 */
function responsive(el, event) {
    event.preventDefault();

    const body = document.querySelector('body');

    if (body.classList.contains('open')) {
        body.removeAttribute('class');
    } else {
        body.setAttribute('class', 'open');
    }
}

/**
 * Toggles the phone menu open or closed.
 * 
 * @function open_menu_phone
 * @param {HTMLElement} el - The element that triggered the function.
 * @returns {void}
 */
function open_menu_phone(el) {
    const body = document.querySelector('body');

    if (body.classList.contains('phone-menu-open')) {
        body.removeAttribute('class');
    } else {
        body.setAttribute('class', 'phone-menu-open');
    }
}

/**
 * Closes the boxes by calling the close_info_box and close_lives functions.
 * 
 * @function close_boxes
 * @param {HTMLElement} el - The element that triggered the event.
 * @param {Event} event - The event object.
 * @returns {void}
 */
function close_boxes(el, event) {
    event.preventDefault();
    close_info_box(el, event);
    close_lives(el, event);
}

/**
 * Opens the info box and adds the necessary class to the body element.
 * 
 * @function open_info_box
 * @param {HTMLElement} el - The element that triggered the event.
 * @param {Event} event - The event object.
 * @returns {void}
 */
function open_info_box(el, event) {
    event.preventDefault();
    el.setAttribute('onclick', 'close_info_box(this, event)');
    const body = document.querySelector('body');
    body.setAttribute('class', 'info-section-phone-active');
}

/**
 * Closes the info box and restores the default behavior of the phone button.
 * 
 * @function close_info_box
 * @param {HTMLElement} el - The element that triggered the event.
 * @param {Event} event - The event object.
 * @returns {void}
 */
function close_info_box(el, event) {
    event.preventDefault();
    document.getElementById('info-section-phone-button').setAttribute('onclick', 'open_info_box(this, event)');
    const body = document.querySelector('body');
    body.removeAttribute('class');
}