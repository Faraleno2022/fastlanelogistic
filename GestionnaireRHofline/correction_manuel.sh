#!/bin/bash

set -e

# Configuration
ORIGINAL_PDF="Manuel_Utilisation_GestionnaireRH (8).pdf"
SOURCE_TXT="manuel_source.txt"
CORRECTED_TXT="manuel_source_CORRIGE.txt"
FINAL_PDF="Manuel_Utilisation_GestionnaireRH_CORRIGE_2026.pdf"
BACKUP_DIR="backups"
LOG_FILE="corrections.log"

# Couleurs
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

success() {
    echo -e "${GREEN}✓${NC} $1" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}✗${NC} $1" | tee -a "$LOG_FILE"
    exit 1
}

# Vérifier le PDF
if [ ! -f "$ORIGINAL_PDF" ]; then
    error "PDF non trouvé: $ORIGINAL_PDF"
fi
success "PDF trouvé"

# Créer les sauvegardes
mkdir -p "$BACKUP_DIR"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
cp "$ORIGINAL_PDF" "$BACKUP_DIR/manuel_original_$TIMESTAMP.pdf"
success "Sauvegarde créée"

# Extraire PDF en texte
log "Extraction du PDF..."
pdftotext "$ORIGINAL_PDF" "$SOURCE_TXT"
success "PDF extrait en texte"

# Sauvegarder l'original
cp "$SOURCE_TXT" "$SOURCE_TXT.backup"

# Appliquer les 3 corrections
log "Application des corrections..."
cat "$SOURCE_TXT" | \
  sed 's/Heures de nuit (21h-6h): majoration de 50%/Heures de nuit (20h-6h): majoration de 120%/g' | \
  sed 's/Dimanches et jours fériés: majoration de 100%/Dimanches et jours fériés: majoration de 160% (jour) et 200% (nuit)/g' | \
  sed 's/TA (Taxe Apprentissage) Brut × 1,5%/TA (Taxe Apprentissage) Brut × 2%/g' | \
  sed 's/TA: 1,5%/TA: 2%/g' > "$CORRECTED_TXT"

success "Corrections appliquées"

# Vérifier les corrections
log "Vérification..."
if grep -q "20h-6h.*120%" "$CORRECTED_TXT"; then
    success "✓ Heures de nuit corrigées (20h-6h à +120%)"
else
    error "Heures de nuit non corrigées"
fi

if grep -q "160%.*200%" "$CORRECTED_TXT"; then
    success "✓ Jours fériés corrigés (+160% jour, +200% nuit)"
else
    error "Jours fériés non corrigés"
fi

if grep -q "× 2%" "$CORRECTED_TXT"; then
    success "✓ Taxe d'apprentissage corrigée (2%)"
else
    error "Taxe d'apprentissage non corrigée"
fi

# Afficher les différences
log "Différences détectées:"
diff -u "$SOURCE_TXT.backup" "$CORRECTED_TXT" | head -50 || true

# Générer le PDF
log "Génération du PDF corrigé..."
if command -v pandoc &> /dev/null; then
    pandoc "$CORRECTED_TXT" -o "$FINAL_PDF"
    success "PDF généré: $FINAL_PDF"
else
    error "pandoc non installé. Installer avec: sudo apt-get install pandoc"
fi

echo ""
echo "=================================="
echo "✓ CORRECTIONS TERMINÉES"
echo "=================================="
echo "Fichiers générés:"
echo "  - $CORRECTED_TXT (texte corrigé)"
echo "  - $FINAL_PDF (PDF corrigé)"
echo "  - $BACKUP_DIR/ (sauvegardes)"
echo ""
