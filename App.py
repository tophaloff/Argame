import streamlit as st

# Configuration look & feel
st.set_page_config(page_title="Argame - Argus Jeux Vidéo", page_icon="🎮")

st.markdown("""
    <style>
    .main { background: linear-gradient(135deg, #0f2027, #203a43); color: white; }
    .stButton>button { background-color: #2ecc71; color: black; font-weight: bold; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🎮 Argame")
st.write("Scannez ou recherchez la cote de vos jeux vidéo.")

# 1. Option de Scan (Photo)
st.subheader("📸 Reconnaissance par image")
image_file = st.camera_input("Prenez une photo du jeu (loose ou boîte)")

if image_file:
    st.image(image_file, caption="Image capturée", use_container_width=True)
    st.info("Analyse de l'image en cours... (Bientôt disponible avec l'IA)")

st.divider()

# 2. Recherche manuelle
st.subheader("🔍 Recherche manuelle")
nom_jeu = st.text_input("Entrez le nom du jeu :")

if nom_jeu:
    # Simulation de résultats
    st.success(f"Résultats pour : {nom_jeu}")
    col1, col2, col3 = st.columns(3)
    col1.metric("Loose", "45€", "+5%")
    col2.metric("Complet (CIB)", "120€", "Stable")
    col3.metric("Neuf", "850€", "-2%")
