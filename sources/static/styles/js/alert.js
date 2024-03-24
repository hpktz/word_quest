/**
 * Opens an alert box with the specified title and description.
 * 
 * @function open_alert
 * @param {string} title - The title of the alert box.
 * @param {string} desc - The description of the alert box.
 * @returns {void}
 */
function open_alert(title, desc) {
    const alertBox = document.querySelector('.alert');
    const header = document.getElementsByTagName('header')[0];
    const main = document.getElementsByTagName('main')[0];

    alertBox.querySelector('.title').innerHTML = title;
    alertBox.querySelector('.text').innerHTML = desc;
    alertBox.classList.add('active');

    header.style.overflow = 'hidden';
    header.style.pointerEvents = 'none';

    main.style.overflow = 'hidden';
    main.style.pointerEvents = 'none';
}

/**
 * Closes the alert box.
 * 
 * @function close_alert
 * @param {HTMLElement} el - The element representing the alert box.
 * @param {Event} e - The event that triggered the function.
 * @returns {void}
 */
const alertButton = document.getElementById('alert-button');
alertButton.addEventListener('click', (e) => {
    e.preventDefault();
    close_alert(alertButton, e);
});

function close_alert(el, e) {
    const alertBox = document.querySelector('.alert');
    const header = document.getElementsByTagName('header')[0];
    const main = document.getElementsByTagName('main')[0];

    alertBox.classList.remove('active');

    header.style.removeProperty('overflow');
    header.style.removeProperty('pointer-events');

    main.style.removeProperty('overflow');
    main.style.removeProperty('pointer-events');
}