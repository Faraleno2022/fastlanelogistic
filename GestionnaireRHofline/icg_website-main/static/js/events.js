// events.js
document.addEventListener('DOMContentLoaded', function() {
    
    // --- Script pour l'aperçu de l'image ---
    const fileInput = document.getElementById('id_event_picture');
    const previewImg = document.getElementById('hse-preview');
    
    if(fileInput && previewImg) {
        // Applique la classe pour masquer l'input file réel si tu ne veux pas qu'il soit visible
        fileInput.classList.add('hse-input-file'); 

        fileInput.addEventListener('change', function(e) {
            if(this.files && this.files[0]) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    previewImg.src = e.target.result;
                };
                reader.readAsDataURL(this.files[0]);
            } else {
                // Remet l'image par défaut si aucun fichier n'est sélectionné
                // Assure-toi que le chemin est correct pour la prod (ex: via une URL absolue ou une variable JS)
                previewImg.src = "{% static 'images/hse-default.jpg' %}"; 
            }
        });
    }

    // --- Compteur de caractères pour la description ---
    const textarea = document.getElementById('id_event_description');
    const charCount = document.getElementById('hse-char-count');
    const maxLength = 1500; 

    if(textarea && charCount) {
        charCount.textContent = textarea.value.length; // Initialiser au chargement

        textarea.addEventListener('input', function() {
            const count = this.value.length;
            charCount.textContent = count;
            
            if(count > maxLength) {
                charCount.style.color = 'red';
            } else {
                charCount.style.color = '#FF6D00'; // Couleur orange directe
            }
        });
    }

});