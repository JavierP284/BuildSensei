async function fillSelect(url, selectId) {
    try {
        const response = await fetch(url);
        const data = await response.json();
        const select = document.getElementById(selectId);

        select.innerHTML = ''; // Limpiar "Cargando..."
        data.forEach(item => {
            const option = document.createElement('option');
            option.value = item;
            option.textContent = item;
            select.appendChild(option);
        });
    } catch (error) {
        console.error('Error cargando componentes:', error);
    }
}

// Llenar CPU y GPU al cargar
fillSelect('/api/cpus', 'cpu-select');
fillSelect('/api/gpus', 'gpu-select');
