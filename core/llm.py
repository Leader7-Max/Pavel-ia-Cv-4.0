"""Gestion des interactions avec l'API Google GenAI (Gemini et Embeddings)."""
from google import genai
from .config import GEMINI_MODEL, EMBED_MODEL, secret

def get_client():
    """Initialise et retourne le client GenAI avec la clé API des secrets ou de l'environnement."""
    api_key = secret("GEMINI_API_KEY")
    if not api_key:
        # Fallback si configuré via st.secrets ou os.environ d'une autre manière
        import os
        api_key = os.getenv("GEMINI_API_KEY", "")
    return genai.Client(api_key=api_key if api_key else None)

def embed(texts: list[str], task_type: str = "RETRIEVAL_DOCUMENT") -> list[list[float]]:
    """Génère des embeddings pour une liste de textes via le modèle configuré."""
    client = get_client()
    response = client.models.embed_content(
        model=EMBED_MODEL,
        contents=texts,
    )
    # Extraction des vecteurs de la réponse du SDK google-genai
    return [vals.values for vals in response.embeddings]

def ask_gemini(prompt: str, system_instruction: str = None) -> str:
    """Envoie un prompt à Gemini et retourne la réponse textuelle."""
    client = get_client()
    config = {}
    if system_instruction:
        config["system_instruction"] = system_instruction
        
    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
        config=config if config else None,
    )
    return response.text
