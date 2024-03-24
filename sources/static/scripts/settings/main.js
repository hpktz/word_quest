const csrf_token = document.getElementById("csrf_token").value;
/**
 * 
 * This function is use to change the profile picture of the user (design)
 * 
 * @function profile_picture_container
 * @param {HTMLElement} radio
 * @returns {void}
 * 
 */
const profilePictureRadios = document.querySelectorAll(".profile-picture-radio");
profilePictureRadios.forEach(radio => radio.addEventListener("click", () => profile_picture_container(radio)));

function profile_picture_container(radio) {
    const container = radio.parentElement.parentElement;
    if (container.classList.contains("active")) {
        // Wait for the animation to end
        setTimeout(() => {
            container.classList.remove("active");
        }, 301);
    } else {
        container.classList.add("active");
    }
}

/**
 * 
 * This function is used to activate the button when something is written in the input
 * 
 * @function set_button
 * @param {HTMLElement} form
 * @returns {void}
 * 
 */
function set_button(form) {
    const button = form.querySelector(".submit-button");
    button.classList.add("active");
}

/**
 * 
 * This function is used to open the otp verification popup
 * 
 * @function popup_verification_email
 * @returns {void}
 */
function popup_verification_email() {
    const popup = document.querySelector(".pop-up.otp_check");
    popup.classList.add("active");
}

/**
 * 
 * This function is used to close the otp verification popup
 * 
 * @function close_popup_verification_email
 * @param {HTMLElement} el - The element
 * @param {Event} event - The event
 * @returns {void}
 * 
 */
const closePopupVerificationEmail = document.getElementById("close-popup-verification-email");
closePopupVerificationEmail.addEventListener("click", (e) => close_popup_verification_email(closePopupVerificationEmail, e));

function close_popup_verification_email(el = null, event = null) {
    if (event) {
        event.preventDefault();
    }
    const popup = document.querySelector(".pop-up.otp_check");
    popup.classList.remove("active");
}

/**
 * 
 * This function is used to check if the otp is correct (by sending a request to the server)
 * 
 * @function verification_email
 * @param {HTMLElement} form - The form
 * @param {Event} event - The event
 * @returns {void}
 * 
 */
const otpForm = document.getElementById("otp-form");
otpForm.addEventListener("submit", (e) => verification_email(otpForm, e));
otpForm.addEventListener("input", (e) => set_button(otpForm));

async function verification_email(form, event) {
    // Prevent the form to be submitted
    event.preventDefault();
    const alert = document.getElementById("otp-alert-mess");
    if (form.button.classList.contains("active")) {
        // Activate the loader to improve the user experience
        form.button.innerHTML = "<div class='loader'></div>";
    } else {
        return;
    }
    // Get the code
    const code = form.querySelector("#code").value;
    if (code === "") {
        // If the code is empty, activate the error animation
        form.button.innerHTML = "Vérifier";
        form.button.classList.remove("active");
        form.button.classList.add("pulse");
        alert.innerHTML = "<p class='alert-mess'>Veuillez remplir le champ</p>";
        setTimeout(() => {
            form.button.classList.remove("pulse");
        }, 250);
        return;
    }
    try {
        // Send the request to the server
        const response = await fetch("/dashboard/settings/verify-email/" + code);
        const data = await response.json();
        if (data.code == 200) { // If the code is correct
            // Show a success message to the user
            form.button.innerHTML = "Vérifié";
            form.button.classList.remove("active");
            alert.innerHTML = `<p class='success-mess'>${data.message}</p>`;;
            setTimeout(() => {
                form.button.innerHTML = "Vérifier";
                alert.innerHTML = "";
                close_popup_verification_email();
                document.getElementById("settings-section-alert-mess").innerHTML = `<p class='success-mess'>${data.message}</p>`;
                setTimeout(() => {
                    document.getElementById("settings-section-alert-mess").innerHTML = "";
                }, 2000);
            }, 2000);
        } else { // If the code is incorrect
            // Activate the error animation
            form.button.innerHTML = "Vérifier";
            form.button.classList.remove("active");
            form.button.classList.add("pulse");
            alert.innerHTML = `<p class='alert-mess'>${data.message}</p>`;
            setTimeout(() => {
                form.button.classList.remove("pulse");
            }, 250);
        }
    } catch (error) {
        // If an error occured
        // Show an alert to the user
        form.button.innerHTML = "Vérifier";
        form.button.classList.remove("active");
        open_alert("Une erreur est survenue", "Une erreur est survenue, veuillez réessayer plus tard");
    }
}

/**
 * 
 * This function is used to send the user infos to the server
 * 
 * @function send_user_infos
 * @param {HTMLElement} form - The form
 * @param {Event} event - The event
 * @returns {void}
 * 
 */
const userInfosForm = document.getElementById("user-infos-form");
userInfosForm.addEventListener("submit", (e) => send_user_infos(userInfosForm, e));
userInfosForm.addEventListener("input", (e) => set_button(userInfosForm));

async function send_user_infos(form, event) {
    // Prevent the form to be submitted
    event.preventDefault();
    const alert = document.getElementById("settings-section-alert-mess");
    if (form.button.classList.contains("active")) {
        form.button.innerHTML = "<div class='loader'></div>";
    } else {
        return;
    }
    // Get the username and the email
    const username = form.querySelector("#username").value;
    const email = form.querySelector("#email").value;
    if (username === "" || email === "") {
        // If the username or the email is empty, activate the error animation
        form.button.innerHTML = "Enregistrer";
        form.button.classList.remove("active");
        form.button.classList.add("pulse");
        alert.innerHTML = "<p class='alert-mess'>Veuillez remplir tous les champs</p>";
        setTimeout(() => {
            form.button.classList.remove("pulse");
        }, 250);
        return;
    }
    try {
        // Send the request to the server
        const response = await fetch("/dashboard/settings/change-user-infos", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrf_token // Add the csrf token to the headers to prevent csrf attacks
            },
            body: JSON.stringify({
                username: username,
                email: email,
                profilePicture: form.profilePicture.value
            })
        });
        // Get the response
        const data = await response.json();
        if (data.code == 200) {
            form.button.innerHTML = "Enregistré";
            form.button.classList.remove("active");
            alert.innerHTML = `<p class='success-mess'>${data.message}</p>`;;
            setTimeout(() => {
                form.button.innerHTML = "Enregistrer";
                alert.innerHTML = "";
            }, 2000);
        } else if (data.code == 201) {
            form.button.innerHTML = "Enregistrer";
            form.button.classList.remove("active");
            popup_verification_email();
        } else {
            form.button.innerHTML = "Enregistrer";
            form.button.classList.remove("active");
            form.button.classList.add("pulse");
            alert.innerHTML = `<p class='alert-mess'>${data.message}</p>`;
            setTimeout(() => {
                form.button.classList.remove("pulse");
            }, 250);
        }
    } catch (error) {
        form.button.innerHTML = "Enregistrer";
        form.button.classList.remove("active");
        open_alert("Une erreur est survenue", "Une erreur est survenue, veuillez réessayer plus tard");
    }
}

/**
 * 
 * This function is used to send the user password to the server
 * 
 * @function send_security_form
 * @param {HTMLElement} form - The form
 * @param {Event} event - The event
 * @returns {void}
 * 
 */
const passwordForm = document.getElementById("password-form");
passwordForm.addEventListener("submit", (e) => send_security_form(passwordForm, e));
passwordForm.addEventListener("input", (e) => set_button(passwordForm));
async function send_security_form(form, event) {
    // Prevent the form to be submitted
    event.preventDefault();
    const alert = document.getElementById("password-section-alert-mess");
    if (form.button.classList.contains("active")) {
        form.button.innerHTML = "<div class='loader'></div>";
    } else {
        return;
    }
    // Get the old password, the new password and the mfa
    const old_password = form.querySelector("#old-password").value;
    const new_password = form.querySelector("#new-password").value;
    const mfa = form.querySelector("#mfa").checked;
    try {
        const response = await fetch("/dashboard/settings/change-password", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrf_token // Add the csrf token to the headers to prevent csrf attacks
            },
            body: JSON.stringify({
                old_password: old_password,
                new_password: new_password,
                mfa: mfa
            })
        });
        const data = await response.json();
        // Get the response
        if (data.code == 200) { // If the password has been changed
            form.button.innerHTML = "Enregistré";
            form.button.classList.remove("active");
            alert.innerHTML = `<p class='success-mess'>${data.message}</p>`;;
            setTimeout(() => {
                form.button.innerHTML = "Enregistrer";
                alert.innerHTML = "";
            }, 2000);
        } else {
            form.button.innerHTML = "Enregistrer";
            form.button.classList.remove("active");
            form.button.classList.add("pulse");
            alert.innerHTML = `<p class='alert-mess'>${data.message}</p>`;
            setTimeout(() => {
                form.button.classList.remove("pulse");
            }, 250);
        }
    } catch (error) {
        form.button.innerHTML = "Enregistrer";
        form.button.classList.remove("active");
        open_alert("Une erreur est survenue", "Une erreur est survenue, veuillez réessayer plus tard");
    }
}

/**
 * 
 * This function is used to change the visibility of the user profile
 * 
 * @function change_visibility
 * @param {HTMLElement} checkbox - The checkbox
 * @param {Event} event - The event
 * @returns {void}
 * 
 */
const visibilityCheckbox = document.getElementById("visibility");
visibilityCheckbox.addEventListener("change", (e) => change_visibility(visibilityCheckbox, e));
async function change_visibility(checkbox, event) {
    // Activate the loader to improve the user experience
    checkbox.labels[0].innerHTML = `<div class="loader-container"><div class="loader"></div></div>`;
    let checked = checkbox.checked;
    let visibility = checked ? 1 : 0;

    try {
        // Send the request to the server
        const response = await fetch("/dashboard/settings/change-visibility/" + visibility, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrf_token
            }
        });
        const data = await response.json();
        if (data.code == 200) { // If the visibility has been changed
            if (checked) {
                checkbox.checked = false;
                checkbox.labels[0].innerHTML = `<div class="toggle-button"></div>`;
                setTimeout(() => {
                    checkbox.checked = true;
                }, 100);
            } else {
                checkbox.checked = true;
                checkbox.labels[0].innerHTML = `<div class="toggle-button"></div>`;
                setTimeout(() => {
                    checkbox.checked = false;
                }, 100);
            }
        } else {
            checkbox.labels[0].innerHTML = `<div class="toggle-button"></div>`;
            open_alert("Une erreur est survenue", "Une erreur est survenue, veuillez réessayer plus tard");
        }
    } catch (error) {
        checkbox.labels[0].innerHTML = `<div class="toggle-button"></div>`;
        open_alert("Une erreur est survenue", "Une erreur est survenue, veuillez réessayer plus tard");
    }
}

/**
 * 
 * This function is used to open the delete account popup
 * 
 * @function popup_delete
 * @returns {void}
 * 
 */
const popupDeleteButton = document.getElementById("popup-delete-button");
popupDeleteButton.addEventListener("click", () => popup_delete());

function popup_delete() {
    const popup = document.querySelector(".pop-up.delete_account");
    popup.classList.add("active");
}

/**
 * 
 * This function is used to close the delete account popup
 * 
 * @function close_popup_delete
 * @param {HTMLElement} el - The element
 * @param {Event} event - The event
 * @returns {void}
 * 
 */
const closePopupDelete = document.getElementById("close-popup-delete");
closePopupDelete.addEventListener("click", (e) => close_popup_delete(closePopupDelete, e));

function close_popup_delete(el = null, event = null) {
    if (event) {
        event.preventDefault();
    }
    const popup = document.querySelector(".pop-up.delete_account");
    popup.classList.remove("active");
}

/**
 * 
 * This function is used to delete the user account
 * 
 * @function delete_account
 * @param {HTMLElement} button - The button
 * @returns {void}
 * 
 */
const deleteAccountButton = document.getElementById("delete-account-button");
deleteAccountButton.addEventListener("click", () => delete_account(deleteAccountButton));
async function delete_account(button) {
    const input = document.getElementById("delete");
    if (input.value === "supprimer mon compte") {
        button.innerHTML = "<div class='loader'></div>";
        try {
            // Send the request to the server
            const response = await fetch("/dashboard/settings/delete-account", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": csrf_token
                }
            });
            const data = await response.json();
            if (data.code == 200) {
                // If the account has been deleted
                window.location.href = "/";
            } else {
                button.classList.add("pulse");
                setTimeout(() => {
                    button.classList.remove("pulse");
                }, 250);
            }
        } catch (error) {
            button.innerHTML = "Supprimer";
            open_alert("Une erreur est survenue", "Une erreur est survenue, veuillez réessayer plus tard");
        }
    } else {
        button.classList.add("pulse");
        setTimeout(() => {
            button.classList.remove("pulse");
        }, 250);
    }
}