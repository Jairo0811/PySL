(() => {
    "use strict";

    const VALID_USER = "Jairo";
    const VALID_PASSWORD = "jairomatias";

    const form = document.querySelector("[data-login-form]");
    if (!form) {
        return;
    }

    form.addEventListener("submit", (event) => {
        const user = form.elements.user.value.trim();
        const password = form.elements.pass.value;

        if (!user) {
            alert("Llenar campo usuario");
            event.preventDefault();
            return;
        }

        if (!password) {
            alert("Llenar campo contraseña");
            event.preventDefault();
            return;
        }

        if (user === VALID_USER && password === VALID_PASSWORD) {
            alert("cuenta correcta");
            return;
        }

        event.preventDefault();
        window.location.href = "bad.html";
    });
})();
