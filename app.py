"""PAVEL IA CV PRO — application Streamlit moderne."""

import datetime
import re

import streamlit as st

import ai
import exporters
from config import COUNTRIES, CV_TYPES, LANGS, LEVELS, TEMPLATES, has


# ============================================================
# CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Pavel IA CV Pro",
    page_icon="✨",
    layout="centered",
    initial_sidebar_state="collapsed",
)


# ============================================================
# DESIGN PREMIUM
# ============================================================

st.markdown(
    """
<style>

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

:root {
    --bg: #070b14;
    --card: rgba(18, 24, 39, 0.82);
    --card2: rgba(24, 32, 52, 0.72);
    --border: rgba(255,255,255,0.10);
    --text: #f8fafc;
    --muted: #94a3b8;
    --blue: #4f8cff;
    --purple: #8b5cf6;
    --cyan: #22d3ee;
    --green: #22c55e;
}

html,
body,
[data-testid="stAppViewContainer"] {
    background:
        radial-gradient(circle at 10% 5%, rgba(79,140,255,0.15), transparent 28%),
        radial-gradient(circle at 90% 10%, rgba(139,92,246,0.13), transparent 25%),
        radial-gradient(circle at 50% 100%, rgba(34,211,238,0.08), transparent 30%),
        var(--bg);
    color: var(--text);
}

[data-testid="stHeader"] {
    background: transparent;
}

[data-testid="stToolbar"] {
    visibility: hidden;
}

* {
    font-family: "Inter", sans-serif;
}

.block-container {
    max-width: 900px;
    padding-top: 1.2rem;
    padding-bottom: 4rem;
}

.hero {
    position: relative;
    overflow: hidden;
    padding: 2rem 1.5rem;
    margin-bottom: 1.4rem;
    border-radius: 26px;
    border: 1px solid rgba(255,255,255,0.12);
    background:
        linear-gradient(
            135deg,
            rgba(79,140,255,0.22),
            rgba(139,92,246,0.20),
            rgba(7,11,20,0.92)
        );
    box-shadow:
        0 25px 80px rgba(0,0,0,0.35),
        inset 0 1px 0 rgba(255,255,255,0.08);
    text-align: center;
}

.hero::before {
    content: "";
    position: absolute;
    width: 240px;
    height: 240px;
    top: -130px;
    right: -80px;
    border-radius: 50%;
    background: rgba(79,140,255,0.20);
    filter: blur(25px);
    animation: floatGlow 5s ease-in-out infinite;
}

.hero::after {
    content: "";
    position: absolute;
    width: 180px;
    height: 180px;
    bottom: -110px;
    left: -70px;
    border-radius: 50%;
    background: rgba(139,92,246,0.18);
    filter: blur(25px);
    animation: floatGlow2 6s ease-in-out infinite;
}

.hero-content {
    position: relative;
    z-index: 2;
}

.hero h1 {
    margin: 0;
    font-size: clamp(2.3rem, 8vw, 4rem);
    font-weight: 800;
    letter-spacing: -2px;
    background: linear-gradient(
        90deg,
        #ffffff,
        #8fc1ff,
        #b794ff,
        #ffffff
    );
    background-size: 250
