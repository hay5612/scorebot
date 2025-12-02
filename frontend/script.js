const API_BASE = "https://scorebot-bc8z.onrender.com";
const PREDICT_ENDPOINT = "/predict";
const BACKEND_URL = "https://scorebot-bc8z.onrender.com";

const TEAMS = [
  "ARI", "ATL", "BAL", "BUF", "CAR", "CHI", "CIN", "CLE",
  "DAL", "DEN", "DET", "GB", "HOU", "IND", "JAX", "KC",
  "LV", "LAC", "LAR", "MIA", "MIN", "NE", "NO", "NYG",
  "NYJ", "PHI", "PIT", "SEA", "SF", "TB", "TEN", "WAS",
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

  // populate dropdown menus
  TEAMS.forEach((abbr) => {
    const makeOption = () => {
      const opt = document.createElement("option");
      opt.value = opt.textContent = abbr;
      return opt;
    };
    homeSelect.appendChild(makeOption());
    awaySelect.appendChild(makeOption());
  });

  homeSelect.value = "KC";
  awaySelect.value = "BUF";

  // form submit handler
  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    statusEl.textContent = "";
    statusEl.className = "";
    scoreCard.classList.add("hidden");
    extraInfo.textContent = "";
    pointDiffEl.textContent = "";
    rawJson.textContent = "";

    const payload = {
      home_team: homeSelect.value,
      away_team: awaySelect.value,
      start_season: parseInt(document.getElementById("start-season").value, 10),
      end_season: parseInt(document.getElementById("end-season").value, 10),
      model_type: document.getElementById("model-type").value,
      neutral_field: document.getElementById("neutral-field").checked,
    };

    if (payload.home_team === payload.away_team) {
      statusEl.textContent = "Home and away teams must be different.";
      statusEl.className = "status-error";
      return;
    }

    submitBtn.disabled = true;
    submitBtn.textContent = "Predicting...";

    try {
      const res = await fetch(API_BASE + PREDICT_ENDPOINT, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!res.ok) throw new Error(`HTTP ${res.status}`);

      const data = await res.json();
      rawJson.textContent = JSON.stringify(data, null, 2);

      homeLabel.textContent = `${payload.home_team} (Home)`;
      awayLabel.textContent = `${payload.away_team} (Away)`;

      // win probability
      const winProb = data.home_win_probability ?? null;
      if (winProb !== null) {
        extraInfo.textContent = `Home win probability: ${(winProb * 100).toFixed(1)}%`;
      }

      // point difference
      if (data.predicted_point_diff !== undefined) {
        const diff = data.predicted_point_diff.toFixed(1);
        pointDiffEl.textContent = `Predicted point differential: ${diff}`;
      }

      statusEl.textContent = "Prediction ready.";
      statusEl.className = "status-ok";
      scoreCard.classList.remove("hidden");
    } catch (err) {
      statusEl.textContent = "Error contacting API: " + err.message;
      statusEl.className = "status-error";
    } finally {
      submitBtn.disabled = false;
      submitBtn.textContent = "Get Prediction";
    }
  });
});
