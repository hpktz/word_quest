/**
 * 
 * @param {*} radio 
 */
function profile_picture_container(radio) {
    const container = radio.parentElement.parentElement;
    if (container.classList.contains("active")) {
        setTimeout(() => {
            container.classList.remove("active");
        }, 301);
    } else {
        container.classList.add("active");
    }
}

function set_button(form) {
    const button = form.querySelector(".submit-button");
    button.classList.add("active");
}

function popup_verification_email() {
    const popup = document.querySelector(".pop-up.otp_check");
    popup.classList.add("active");
}

function close_popup_verification_email(el = null, event = null) {
    if (event) {
        event.preventDefault();
    }
    const popup = document.querySelector(".pop-up.otp_check");
    popup.classList.remove("active");
}

async function verification_email(form, event) {
    event.preventDefault();
    const alert = document.getElementById("otp-alert-mess");
    if (form.button.classList.contains("active")) {
        form.button.innerHTML = "<div class='loader'></div>";
    } else {
        return;
    }
    const code = form.querySelector("#code").value;
    if (code === "") {
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
        const response = await fetch("/dashboard/settings/verify-email/" + code);
        const data = await response.json();
        if (data.code == 200) {
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
        } else {
            form.button.innerHTML = "Vérifier";
            form.button.classList.remove("active");
            form.button.classList.add("pulse");
            alert.innerHTML = `<p class='alert-mess'>${data.message}</p>`;
            setTimeout(() => {
                form.button.classList.remove("pulse");
            }, 250);
        }
    } catch (error) {
        form.button.innerHTML = "Vérifier";
        form.button.classList.remove("active");
        open_alert("Une erreur est survenue", "Une erreur est survenue, veuillez réessayer plus tard");
    }
}

async function send_user_infos(form, event) {
    event.preventDefault();
    const alert = document.getElementById("settings-section-alert-mess");
    if (form.button.classList.contains("active")) {
        form.button.innerHTML = "<div class='loader'></div>";
    } else {
        return;
    }
    const username = form.querySelector("#username").value;
    const email = form.querySelector("#email").value;
    if (username === "" || email === "") {
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
        const response = await fetch("/dashboard/settings/change-user-infos", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                username: username,
                email: email,
                profilePicture: form.profilePicture.value
            })
        });
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

async function send_security_form(form, event) {
    event.preventDefault();
    const alert = document.getElementById("password-section-alert-mess");
    if (form.button.classList.contains("active")) {
        form.button.innerHTML = "<div class='loader'></div>";
    } else {
        return;
    }
    const old_password = form.querySelector("#old-password").value;
    const new_password = form.querySelector("#new-password").value;
    const mfa = form.querySelector("#mfa").checked;
    try {
        const response = await fetch("/dashboard/settings/change-password", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                old_password: old_password,
                new_password: new_password,
                mfa: mfa
            })
        });
        const data = await response.json();
        if (data.code == 200) {
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

async function change_visibility(checkbox, event) {
    checkbox.labels[0].innerHTML = `<div class="loader-container"><div class="loader"></div></div>`;
    let checked = checkbox.checked;
    let visibility = checked ? 1 : 0;

    try {
        const response = await fetch("/dashboard/settings/change-visibility/" + visibility);
        const data = await response.json();
        if (data.code == 200) {
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

function popup_delete() {
    const popup = document.querySelector(".pop-up.delete_account");
    popup.classList.add("active");
}

function close_popup_delete(el = null, event = null) {
    if (event) {
        event.preventDefault();
    }
    const popup = document.querySelector(".pop-up.delete_account");
    popup.classList.remove("active");
}

async function delete_account(button) {
    const input = document.getElementById("delete");
    if (input.value === "supprimer mon compte") {
        button.innerHTML = "<div class='loader'></div>";
        try {
            const response = await fetch("/dashboard/settings/delete-account");
            const data = await response.json();
            if (data.code == 200) {
                window.location.href = "/dashboard/settings/delete-account";
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