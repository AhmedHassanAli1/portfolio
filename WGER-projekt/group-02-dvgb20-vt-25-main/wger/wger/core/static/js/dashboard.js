fetch('/api/v2/measurement-category/')
    .then(response => response.json())
    .then(data => {
   
        const dropdown = document.getElementById('measurement-dropdown');
        data.results.forEach(measurement => {
         
            const option = document.createElement('option');
            option.value = measurement.id;
      
            option.textContent = measurement.name;
            dropdown.appendChild(option);
        });


      
        dropdown.addEventListener('change', (event) => {
            const selectedId = event.target.value;
            if (selectedId) {
                fetch(`/api/v2/measurement-category/${selectedId}/`)
                    .then(response => response.json())
                    .then(data => {
                    
                    fetch(`/api/v2/measurement/${selectedId}`)
                        .then(response => response.json())
                        .then(data2 => {
                            
                            if(data2.value==undefined)
                            {
                                data2.value ="no value chosen"
                            }
                            if(data2.date==undefined)
                            {
                                data2.date="no date chosen"
                            }
                            document.getElementById('selected-measurement').textContent = 
                                `Measurement: ${data.name} - Value: ${data2.value} (Date: ${data2.date})`;
                        });
                    });
            }
        });
    })
    .catch(error => console.error('Fel vid hämtning av mätningar:', error));