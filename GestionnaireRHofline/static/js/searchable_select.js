/**
 * Script pour ajouter une zone de recherche aux listes déroulantes
 * Fournit:
 * - Recherche en temps réel dans les options
 * - Hauteur limitée à 15 lignes avec scrollbar
 * - Support multi-tenant
 */

class SearchableSelect {
    constructor(selectElement) {
        this.select = selectElement;
        this.originalOptions = Array.from(this.select.options);
        this.searchInput = null;
        this.wrapper = null;
        this.init();
    }

    init() {
        // Ajouter la classe scrollable-select si elle n'existe pas
        if (!this.select.classList.contains('scrollable-select') &&
            !this.select.classList.contains('searchable-select')) {
            this.select.classList.add('scrollable-select');
        }

        // Créer le wrapper avec le champ de recherche
        this.createSearchWrapper();

        // Gérer les événements de l'utilisateur
        this.attachEventListeners();
    }

    createSearchWrapper() {
        // Créer le conteneur
        this.wrapper = document.createElement('div');
        this.wrapper.className = 'select-search-wrapper show-search';

        // Créer le champ de recherche
        this.searchInput = document.createElement('input');
        this.searchInput.type = 'text';
        this.searchInput.className = 'select-search-input form-control';
        this.searchInput.placeholder = '🔍 Rechercher...';
        this.searchInput.setAttribute('aria-label', 'Rechercher');

        // Insérer dans le DOM
        this.select.parentNode.insertBefore(this.wrapper, this.select);
        this.wrapper.appendChild(this.searchInput);
        this.wrapper.appendChild(this.select);

        // Définir la hauteur pour 15 lignes (environ 350px)
        if (!this.select.style.maxHeight) {
            this.select.style.maxHeight = '350px';
            this.select.style.overflowY = 'auto';
        }
    }

    attachEventListeners() {
        // Recherche en temps réel
        this.searchInput.addEventListener('input', (e) => {
            this.filterOptions(e.target.value);
        });

        // Fermer le wrapper quand on quitte le select
        this.select.addEventListener('blur', () => {
            this.searchInput.value = '';
            this.filterOptions('');
        });

        // Permettre la navigation au clavier
        this.searchInput.addEventListener('keydown', (e) => {
            if (e.key === 'ArrowDown') {
                e.preventDefault();
                this.select.focus();
                if (this.select.selectedIndex < this.select.options.length - 1) {
                    this.select.selectedIndex++;
                }
            } else if (e.key === 'ArrowUp') {
                e.preventDefault();
                this.select.focus();
                if (this.select.selectedIndex > 0) {
                    this.select.selectedIndex--;
                }
            } else if (e.key === 'Enter') {
                e.preventDefault();
                this.select.focus();
            }
        });
    }

    filterOptions(searchTerm) {
        const term = searchTerm.toLowerCase().trim();
        let visibleCount = 0;

        for (const option of this.originalOptions) {
            const text = option.text.toLowerCase();
            const value = option.value.toLowerCase();

            // Vérifier si le terme correspond au texte ou à la valeur
            const matches = text.includes(term) || value.includes(term);

            if (!term || matches) {
                option.classList.remove('hidden-option');
                option.style.display = 'block';
                visibleCount++;
            } else {
                option.classList.add('hidden-option');
                option.style.display = 'none';
            }
        }

        // Afficher ou masquer le message "aucun résultat"
        if (visibleCount === 0 && term) {
            this.showNoResults();
        } else {
            this.removeNoResults();
        }
    }

    showNoResults() {
        // Créer une option fictive pour indiquer "Aucun résultat"
        if (!document.querySelector('.no-results-option')) {
            const noResultsOption = document.createElement('option');
            noResultsOption.className = 'no-results-option';
            noResultsOption.disabled = true;
            noResultsOption.text = '❌ Aucun résultat';
            this.select.appendChild(noResultsOption);
        }
    }

    removeNoResults() {
        const noResultsOption = document.querySelector('.no-results-option');
        if (noResultsOption) {
            noResultsOption.remove();
        }
    }
}

/**
 * Initialiser les SearchableSelect au chargement du DOM
 */
document.addEventListener('DOMContentLoaded', function() {
    // Chercher tous les select avec la classe searchable-select ou scrollable-select
    const selects = document.querySelectorAll(
        'select.searchable-select, select.scrollable-select, ' +
        'select[data-searchable="true"], select[data-max-lines]'
    );

    selects.forEach(select => {
        // Éviter l'initialisation double
        if (!select.dataset.searchableInitialized) {
            new SearchableSelect(select);
            select.dataset.searchableInitialized = 'true';
        }
    });
});

/**
 * Pour les formulaires AJAX ou dynamiques, réinitialiser les SearchableSelect
 */
function initSearchableSelects(container = document) {
    const selects = container.querySelectorAll(
        'select.searchable-select, select.scrollable-select, ' +
        'select[data-searchable="true"], select[data-max-lines]'
    );

    selects.forEach(select => {
        if (!select.dataset.searchableInitialized) {
            new SearchableSelect(select);
            select.dataset.searchableInitialized = 'true';
        }
    });
}
