"""Configuration de PAVEL IA CV PRO."""

# Préparation Premium : passer PLAN à "premium" et retirer des clés de
# FREE_FEATURES pour restreindre l'offre gratuite. Aucun paiement pour l'instant.
PLAN = "free"
FREE_FEATURES = {"cv", "letter", "analyze", "adapt", "ats", "translate", "express", "docs",
                 "interview", "linkedin", "tracker"}


def has(feature):
    return PLAN == "premium" or feature in FREE_FEATURES


COUNTRIES = ["France", "Suisse", "Belgique", "Canada", "Luxembourg",
             "Allemagne", "Royaume-Uni", "Autre"]
LANGS = {"Français": "français", "English": "English", "Deutsch": "Deutsch",
         "Español": "español", "Italiano": "italiano"}
CV_TYPES = ["Professionnel", "Moderne", "Élégant", "Européen", "Étudiant",
            "Sans expérience", "Reconversion professionnelle", "International",
            "Informatique", "Restauration", "Bâtiment", "Nettoyage",
            "Logistique", "Administratif", "Commercial", "Autre secteur"]
LEVELS = ["Sans expérience", "Débutant (0-2 ans)", "Confirmé (2-5 ans)",
          "Expérimenté (5 ans et plus)"]
TEMPLATES = {
    "CLASSIC": "Classique : sobre, bleu-gris",
    "MODERN": "Moderne et épuré : bandeau bleu",
    "EXECUTIVE": "Exécutif et corporate : marine, serif",
    "PREMIUM": "Premium : noir et or, serif",
    "ELEGANT": "Élégant : bordeaux, titre centré",
    "EUROPEAN": "Européen : colonnes type Europass",
    "TEAL": "Créatif : colonne turquoise",
    "NAVY": "Créatif : colonne marine",
    "CORAL": "Dynamique : colonne corail",
    "EMERALD": "Frais : bandeau émeraude",
    "MINIMAL": "Minimal : ardoise, titres espacés",
    "ATS": "ATS : texte simple, noir",
}

# Lien de don PayPal (peut aussi être défini dans Streamlit Secrets : PAYPAL_URL)
PAYPAL_URL = "https://www.paypal.me/Pavelia38"

# Adresse publique de l'app (facultatif : sinon détection automatique). Ex. : https://mon-app.streamlit.app
APP_URL = "https://pavel-ia-cv-40-h737krcujmyodstbukguzw.streamlit.app"

# Repère de version affiché en bas de page (permet de vérifier que le bon code est en ligne)
BUILD = "2026.10.01-r11"
