document.addEventListener('DOMContentLoaded', function() {
    const contactForm = document.getElementById('contactForm');
    
    if (contactForm) {
        contactForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Récupération des valeurs avec les bons IDs
            const name = document.getElementById('contact_name').value;
            const email = document.getElementById('contact_email').value;
            const message = document.getElementById('contact_message').value;
            
            // Validation
            if (!name || !email || !message) {
                alert('Veuillez remplir tous les champs obligatoires');
                return;
            }
            
            // Changement visuel du bouton
            const submitBtn = contactForm.querySelector('.submit-btn');
            const btnText = submitBtn.querySelector('.btn-text');
            const btnIcon = submitBtn.querySelector('i');
            
            btnText.textContent = 'Envoi en cours...';
            btnIcon.classList.replace('fa-paper-plane', 'fa-spinner', 'fa-spin');
            
            // Soumission réelle du formulaire
            contactForm.submit();
        });
    }
});