window.addEventListener("load", function () {
    const btn = document.getElementById("btn")
    const text_resultat = document.getElementById("text_resultat")
    const btn_retry = document.getElementById("btn_retry")
    const input = document.getElementById("nombre")
    const mystere = document.getElementById("nombre_mystere").name

    btn.addEventListener("click", function () {
        const nombre = Number.parseInt(input.value)

        if (nombre < mystere) {
            text_resultat.innerText = "."
            // temps d'attente de 0.5seconde
            setTimeout(function () {
                text_resultat.innerText = ".."
            }, 500);
            setTimeout(function () {
                text_resultat.innerText = "..."
            }, 1000);
            setTimeout(function () {
                text_resultat.innerHTML = "Trop petit !"
            }, 1500);
        } else if (nombre > mystere) {
            setTimeout(function () {
                text_resultat.innerText = ".."
            }, 500);
            setTimeout(function () {
                text_resultat.innerText = "..."
            }, 1000);
            setTimeout(function () {
                text_resultat.innerHTML = "Trop grand !"
            }, 1500);
        } else {
            setTimeout(function () {
                text_resultat.innerText = ".."
            }, 500);
            setTimeout(function () {
                text_resultat.innerText = "..."
            }, 1000);
            setTimeout(function () {
                text_resultat.innerHTML = "Bravo ! Vous avez trouvé le nombre mystère !"
                btn.style.display = "none"
                btn_retry.style.display = "block"
            }, 1500);

        }
    });
});
