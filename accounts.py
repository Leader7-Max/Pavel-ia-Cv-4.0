"""Module accounts : gère la connexion, l'inscription et l'accès aux pages."""
import streamlit as st

def enforce():
    """Vérifie l'état de l'utilisateur si nécessaire."""
    pass

def notice():
    """Affiche une notice liée aux comptes si besoin."""
    pass

def page(H):
    """Page de gestion du compte utilisateur."""
    H.top("Mon compte")
    st.write("Gestion des comptes et des abonnements (bientôt disponible).")
    
    # Exemple de base pour stocker un utilisateur dans session_state si besoin
    if "user" not in H.ss:
        H.ss["user"] = None

    if H.ss["user"]:
        st.success(f"Connecté en tant que : {H.ss['user'].get('name', 'Utilisateur')}")
        if st.button("Se déconnecter"):
            H.ss["user"] = None
            st.rerun()
    else:
        st.info("Vous n'êtes pas connecté.")
        name_input = st.text_input("Votre nom pour la session")
        if st.button("Se connecter"):
            if name_input.strip():
                H.ss["user"] = {"name": name_input.strip()}
                st.success("Connexion réussie !")
                st.rerun()
            else:
                st.warning("Veuillez entrer un nom.")
