const API_BASE = "https://scorebot-bc8z.onrender.com";
const PREDICT_ENDPOINT = "/predict"; // change if your route is different
const BACKEND_URL = "https://scorebot-bc8z.onrender.com";


const TEAMS = [
  "ARI",
  "ATL",
  "BAL",
  "BUF",
  "CAR",
  "CHI",
  "CIN",
  "CLE",
  "DAL",
  "DEN",
  "DET",
  "GB",
  "HOU",
  "IND",
  "JAX",
  "KC",
  "LV",
  "LAC",
  "LAR",
  "MIA",
  "MIN",
  "NE",
  "NO",
  "NYG",
  "NYJ",
  "PHI",
  "PIT",
  "SEA",
  "SF",
  "TB",
  "TEN",
  "WAS",
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

  // populate team dropdowns
  TEAMS.forEach((abbr) => {
    const makeOption = () => {
      const opt = document.createElement("option");
      opt.value = abbr;
      opt.textContent = abbr;
      return opt;
    };
    homeSelect.appendChild(makeOption());
    awaySelect.appendChild(makeOption());
  });

  homeSelect.value = "KC";
  awaySelect.value = "BUF";

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    statusEl.textContent = "";
    statusEl.className = "";
    scoreCard.classList.add("hidden");
    extraInfo.textContent = "";
    rawJson.textContent = "";

    const home = homeSelect.value;
    const away = awaySelect.value;

    if (home === away) {
      statusEl.textContent = "Home and away teams must be different.";
      statusEl.className = "status-error";
      return;
    }

    const season = parseInt(document.getElementById("season").value, 10);
    const week = parseInt(document.getElementById("week").value, 10);
    const modelType = document.getElementById("model-type").value || null;
    const neutralField = document.getElementById("neutral-field").checked;

    // *** EDIT THIS TO MATCH YOUR FASTAPI PREDICTION MODEL ***
    const payload = {
      home_team: home,
      away_team: away,
      season: season,
      week: week,
      model_type: modelType,
      neutral_field: neutralField,
    };

    submitBtn.disabled = true;
    submitBtn.textContent = "Predicting...";

    try {
      const res = await fetch(API_BASE + PREDICT_ENDPOINT, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        const text = await res.text();
        throw new Error(`HTTP ${res.status}: ${text}`);
      }

      const data = await res.json();
      rawJson.textContent = JSON.stringify(data, null, 2);

      // Try to pull out common keys if they exist
      const hs =
        data.home_score ??
        data.predicted_home_score ??
        data.home_points ??
        null;
      const as =
        data.away_score ??
        data.predicted_away_score ??
        data.away_points ??
        null;

      homeLabel.textContent = `${home} (Home)`;
      awayLabel.textContent = `${away} (Away)`;

      if (hs !== null && as !== null) {
        homeScore.textContent = hs;
        awayScore.textContent = as;
      } else {
        homeScore.textContent = "?";
        awayScore.textContent = "?";
      }

      // Optional: win probability if present
      const winProbHome =
        data.home_win_prob ??
        data.win_prob_home ??
        data.home_win_probability ??
        null;

      if (winProbHome !== null) {
        const pct = (winProbHome * 100).toFixed(1);
        extraInfo.textContent = `Home win probability: ${pct}%`;
      }

      scoreCard.classList.remove("hidden");
      statusEl.textContent = "Prediction received.";
      statusEl.className = "status-ok";
    } catch (err) {
      console.error(err);
      statusEl.textContent = "Error contacting API: " + err.message;
      statusEl.className = "status-error";
    } finally {
      submitBtn.disabled = false;
      submitBtn.textContent = "Get Prediction";
    }
  });
});