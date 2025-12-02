const API_BASE = "https://scorebot-bc8z.onrender.com";
const PREDICT_ENDPOINT = "/predict";

const TEAMS = [
  "ARI","ATL","BAL","BUF","CAR","CHI","CIN","CLE","DAL","DEN","DET","GB",
  "HOU","IND","JAX","KC","LV","LAC","LAR","MIA","MIN","NE","NO","NYG","NYJ",
  "PHI","PIT","SEA","SF","TB","TEN","WAS"
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
  const pointDiffEl = document.getElementById("point-diff");
  const rawJson = document.getElementById("raw-json");

  // Populate dropdowns
  TEAMS.forEach((abbr) => {
    let opt1 = document.createElement("option");
    opt1.value = abbr;
    opt1.textContent = abbr;
    homeSelect.appendChild(opt1);

    let opt2 = document.createElement("option");
    opt2.value = abbr;
    opt2.textContent = abbr;
    awaySelect.appendChild(opt2);
  });

  homeSelect.value = "KC";
  awaySelect.value = "BUF";

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    statusEl.textContent = "";
    scoreCard.classList.add("hidden");
    extraInfo.textContent = "";
    pointDiffEl.textContent = "";
    rawJson.textContent = "";

    const payload = {
      home_team: homeSelect.value,
      away_team: awaySelect.value,
      start_season: parseInt(document.getElementById("start-season").value),
      end_season: parseInt(document.getElementById("end-season").value),
      model_type: document.getElementById("model-type").value
    };

    submitBtn.disabled = true;
    submitBtn.textContent = "Predicting...";

    try {
      const res = await fetch(API_BASE + PREDICT_ENDPOINT, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        throw new Error(`HTTP ${res.status}`);
      }

      const data = await res.json();
      rawJson.textContent = JSON.stringify(data, null, 2);

      homeLabel.textContent = `${payload.home_team} (Home)`;
      awayLabel.textContent = `${payload.away_team} (Away)`;

      // win prob
      const winProb = data.home_win_probability;
      if (winProb !== undefined) {
        extraInfo.textContent = `Home win probability: ${(winProb * 100).toFixed(1)}%`;
      }

      // point diff
      if (data.predicted_point_diff !== undefined) {
        const diff = data.predicted_point_diff.toFixed(1);
        pointDiffEl.textContent = `Predicted point difference: ${diff}`;
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
