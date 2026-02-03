import streamlit as st
import requests
from bs4 import BeautifulSoup

st.set_page_config(page_title="Argame - Argus Gratuit", page_icon="🎮")

# --- FONCTION DE RÉCUPÉRATION DES PRIX ---
def get_price_charting(game_name):
    # On prépare l'URL de recherche
    search_url = f"https://www.pricecharting.com/search-products?q={game_name.replace(' ', '+')}&type=videogames"
    headers = {"User-Agent": "Mozilla/5.0"} # Pour ne pas être bloqué par le site
    
    try:
        response = requests.get(search_url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # On cherche le premier tableau de résultats
        product_row = soup.find('tr', id=lambda x: x and x.startswith('product-'))
        
        if product_row:
            name = product_row.find('td', class_='title').text.strip()
            # Extraction des prix (on nettoie les symboles $)
            price_loose = product_row.find('td', class_='price numeric loose').text.strip()
            price_cib = product_row.find('td', class_='price numeric cib').text.strip()
            
            return {"nom": name, "loose": price_loose, "cib": price_cib}
        return None
    except:
        return None

# --- INTERFACE ---
st.title("🎮 Argame")
st.write("Récupération des prix en direct de PriceCharting")

query = st.text_input("Nom du jeu (ex: Mario 64, Zelda...)")

if query:
    with st.spinner('Recherche de la cote...'):
        result = get_price_charting(query)
        
        if result:
            st.success(f"Résultat trouvé : **{result['nom']}**")
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Prix Loose (Cartouche)", result['loose'])
            with col2:
                st.metric("Prix Complet (CIB)", result['cib'])
            
            st.info("Note : Les prix sont convertis du $ vers l'€ approximativement selon le marché US.")
        else:
            st.error("Désolé, je n'ai pas trouvé ce jeu. Essayez d'être plus précis.")

st.divider()
st.subheader("📸 Scan / Photo")
st.camera_input("Scanner pour archive")
