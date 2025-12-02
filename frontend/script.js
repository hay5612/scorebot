<script>
document.getElementById("predict-btn").addEventListener("click", async () => {

    const payload = {
        home_team: document.getElementById("home-team").value,
        away_team: document.getElementById("away-team").value,
        start_season: parseInt(document.getElementById("start-season").value),
        end_season: parseInt(document.getElementById("end-season").value),
        model_type: document.getElementById("model-type").value,
        neutral_site: document.getElementById("neutral-site").checked
    };

    const response = await fetch("https://YOUR_RENDER_BACKEND_URL/predict", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(payload)
    });

    const data = await response.json();

    document.getElementById("result-box").innerHTML = `
        <h3>Prediction:</h3>
        <p><strong>Winner:</strong> ${data.winner}</p>
        <p><strong>Spread:</strong> ${data.spread.toFixed(2)}</p>
    `;
});
</script>
