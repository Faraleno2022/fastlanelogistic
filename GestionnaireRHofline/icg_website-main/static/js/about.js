document.addEventListener('DOMContentLoaded', function() {
    // Animation des cartes
    const cards = document.querySelectorAll('.dna-card, .advantage-card, .culture-card');
    
    cards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-10px)';
            this.style.boxShadow = '0 15px 30px rgba(247, 147, 30, 0.2)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
            this.style.boxShadow = 'none';
        });
    });

    // Smooth scroll
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            document.querySelector(this.getAttribute('href')).scrollIntoView({
                behavior: 'smooth'
            });
        });
    });

    // Effet parallaxe sur l'image d'approche
    const approachImage = document.querySelector('.approach-image img');
    
    window.addEventListener('scroll', function() {
        if (approachImage) {
            const scrollPosition = window.pageYOffset;
            approachImage.style.transform = `translateY(${scrollPosition * 0.1}px)`;
        }
    });
});