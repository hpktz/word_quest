/**
 * 
 * This function is responsible for opening and closing the menu on mobile devices
 * 
 * @function header_menu_phone
 * @returns {void}
 * 
 */
const headerPhoneButton = document.getElementsByClassName('header-phone-button')[0];
headerPhoneButton.addEventListener('click', header_menu_phone);

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