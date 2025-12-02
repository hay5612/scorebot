const API_URL = "https://scorebot-bc8z.onrender.com";

const teams = [
    "ARI","ATL","BAL","BUF","CAR","CHI","CIN","CLE","DAL","DEN",
    "DET","GB","HOU","IND","JAX","KC","LV","LAC","LAR","MIA",
    "MIN","NE","NO","NYG","NYJ","PHI","PIT","SEA","SF","TB","TEN","WSH"
];

function fillTeamDropdowns() {
    const home = document.getElementById("homeTeam");
    const away = document.getElementById("awayTeam");

    teams.forEach(t => {
        home.innerHTML += `<option value="${t}">${t}</option>`;
        away.innerHTML += `<option value="${t}">${t}</option>`;
    });
}

fillTeamDropdowns();

document.getElementById("predictBtn").onclick = async function() {
    const home = document.getElementById("homeTeam").value;
    const away = document.getElementById("awayTeam").value;
    const season = parseInt(document.getElementById("season").value);
    const week = parseInt(document.getElementById("week").value);
    const modelType = document.getElementById("modelType").value;
    const neutral = document.getElementById("neutralField").checked;

    const body = {
        home_team: home,
        away_team: away,
        season: season,
        week: week,
        model_type: modelType,
        neutral_field: neutral
    };

    try {
        const res = await fetch(`${API_URL}/predict`, {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify(body)
        });

        const data = await res.json();
        document.getElementById("resultBox").textContent = JSON.stringify(data, null, 2);

    } catch (err) {
        document.getElementById("resultBox").textContent = "Error: " + err;
    }
};
