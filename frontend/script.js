const API_BASE = "https://scorebot-bc8z.onrender.com";

const teams = [
    "ARI","ATL","BAL","BUF","CAR","CHI","CIN","CLE","DAL","DEN","DET","GB",
    "HOU","IND","JAX","KC","LV","LAC","LAR","MIA","MIN","NE","NO","NYG","NYJ",
    "PHI","PIT","SEA","SF","TB","TEN","WAS"
];

function fillTeamDropdown(id) {
    const sel = document.getElementById(id);
    teams.forEach(t => {
        const opt = document.createElement("option");
        opt.value = t;
        opt.textContent = t;
        sel.appendChild(opt);
    });
}

fillTeamDropdown("homeTeam");
fillTeamDropdown("awayTeam");

document.getElementById("predictBtn").addEventListener("click", async () => {
    const payload = {
        home_team: document.getElementById("homeTeam").value,
        away_team: document.getElementById("awayTeam").value,
        season: parseInt(document.getElementById("season").value),
        week: parseInt(document.getElementById("week").value),
        model_type: document.getElementById("modelType").value,
        neutral_field: document.getElementById("neutralField").checked
    };

    const resultBox = document.getElementById("resultBox");
    resultBox.textContent = "Loading...";

    try {
        const response = await fetch(`${API_BASE}/predict`, {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            const err = await response.json();
            resultBox.textContent = "Error: " + JSON.stringify(err, null, 2);
            return;
        }

        const data = await response.json();
        resultBox.textContent = JSON.stringify(data, null, 2);

    } catch (err) {
        resultBox.textContent = "Network error: " + err;
    }
});
