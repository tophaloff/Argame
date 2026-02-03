import streamlit as st
import requests
from bs4 import BeautifulSoup
import cv2
import numpy as np
from pyzbar.pyzbar import decode

# Configuration
st.set_page_config(page_title="Argame Pro", page_icon="🎮")

def get_price(query):
    """Récupère le prix sur PriceCharting"""
    search_url = f"https://www.pricecharting.com/search-products?q={query.replace(' ', '+')}&type=videogames"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        res = requests.get(search_url, headers=headers)
        soup = BeautifulSoup(res.text, 'html.parser')
        row = soup.find('tr', id=lambda x: x and x.startswith('product-'))
        if row:
            name = row.find('td', class_='title').text.strip()
            p_loose = row.find('td', class_='price numeric loose').text.strip()
            p_cib = row.find('td', class_='price numeric cib').text.strip()
            # Conversion € (1.08)
            l_euro = f"{float(p_loose.replace('$','').replace(',',''))/1.08:.2f} €"
            c_euro = f"{float(p_cib.replace('$','').replace(',',''))/1.08:.2f} €"
            return name, l_euro, c_euro
    except: return None, None, None
    return None, None, None

st.title("🎮 Argame")

# --- SECTION SCANNER (Appareil photo masqué par défaut) ---
st.subheader("📸 Scan de jeu")
if "show_camera" not in st.session_state:
    st.session_state.show_camera = False

if not st.session_state.show_camera:
    if st.button("Ouvrir le Scanner / Appareil Photo"):
        st.session_state.show_camera = True
        st.rerun()
else:
    if st.button("Fermer la caméra"):
        st.session_state.show_camera = False
        st.rerun()
    
    img_file = st.camera_input("Placez le code-barre ou le jeu devant l'objectif")
    
    if img_file:
        # Lecture du code-barre
        file_bytes = np.asarray(bytearray(img_file.read()), dtype=np.uint8)
        opencv_image = cv2.imdecode(file_bytes, 1)
        det_barcodes = decode(opencv_image)
        
        if det_barcodes:
            barcode_data = det_barcodes[0].data.decode('utf-8')
            st.success(f"Code-barre détecté : {barcode_data}")
            # On peut essayer de chercher le prix directement avec le code
            name, l, c = get_price(barcode_data)
            if name:
                st.metric(name, f"Loose: {l} | CIB: {c}")
        else:
            st.warning("Aucun code-barre lisible. Essayez de mieux l'éclairer.")

st.divider()

# --- RECHERCHE MANUELLE ---
query = st.text_input("Ou tapez le nom du jeu :")
if query:
    name, l, c = get_price(query)
    if name:
        st.success(f"Résultat : {name}")
        st.write(f"**Loose :** {l} | **Complet :** {c}")
    else:
        st.error("Jeu non trouvé.")
