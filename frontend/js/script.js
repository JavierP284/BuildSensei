// script.js (versión robusta, evita duplicados y malos endpoints)

document.addEventListener("DOMContentLoaded", () => {
  // endpoints que asumimos existen
  const endpoints = {
    cpus: "/api/cpus",
    gpus: "/api/gpus",
    mobos: "/api/motherboards",
    memory: "/api/memory",
    psus: "/api/psus",
    check: "/api/check-compatibility" // ruta GET con query params: cpu,gpu,motherboard,memory,psu
  };

  // inicializa Choices para cada select y mantiene referencia
  const choicesMap = {};
  ["cpu-select","gpu-select","mobo-select","ram-select","psu-select"].forEach(id => {
    const el = document.getElementById(id);
    if (el && !el.classList.contains("choices-initialized")) {
      const ch = new Choices(el, {
        searchEnabled: true,
        itemSelectText: 'Presiona para seleccionar',
        searchResultLimit: 100,
        shouldSort: false
      });
      choicesMap[id] = ch;
      el.classList.add("choices-initialized");
    }
  });

  // Carga opciones para cada endpoint y select
  async function loadIntoSelect(url, selectId, transform) {
    try {
      const resp = await fetch(url);
      const data = await resp.json();

      const items = transform ? transform(data) : (Array.isArray(data) ? data : []);
      const ch = choicesMap[selectId];
      if (!ch) return;

      // preparar options: {value,label}
      const opts = items.map(it => {
        // 🌟 NUEVO: si viene en formato {label, value} → NO tocar
        if (it.label && it.value) {
          return { value: it.value, label: it.label };
        }

        // si es string → usarlo igual
        if (typeof it === "string") return { value: it, label: it };

        // si tiene name
        if (it.name) return { value: it.name, label: it.name };

        // si tiene id + name
        if (it.id && it.name) return { value: it.id.toString(), label: it.name };

        // fallback
        return { value: String(it), label: String(it) };
      });

      ch.clearChoices();
      ch.setChoices(opts, "value", "label", true);

    } catch (err) {
      console.error("Error cargando " + selectId, err);
    }
  }

  // Cargar opciones
  loadIntoSelect(endpoints.cpus, "cpu-select");
  loadIntoSelect(endpoints.gpus, "gpu-select"); // ahora acepta {label, value}
  loadIntoSelect(endpoints.mobos, "mobo-select");
  loadIntoSelect(endpoints.memory, "ram-select");
  loadIntoSelect(endpoints.psus, "psu-select");

  // Botón comprobar compatibilidad
  const checkBtn = document.getElementById("check-btn");
  const resultBox = document.getElementById("result-box");

  checkBtn.addEventListener("click", async () => {
    const cpu = document.getElementById("cpu-select").value;
    const gpu = document.getElementById("gpu-select").value;
    const mobo = document.getElementById("mobo-select").value;
    const ram = document.getElementById("ram-select").value;
    const psu = document.getElementById("psu-select").value;

    if (!cpu || !gpu || !mobo || !ram || !psu) {
      showResult("Selecciona todos los componentes antes de verificar.", false);
      return;
    }

    const params = new URLSearchParams({
      cpu,
      gpu,
      motherboard: mobo,
      memory: ram,
      psu
    });

    try {
      const resp = await fetch(`/api/check-compatibility?${params.toString()}`);
      if (!resp.ok) {
        const err = await resp.json().catch(() => ({}));
        throw new Error(err.error || resp.statusText || "Error en servidor");
      }

      const data = await resp.json();

      if (data.messages && Array.isArray(data.messages)) {
        const html = data.messages.map(m => {
          const ok = m.startsWith("✔") || m.toLowerCase().includes("compatible");
          return `<div class="result-line ${ok ? 'ok' : 'bad'}">${m}</div>`;
        }).join("");
        resultBox.innerHTML = html;
      } else if (data.compatible === true) {
        showResult("✔️ Todos los componentes son compatibles.", true);
      } else {
        const reason = data.reason || (data.messages ? data.messages.join("; ") : "Incompatibilidad");
        showResult("❌ " + reason, false);
      }
    } catch (err) {
      console.error(err);
      showResult("Error conectando con el servidor: " + (err.message || ""), false);
    }
  });

  function showResult(text, ok) {
    resultBox.innerHTML = `<div class="${ok ? 'ok' : 'bad'}">${text}</div>`;
  }

});
