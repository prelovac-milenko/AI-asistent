let emitenti = [];
let izabraniEmitent = null;

// Učitaj emitente
fetch('/api/emitenti')
  .then(res => res.json())
  .then(data => {
    emitenti = data.emittenti;
  });

const input = document.getElementById('searchInput');
const dropdown = document.getElementById('dropdown');
const prepareButton = document.getElementById('prepareButton');
const questionInput = document.getElementById('questionInput');
const askButton = document.getElementById('askButton');
const answerBox = document.getElementById('answerBox');
const statusBox = document.getElementById('statusBox');

// Dinamička pretraga emitenta
input.addEventListener('input', () => {
  const query = input.value.toLowerCase();
  dropdown.innerHTML = '';

  if (query.length < 1) {
    dropdown.style.display = 'none';
    return;
  }

  const filtered = emitenti.filter(e =>
    e.oznaka.toLowerCase().includes(query) ||
    e.naziv.toLowerCase().includes(query) ||
    e.grad.toLowerCase().includes(query)
  );

  if (filtered.length > 0) {
    dropdown.style.display = 'block';
    filtered.slice(0, 10).forEach(e => {
      const div = document.createElement('div');
      div.textContent = `${e.oznaka} – ${e.naziv} (${e.grad})`;
      div.onclick = () => {
        input.value = `${e.oznaka} – ${e.naziv}`;
        izabraniEmitent = e.oznaka;
        dropdown.style.display = 'none';
        prepareButton.disabled = false;
        statusBox.textContent = '';
        questionInput.disabled = true;
        askButton.disabled = true;
        console.log('Izabran emitent:', izabraniEmitent);
      };
      dropdown.appendChild(div);
    });
  } else {
    dropdown.style.display = 'none';
  }
});

// Zatvaranje dropdown-a klikom van selektora
document.addEventListener('click', (e) => {
  if (!e.target.closest('.container')) {
    dropdown.style.display = 'none';
  }
});

// Dugme za pripremu podataka
prepareButton.addEventListener('click', () => {
  if (!izabraniEmitent) return;

  prepareButton.disabled = true;
  statusBox.textContent = 'Pripremam podatke...';

  const years = ["2020", "2021", "2022", "2023"];
  const query = years.map(y => `years=${y}`).join('&');

  fetch(`/api/bilansi/${izabraniEmitent}?${query}`)
    .then(res => res.json())
    .then(data => {
      statusBox.textContent = '✅ Podaci su pripremljeni.';
      questionInput.disabled = false;
      askButton.disabled = false;
    })
    .catch(err => {
      console.error(err);
      statusBox.textContent = '❌ Greška prilikom pripreme podataka.';
      prepareButton.disabled = false;
    });
});

// Dugme za slanje pitanja
askButton.addEventListener('click', () => {
  const question = questionInput.value.trim();
  if (!question) {
    alert('Unesite pitanje.');
    return;
  }

  answerBox.textContent = "Obrađujem pitanje...";

  const payload = {
    emitent: izabraniEmitent,
    godine: [2020, 2021, 2022, 2023],
    pitanje: question
  };

  fetch('/api/odgovor', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  })
    .then(res => res.json())
    .then(data => {
      answerBox.textContent = data.odgovor || 'Nema odgovora.';
    })
    .catch(err => {
      console.error(err);
      answerBox.textContent = 'Greška prilikom obrade pitanja.';
    });
});
