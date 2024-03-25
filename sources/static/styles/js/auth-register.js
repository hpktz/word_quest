const continueButton = document.getElementById("continue-button");
continueButton.addEventListener("click", () => changePage());
/**
 * 
 * This function is responsible for changing the page
 * 
 * @function changePage
 * @returns {void} 
 */
function changePage() {
    const form = document.getElementById("signup-form");
    var birthday = form.year.value + "-" + form.month.value + "-" + form.day.value;
    console.log(birthday);
    if (form.name.value === "" || form.day.value === "" || form.month.value === "" || form.year.value === "" || form.email.value === "" || form.password.value === "") {
        if (!document.getElementById("login-form-main-alert")) {
            document.getElementById("front-alert").innerHTML = "<p id='login-form-main-alert'>Veuillez remplir tous les champs</p>";
            return;
        } else {
            document.getElementById("login-form-main-alert").innerHTML = "Veuillez remplir tous les champs";
            return;
        }
    } else if (birthday < "1920-01-01" || birthday > "2018-12-31") {
        if (!document.getElementById("login-form-main-alert")) {
            document.getElementById("front-alert").innerHTML = "<p id='login-form-main-alert'>La date de naissance n'est pas valide</p>";
            return;
        } else {
            document.getElementById("login-form-main-alert").innerHTML = "La date de naissance n'est pas valide";
            return;
        }
    } else if (!form.conditions.checked) {
        if (!document.getElementById("login-form-main-alert")) {
            document.getElementById("front-alert").innerHTML = "<p id='login-form-main-alert'>Veuillez accepter les conditions d'utilisation</p>";
            return;
        } else {
            document.getElementById("login-form-main-alert").innerHTML = "Veuillez accepter les conditions d'utilisation";
            return;
        }
    }
    if (document.getElementById("login-form-main-alert")) {
        document.getElementById("login-form-main-alert").remove();
    }
    document.getElementsByClassName("step-bar-fill")[0].style.width = "66%";
    document.getElementsByClassName("part-1")[0].style.left = "-150%";
    document.getElementsByClassName("part-2")[0].style.left = "0";
}

const form = document.getElementById("signup-form");
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
    document.getElementById("birthday").value = form.year.value + "-" + form.month.value + "-" + form.day.value;
    document.getElementById("signup-submit-button").innerHTML = '<div class="loader"></div>';
    document.getElementById("signup-form").submit();
}

const dateInput = document.getElementById("signup-birthday-input");
dateInput.addEventListener("focus", () => {
    dateInput.type = "date";
    if (dateInput.value === "") {
        dateInput.value = "2000-01-01";
    }
});
dateInput.addEventListener("blur", () => {
    if (dateInput.value === "2000-01-01") {
        dateInput.value = "";
        dateInput.type = "text";
    }
});