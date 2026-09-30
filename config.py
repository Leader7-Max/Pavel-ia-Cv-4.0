"""Configuration de PAVEL IA CV PRO."""

# Préparation Premium : passer PLAN à "premium" et retirer des clés de
# FREE_FEATURES pour restreindre l'offre gratuite. Aucun paiement pour l'instant.
PLAN = "free"
FREE_FEATURES = {"cv", "letter", "analyze", "adapt", "ats", "translate", "express", "docs"}


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
    "CLASSIC": "Sobre et professionnel",
    "MODERN": "Moderne, structure visuelle élégante",
    "PREMIUM": "Style haut de gamme (police à empattement)",
    "EUROPEAN": "Structure adaptée au format européen",
    "ATS": "Simple, lisible par les systèmes de recrutement",
}

# Lien PayPal : renseignez-le ici, ou (mieux) dans Streamlit Secrets : PAYPAL_URL = "https://paypal.me/..."
PAYPAL_URL = ""

# Adresse publique de l'app (facultatif : sinon détection automatique). Ex. : https://mon-app.streamlit.app
APP_URL = "https://pavel-ia-cv-40-h737krcujmyodstbukguzw.streamlit.app"

# Repère de version affiché en bas de page (permet de vérifier que le bon code est en ligne)
BUILD = "2026.09.30-r6"
