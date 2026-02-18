const phqDiv = document.getElementById("phq9");
for (let i = 1; i <= 9; i++) {
    phqDiv.innerHTML += `
        <p>Question ${i}</p>
        <select id="q${i}">
            <option value="0">0 - Not at all</option>
            <option value="1">1 - Several days</option>
            <option value="2">2 - More than half the days</option>
            <option value="3">3 - Nearly every day</option>
        </select>
    `;
}

let keystrokes = [];

document.getElementById("typingBox").addEventListener("keydown", function(e) {
    keystrokes.push({
        key: e.key,
        event: "down",
        time: performance.now()
    });
});

document.getElementById("typingBox").addEventListener("keyup", function(e) {
    keystrokes.push({
        key: e.key,
        event: "up",
        time: performance.now()
    });
});

async function submitData() {

    let score = 0;
    for (let i = 1; i <= 9; i++) {
        score += parseInt(document.getElementById(`q${i}`).value);
    }

    const response = await fetch("http://127.0.0.1:8000/submit", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            phq9_score: score,
            typing_text: document.getElementById("typingBox").value,
            keystrokes: keystrokes,
            features: { total_keys: keystrokes.length }
        })
    });

    const result = await response.json();
    alert(result.status);
}
