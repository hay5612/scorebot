const API_BASE = "https://scorebot-bc8z.onrender.com";
const PREDICT_ENDPOINT = "/predict";

const TEAMS = [
  "ARI","ATL","BAL","BUF","CAR","CHI","CIN","CLE","DAL","DEN","DET",
  "GB","HOU","IND","JAX","KC","LV","LAC","LAR","MIA","MIN","NE","NO",
  "NYG","NYJ","PHI","PIT","SEA","SF","TB","TEN","WAS"
];

document.addEventListener("DOMContentLoaded", () => {

  const homeSelect = document.getElementById("home-team");
  const awaySelect = document.getElementById("away-team");
  const form = document.getElementById("prediction-form");
  const submitBtn = document.getElementById("submit-btn");

  const statusEl = document.getElementById("status");
  const scoreCard = document.getElementById("score-display");
  const homeLabel = document.getElementById("home-label");
  const awayLabel = document.getElementById("away-label");
  const homeScore = document.getElementById("home-score");
  const awayScore = document.getElementById("away-score");
  const extraInfo = document.getElementById("extra-info");
  const rawJson = document.getElementById("raw-json");

  // Populate dropdowns
  TEAMS.forEach((abbr) => {
    const opt1 = document.createElement("option");
    opt1.value = abbr;
    opt1.textContent = abbr;

    const opt2 = document.createElement("option");
    opt2.value = abbr;
    opt2.textContent = abbr;

    homeSelect.appendChild(opt1);
    awaySelect.appendChild(opt2);
  });

  homeSelect.value = "KC";
  awaySelect.value = "BUF";

  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    statusEl.textContent = "";
    statusEl.className = "";
    scoreCard.classList.add("hidden");
    rawJson.textContent = "";

    const home = homeSelect.value;
    const away = awaySelect.value;
    const startSeason = parseInt(document.getElementById("start-season").value, 10);
    const endSeason = parseInt(document.getElementById("end-season").value, 10);
    const modelType = document.getElementById("model-type").value;

    if (home === away) {
      statusEl.textContent = "Teams must be different.";
      statusEl.className = "status-error";
      return;
    }

    if (startSeason > endSeason) {
      statusEl.textContent = "Start season must be ≤ end season.";
      statusEl.className = "status-error";
      return;
    }

    const payload = {
      home_team: home,
      away_team: away,
      start_season: startSeason,
      end_season: endSeason,
      model_type: modelType
    };

    submitBtn.disabled = true;
    submitBtn.textContent = "Predicting...";

    try {
      const res = await fetch(API_BASE + PREDICT_ENDPOINT, {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(payload)
      });

      if (!res.ok) {
        const text = await res.text();
        throw new Error(`HTTP ${res.status}: ${text}`);
      }

      const data = await res.json();
      rawJson.textContent = JSON.stringify(data, null, 2);

      homeLabel.textContent = `${home} (Home)`;
      awayLabel.textContent = `${away} (Away)`;

      homeScore.textContent = data.predicted_point_diff >= 0 ? "Win" : "Loss";
      awayScore.textContent = data.predicted_point_diff >= 0 ? "Loss" : "Win";

      if (data.home_win_probability !== null) {
        const pct = (data.home_win_probability * 100).toFixed(1);
        extraInfo.textContent = `Home win probability: ${pct}%`;
      }

      scoreCard.classList.remove("hidden");
      statusEl.textContent = "Prediction received.";
      statusEl.className = "status-ok";

    } catch (err) {
      statusEl.textContent = "Error contacting API: " + err.message;
      statusEl.className = "status-error";
    } finally {
      submitBtn.disabled = false;
      submitBtn.textContent = "Get Prediction";
    }
  });
});
