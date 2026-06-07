let slideIndex = 1;
let autoSlideTimeout;

// Initialiser le diaporama
document.addEventListener('DOMContentLoaded', function() {
    showSlides(slideIndex);
    startAutoSlide();
});

// Fonctions de contrôle
function plusSlides(n) {
    clearTimeout(autoSlideTimeout); // Arrêter le diaporama automatique lors d'une interaction manuelle
    showSlides(slideIndex += n);
    startAutoSlide(); // Redémarrer le diaporama automatique
}

function currentSlide(n) {
    clearTimeout(autoSlideTimeout); // Arrêter le diaporama automatique lors d'une interaction manuelle
    showSlides(slideIndex = n);
    startAutoSlide(); // Redémarrer le diaporama automatique
}

function showSlides(n) {
    let i;
    let slides = document.getElementsByClassName("carousel-slide");
    let dots = document.getElementsByClassName("dot");

    if (n > slides.length) { slideIndex = 1 }
    if (n < 1) { slideIndex = slides.length }

    for (i = 0; i < slides.length; i++) {
        slides[i].style.display = "none";
    }
    for (i = 0; i < dots.length; i++) {
        dots[i].className = dots[i].className.replace(" active", "");
    }

    slides[slideIndex - 1].style.display = "block";
    dots[slideIndex - 1].className += " active";
}

// Fonction pour le diaporama automatique
function startAutoSlide() {
    autoSlideTimeout = setTimeout(function() {
        plusSlides(1); // Passe à la slide suivante
    }, 15000); // Change de slide toutes les 15 secondes (5000ms)
}