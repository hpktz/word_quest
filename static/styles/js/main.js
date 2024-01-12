function redirect(el, event) {
    event.preventDefault();
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
    setTimeout(function() {
        window.location.href = href;
    }, 510);
}

function is_open() {
    const body = document.querySelector('body');

    return body.classList.contains('open');
}

function responsive(el, event) {
    event.preventDefault();

    const body = document.querySelector('body');

    if (body.classList.contains('open')) {
        body.removeAttribute('class');
    } else {
        body.setAttribute('class', 'open');
    }
}

function open_menu_phone(el) {
    const body = document.querySelector('body');

    if (body.classList.contains('phone-menu-open')) {
        body.removeAttribute('class');
    } else {
        body.setAttribute('class', 'phone-menu-open');
    }
}

function close_boxes(el, event) {
    event.preventDefault();
    close_info_box(el, event);
    close_lives(el, event);
}

function open_info_box(el, event) {
    event.preventDefault();
    el.setAttribute('onclick', 'close_info_box(this, event)');
    const body = document.querySelector('body');
    body.setAttribute('class', 'info-section-phone-active');
}

function close_info_box(el, event) {
    event.preventDefault();
    document.getElementById('info-section-phone-button').setAttribute('onclick', 'open_info_box(this, event)');
    const body = document.querySelector('body');
    body.removeAttribute('class');
}