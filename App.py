import streamlit as st
import pandas as pd

st.set_page_config(page_title="Argame - Argus Pro", page_icon="🎮")

# --- BASE DE DONNÉES FICTIVE (À remplacer par une API plus tard) ---
data = {
    "jeu": ["Pokemon Bleu", "Zelda Ocarina of Time", "Mario 64", "Sonic Adventure"],
    "console": ["Gameboy", "N64", "N64", "Dreamcast"],
    "loose": [45, 50, 35, 25],
    "cib": [150, 130, 100, 60],
    "neuf": [900, 850, 600, 200]
}
df = pd.DataFrame(data)

st.title("🎮 Argame")

# --- RECHERCHE ---
query = st.text_input("Rechercher un titre (ex: Pokemon)...")

if query:
    # On cherche dans notre base de données
    resultats = df[df['jeu'].str.contains(query, case=False)]
    
    if not resultats.empty:
        for index, row in resultats.iterrows():
            st.header(f"{row['jeu']} ({row['console']})")
            c1, c2, c3 = st.columns(3)
            c1.metric("Loose", f"{row['loose']}€")
            c2.metric("Complet", f"{row['cib']}€")
            c3.metric("Neuf", f"{row['neuf']}€")
    else:
        st.error("Jeu non trouvé dans la base de données actuelle.")

st.divider()
st.subheader("📸 Scan de cartouche")
st.camera_input("Prendre une photo")
