import streamlit as st

# Configuration de la page
st.set_page_config(page_title="Argame - Argus Jeux Vidéo", page_icon="🎮")

# Style personnalisé pour le côté "Gaming"
st.markdown("""
    <style>
    .main { background-color: #0f2027; color: white; }
    .stButton>button { background-color: #2ecc71; color: black; border-radius: 10px; width: 100%; }
    .price-box { padding: 10px; border-radius: 10px; background: #2c3e50; margin: 5px 0; }
    </style>
    """, unsafe_allow_html=True)

st.title("🎮 Argame")
st.subheader("L'Argus des collectionneurs")

# Barre de recherche
query = st.text_input("Rechercher un jeu (ex: Pokemon Bleu, Zelda...)", "")

col1, col2 = st.columns(2)
with col1:
    if st.button("📷 Scanner Image"):
        st.info("Reconnaissance d'image en cours de développement...")
with col2:
    if st.button("📊 Voir la Cote"):
        if query:
            st.success(f"Résultats pour : {query}")
            
            # Simulation de données
            st.markdown('<div class="price-box">🧩 **Loose (Cartouche seule)** : 45€ <span style="color:#2ecc71">▲ 5%</span></div>', unsafe_allow_html=True)
            st.markdown('<div class="price-box">📦 **Complet (CIB)** : 120€ <span style="color:#f1c40f">▬ Stable</span></div>', unsafe_allow_html=True)
            st.markdown('<div class="price-box">✨ **Neuf Scellé** : 850€ <span style="color:#e74c3c">▼ 2%</span></div>', unsafe_allow_html=True)
        else:
            st.warning("Veuillez entrer un nom de jeu.")

st.divider()
st.caption("Données simulées - Connexion API PriceCharting à venir.")
