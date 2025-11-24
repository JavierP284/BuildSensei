// script.js (versión robusta, evita duplicados y malos endpoints)

document.addEventListener("DOMContentLoaded", () => {
  const endpoints = {
    cpus: "/api/cpus",
    gpus: "/api/gpus",
    mobos: "/api/motherboards",
    memory: "/api/memory",
    psus: "/api/psus",
    check: "/api/check-compatibility"
  };

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

  async function loadIntoSelect(url, selectId, transform) {
    try {
      const resp = await fetch(url);
      const data = await resp.json();

      const items = transform ? transform(data) : (Array.isArray(data) ? data : []);
      const ch = choicesMap[selectId];
      if (!ch) return;

      const opts = items.map(it => {
        if (it.label && it.value) {
          return { value: it.value, label: it.label };
        }
        if (typeof it === "string") return { value: it, label: it };
        if (it.name) return { value: it.name, label: it.name };
        if (it.id && it.name) return { value: it.id.toString(), label: it.name };
        return { value: String(it), label: String(it) };
      });

      ch.clearChoices();
      ch.setChoices(opts, "value", "label", true);

    } catch (err) {
      console.error("Error cargando " + selectId, err);
    }
  }

  loadIntoSelect(endpoints.cpus, "cpu-select");
  loadIntoSelect(endpoints.gpus, "gpu-select");
  loadIntoSelect(endpoints.mobos, "mobo-select");
  loadIntoSelect(endpoints.memory, "ram-select");
  loadIntoSelect(endpoints.psus, "psu-select");

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
      console.log("Respuesta del servidor:", data);

      // Construir HTML con análisis detallado
      let html = "";

      // Status general
      if (data.compatible) {
        html += `<div class="result-line ok">✔️ ${data.message || 'Todos los componentes son compatibles'}</div>`;
      } else {
        html += `<div class="result-line bad">❌ Incompatibilidad detectada</div>`;
      }

      // Mostrar problemas
      if (data.issues && Array.isArray(data.issues)) {
        html += `<div class="issues-section">`;
        data.issues.forEach(issue => {
          html += `<div class="result-line bad">❌ ${issue}</div>`;
        });
        html += `</div>`;
      }

      // Mostrar análisis de potencia
      if (data.power_analysis) {
        const pa = data.power_analysis;
        html += `
          <div class="power-analysis-section">
            <h4>⚡ Análisis de Potencia</h4>
            <div class="power-detail">
              <span class="label">GPU (TDP):</span>
              <span class="value">${pa.gpu_power_tdp}W</span>
            </div>
            <div class="power-detail">
              <span class="label">CPU (TDP):</span>
              <span class="value">${pa.cpu_power_tdp}W</span>
            </div>
            <div class="power-detail">
              <span class="label">Consumo Total Estimado:</span>
              <span class="value">${pa.total_estimated}W</span>
            </div>
            <div class="power-detail">
              <span class="label">PSU Disponible:</span>
              <span class="value">${pa.psu_available}W</span>
            </div>
            <div class="power-detail">
              <span class="label">Margen:</span>
              <span class="value ${pa.margin >= 0 ? 'positive' : 'negative'}">${pa.margin}W</span>
            </div>
          </div>
        `;
      }

      // Mostrar análisis de cuello de botella (bottleneck_analysis) usando clases CSS
      if (data.bottleneck_analysis) {
        const bn = data.bottleneck_analysis;
        // detalles opcionales (json)
        const detailsId = 'bn-details-' + Math.random().toString(36).slice(2,8);
        html += `
          <div class="bottleneck-section">
            <h4>⚖️ Análisis de Cuello de Botella</h4>
            <div class="power-detail">
              <span class="label">Resultado:</span>
              <span class="value">${bn.summary}</span>
            </div>
            <button class="btn btn--ghost" type="button" data-details="${detailsId}">Más info</button>
            <div id="${detailsId}" class="bottleneck-details" style="display:none;margin-top:10px;">
              <div><strong>CPU núcleos:</strong> ${bn.details.cpu_cores ?? '—'}</div>
              <div><strong>CPU boost:</strong> ${bn.details.cpu_boost_ghz ?? '—'} GHz</div>
              <div><strong>CPU TDP:</strong> ${bn.details.cpu_tdp ?? '—'} W</div>
              <div><strong>GPU TDP:</strong> ${bn.details.gpu_tdp ?? bn.details.gpu_tdp ?? '—'} W</div>
              ${bn.details.note ? `<div style="margin-top:6px;color:#555;"><em>${bn.details.note}</em></div>` : ''}
            </div>
          </div>
        `;
      }
      
      // Mostrar advertencias
      if (data.warnings && Array.isArray(data.warnings)) {
        html += `<div class="warnings-section">`;
        data.warnings.forEach(warning => {
          html += `<div class="result-line warning">⚠️ ${warning}</div>`;
        });
        html += `</div>`;
      }

      resultBox.innerHTML = html;
      // activar toggles "Más info"
      document.querySelectorAll('button[data-details]').forEach(btn => {
        btn.addEventListener('click', () => {
          const id = btn.getAttribute('data-details');
          const el = document.getElementById(id);
          if (!el) return;
          el.style.display = (el.style.display === 'none') ? 'block' : 'none';
        });
      });

    } catch (err) {
      console.error(err);
      showResult("Error conectando con el servidor: " + (err.message || ""), false);
    }
  });

  function showResult(text, ok) {
    resultBox.innerHTML = `<div class="${ok ? 'ok' : 'bad'}">${text}</div>`;
  }

});
