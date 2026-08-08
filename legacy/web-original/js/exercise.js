(() => {
    "use strict";

    const REQUIRED_VALUES = 5;

    function readNumbers() {
        const values = [];

        for (let index = 0; index < REQUIRED_VALUES; index += 1) {
            const value = Number.parseInt(prompt("Ingresar numero"), 10);
            values.push(value);
        }

        return values;
    }

    function findSmallestEvenIndex(values) {
        let smallest = Number.POSITIVE_INFINITY;
        let position = -1;

        values.forEach((value, index) => {
            if (Number.isFinite(value) && value % 2 === 0 && value < smallest) {
                smallest = value;
                position = index;
            }
        });

        return position;
    }

    function render(values, selectedIndex) {
        const container = document.querySelector("[data-exercise-result]");
        if (!container) {
            return;
        }

        const table = document.createElement("table");
        table.className = "exercise-table";

        values.forEach((value, index) => {
            const row = document.createElement("tr");
            row.className = index === selectedIndex ? "smallest-even" : "not-selected";

            const valueCell = document.createElement("td");
            valueCell.textContent = String(value);

            const resultCell = document.createElement("td");
            resultCell.textContent = index === selectedIndex ? "Par menor" : "-";

            row.append(valueCell, resultCell);
            table.appendChild(row);
        });

        container.replaceChildren(table);
    }

    document.addEventListener("DOMContentLoaded", () => {
        const values = readNumbers();
        render(values, findSmallestEvenIndex(values));
    });
})();
