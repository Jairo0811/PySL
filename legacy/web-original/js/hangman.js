(() => {
    "use strict";

    const MAN_PARTS = ["___\n", "   |\n", "   O\n", "  /", "|", "\\\n", "  /", " \\\n", "___"];
    const WORDS = [
        "software",
        "javascript",
        "videojuego",
        "programacion",
        "html",
        "basededatos",
        "variable",
        "fotogramas",
        "css",
        "maquinavirtual",
        "nintendo",
        "algoritmo",
        "codigo",
        "pseudocodigo",
    ];

    let word = [];
    let parts = 0;
    let newColumn = 0;
    let playing = false;

    const form = document.forms.visor;

    function chooseWord() {
        const index = Math.floor(Math.random() * WORDS.length);
        word = [...WORDS[index]];
    }

    function drawMan() {
        form.displayHombre.value = MAN_PARTS.slice(0, Math.min(parts, MAN_PARTS.length)).join("");
    }

    function drawLetter(letter) {
        const currentLetters = form.displayPalabra.value.trimEnd().split(" ");
        let found = false;

        form.displayPalabra.value = word
            .map((current, index) => {
                if (current === letter) {
                    found = true;
                    return letter;
                }
                return currentLetters[index] || "_";
            })
            .join(" ") + " ";

        return found;
    }

    function addUsedLetter(letter) {
        form.displayLetras.value += `${letter} `;
        if (newColumn === 3) {
            form.displayLetras.value += "\n";
            newColumn = 0;
        } else {
            newColumn += 1;
        }
    }

    function isComplete() {
        return !form.displayPalabra.value.split(" ").includes("_");
    }

    function finishGame(won) {
        playing = false;

        if (won) {
            form.ganadas.value = Number(form.ganadas.value) + 1;
            alert("¡COMPAI TU ERE UN DURO! ¡MANGATE TU CAMINAO!");
            return;
        }

        form.perdidas.value = Number(form.perdidas.value) + 1;
        alert(`¡LA MACATE LOCO, NO MANGATE TU CAMINAO!\n La palabra era: ${word.join("")}`);
    }

    function play(letter) {
        if (!playing) {
            alert("Pulsa Juego nuevo para comenzar\nuna partida nueva.");
            return;
        }

        addUsedLetter(letter);
        const hit = drawLetter(letter);

        if (!hit) {
            parts += 1;
            drawMan();
        }

        if (parts === MAN_PARTS.length) {
            finishGame(false);
        } else if (isComplete()) {
            finishGame(true);
        }
    }

    function startGame() {
        playing = true;
        parts = 0;
        newColumn = 0;
        chooseWord();
        drawMan();
        form.displayPalabra.value = `${word.map(() => "_").join(" ")} `;
        form.displayLetras.value = "";
    }

    function clearScore() {
        form.ganadas.value = "0";
        form.perdidas.value = "0";
    }

    document.addEventListener("DOMContentLoaded", () => {
        document.querySelectorAll("[data-letter]").forEach((button) => {
            button.addEventListener("click", () => play(button.dataset.letter));
        });

        document.querySelector("[data-new-game]")?.addEventListener("click", startGame);
        document.querySelector("[data-clear-score]")?.addEventListener("click", clearScore);
        startGame();
    });
})();
