function posaljiPitanje() {
    let pitanje = document.getElementById("pitanje").value;
    let odgovorElement = document.getElementById("odgovor");

    if (!pitanje.trim()) {
        odgovorElement.innerText = "⚠️ Molimo unesite pitanje.";
        return;
    }

    // Salje pitanje backendu
    fetch("http://127.0.0.1:5000/ask", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ question: pitanje })
    })
    .then(response => response.json())
    .then(data => {
        // Prikazivanje odgovora iz backend-a
        if (data.answer) {
            odgovorElement.innerText = data.answer;
        } else {
            odgovorElement.innerText = "⚠️ Nema odgovora na ovo pitanje.";
        }
    })
    .catch(error => {
        odgovorElement.innerText = "⚠️ Greška pri slanju zahteva.";
        console.error(error);
    });
}
