"""Module de simulation d'entretien d'embauche intelligent par IA pour Pavel IA CV."""
import streamlit as st

def render_interview_simulator():
    st.markdown("### 🧠 Simulateur d'Entretien d'Embauche Intelligent")
    st.caption("Préparez vos entretiens en conditions réelles. L'IA analyse vos réponses et vous coache en direct.")

    # Initialisation de l'état de la session pour l'entretien
    if "interview_started" not in st.session_state:
        st.session_state.interview_started = False
    if "interview_history" not in st.session_state:
        st.session_state.interview_history = []
    if "current_question_index" not in st.session_state:
        st.session_state.current_question_index = 0

    # Étape 1 : Configuration du poste
    if not st.session_state.interview_started:
        with st.form("interview_setup_form"):
            poste_vise = st.text_input("Intitulé du poste visé (ex: Développeur Python, Chef de projet...)", value="Développeur / Expert IA")
            niveau = st.selectbox("Niveau du poste", ["Junior", "Confirmé / Intermédiaire", "Senior / Lead", "Expert / Management"])
            ton = st.selectbox("Style de recruteur", ["Bienveillant et pédagogique", "Strict et professionnel (Pièges techniques)", "Dynamique et direct"])
            
            submitted = st.form_submit_button("🚀 Lancer la simulation")
            if submitted:
                st.session_state.interview_started = True
                st.session_state.poste_vise = poste_vise
                st.session_state.niveau = niveau
                st.session_state.ton = ton
                # Première question générée dynamiquement
                st.session_state.interview_history = [{
                    "role": "interviewer",
                    "text": f"Bonjour ! Commençons. Parlez-moi de votre parcours et de ce qui fait de vous le candidat idéal pour ce poste de {poste_vise} ({niveau})."
                }]
                st.rerun()
    
    # Étape 2 : Déroulement de l'entretien
    else:
        st.info(ل"🎯 Poste ciblé : **{st.session_state.poste_vise}** | Niveau : **{st.session_state.niveau}**")
        
        # Affichage de l'historique de la conversation
        for message in st.session_state.interview_history:
            if message["role"] == "interviewer":
                with st.chat_message("assistant", avatar="🧠"):
                    st.markdown(message["text"])
            else:
                with st.chat_message("user", avatar="👤"):
                    st.markdown(message["text"])

        # Formulaire de réponse de l'utilisateur
        with st.form(key="answer_form", clear_on_submit=True):
            user_answer = st.text_area("Votre réponse :", placeholder="Rédigez votre réponse comme si vous étiez en entretien oral...", height=100)
            col1, col2 = st.columns([1, 4])
            with col1:
                submit_answer = st.form_submit_button("Envoyer 💬")
            with col2:
                reset_interview = st.form_submit_button("🔄 Recommencer l'entretien")

        if reset_interview:
            st.session_state.interview_started = False
            st.session_state.interview_history = []
            st.rerun()

        if submit_answer and user_answer.strip():
            # Ajout de la réponse utilisateur à l'historique
            st.session_state.interview_history.append({"role": "user", "text": user_answer})
            
            # Simulation d'analyse intelligente et génération de la suite
            # (Dans une version connectée à l'IA, on appellera ici la fonction d'appel API de ai.py)
            feedback_simulation = (
                f"💡 **Analyse de votre réponse** :\n"
                f"- *Points forts* : Bonne clarté et structure.\n"
                f"- *Conseil d'amélioration* : Pensez à illustrer avec un chiffre ou un résultat concret.\n\n"
                f"**Question suivante** : Comment gérez-vous une situation de désaccord technique majeur au sein d'une équipe ?"
            )
            
            st.session_state.interview_history.append({"role": "interviewer", "text": feedback_simulation})
            st.rerun()
