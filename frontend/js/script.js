async function fillSelect(url, selectId) {
    try {
        const response = await fetch(url);
        const data = await response.json();
        const select = document.getElementById(selectId);

        select.innerHTML = ''; // Limpiar "Cargando..."
        const choices = new Choices(select, {
            searchEnabled: true,
            itemSelectText: 'Presiona para seleccionar',
            searchResultLimit: 100,
            fuseOptions: {
                threshold: 0.2,
            },
        });

        const options = data.map(item => ({
            value: item,
            label: item,
        }));

        choices.setChoices(options, 'value', 'label', false);

    } catch (error) {
        console.error('Error cargando componentes:', error);
    }
}

// Llenar CPU y GPU al cargar
fillSelect('/api/cpus', 'cpu-select');
fillSelect('/api/gpus', 'gpu-select');
