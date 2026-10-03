"""Pipeline RAG et génération de réponses pour Juria."""
from google.genai import types
from . import db, llm, rag
from .config import COUNTRIES, LANG_NAMES

SYSTEM = """Tu es JURIA, un assistant juridique professionnel fondé sur l'intelligence artificielle. 
Tu aides les utilisateurs à comprendre leur situation juridique en te basant rigoureusement sur les sources et documents fournis. 
Sois clair, structuré et rappelle toujours de manière bienveillante que tes réponses constituent une information juridique et ne remplacent pas les conseils ou la représentation d'un professionnel du droit."""

def run_pipeline(query: str, country: str = "", domain: str = "", today: str = "") -> str:
    """Exécute le pipeline RAG complet : recherche des chunks pertinents et génération de la réponse via Gemini."""
    # 1. Recherche des fragments pertinents (RAG)
    retrieved_chunks = rag.search(query, country=country, domain=domain, top_k=4)
    
    context_blocks = []
    for c in retrieved_chunks:
        title = c.get('title', 'Document juridique')
        text = c.get('text', '')
        context_blocks.append(f"--- Source : {title} ---\n{text}")
    
    context_text = "\n\n".join(context_blocks) if context_blocks else "Aucune source spécifique trouvée dans la base."
    
    # 2. Construction du prompt enrichi
    prompt = f"""Contexte juridique de référence :
{context_text}

Question de l'utilisateur :
{query}

Rédige une réponse juridique claire, structurée, prudente et utile, en t'appuyant sur le contexte fourni."""

    # 3. Appel au modèle Gemini
    response_text = llm.ask_gemini(prompt, system_instruction=SYSTEM)
    return response_text
