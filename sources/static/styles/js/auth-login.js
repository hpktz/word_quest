var barre = document.getElementById("hidden-password-asset");
var oeil = document.getElementById("hidden-password-img");
var password = document.getElementById("login-password-input");

if (oeil) {
    oeil.addEventListener("click", function() {
        if (password.type == "text") {
            password.type = "password";
        } else {
            password.type = "text";
        }
        barre.classList.toggle("hidden");
    });
}

const form = document.getElementById("login-form");
form.addEventListener("submit", (event) => send_form(event));
/**
 * 
 * This function is responsible for sending the form
 * 
 * @function send_form
 * @param {*} event
 * @returns {void}
 */
function send_form(event) {
    event.preventDefault();
    document.getElementById("login-submit-button").innerHTML = '<div class="loader"></div>';
    document.getElementById("login-form").submit();
}