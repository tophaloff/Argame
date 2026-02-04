import streamlit as st
import requests
from bs4 import BeautifulSoup
import cv2
import numpy as np
import pandas as pd
import os
from datetime import datetime

# --- CONFIG ---
DB_FILE = "ma_collection.csv"

# --- AMÉLIORATION DU MOTEUR DE RECHERCHE ---
def get_price(query):
    if not query or len(query) < 3: return None
    
    # On ajoute des mots clés pour aider PriceCharting
    url = f"https://www.pricecharting.com/search-products?q={query.replace(' ', '+')}&type=videogames"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    try:
        r = requests.get(url, headers=headers, timeout=5)
        soup = BeautifulSoup(r.text, 'html.parser')
        
        # On cherche d'abord dans le tableau de résultats
        product_row = soup.find('tr', id=lambda x: x and x.startswith('product-'))
        if product_row:
            name = product_row.find('td', class_='title').text.strip()
            # On nettoie les prix plus agressivement
            p_loose = product_row.find('td', class_='price numeric loose').text.replace('$','').strip()
            p_cib = product_row.find('td', class_='price numeric cib').text.replace('$','').strip()
            
            # Conversion propre
            l = float(p_loose) / 1.08 if p_loose != "N/A" else 0
            c = float(p_cib) / 1.08 if p_cib != "N/A" else 0
            return {"nom": name, "loose": round(l, 2), "cib": round(c, 2)}
    except:
        return None
    return None

# --- INTERFACE ---
st.title("🎮 Argame Scan Pro")

# Astuce pour la caméra : sur Android/iPhone, utiliser l'upload d'image 
# permet de choisir "Appareil Photo" et d'utiliser l'objectif arrière avec autofocus.
source = st.radio("Méthode de scan :", ["Photo (Objectif Arrière)", "Saisie Manuelle"])

jeu_a_chercher = ""

if source == "Photo (Objectif Arrière)":
    # On utilise file_uploader au lieu de camera_input car il permet d'utiliser l'app photo native du téléphone (donc l'objectif arrière)
    img_file = st.file_uploader("Prends une photo du titre du jeu", type=['jpg', 'png', 'jpeg'])
    if img_file:
        with st.spinner("Analyse du titre..."):
            file_bytes = np.asarray(bytearray(img_file.read()), dtype=np.uint8)
            img = cv2.imdecode(file_bytes, 1)
            # Prétraitement pour aider l'OCR
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            # On peut ajouter un seuillage pour le contraste
            jeu_a_chercher = pytesseract.image_to_string(gray).strip()
            st.write(f"🔍 J'ai lu : **{jeu_a_chercher}**")

else:
    jeu_a_chercher = st.text_input("Tape le nom du jeu :")

if jeu_a_chercher:
    res = get_price(jeu_a_chercher)
    if res:
        st.success(f"Trouvé : {res['nom']}")
        st.metric("Prix Loose", f"{res['loose']} €")
        if st.button("💾 Sauvegarder dans la collection"):
            # Sauvegarde locale (en attendant un Google Sheet)
            df = pd.read_csv(DB_FILE) if os.path.exists(DB_FILE) else pd.DataFrame(columns=["Jeu", "Prix", "Date"])
            new_data = pd.DataFrame([{"Jeu": res['nom'], "Prix": res['loose'], "Date": datetime.now()}])
            pd.concat([df, new_data]).to_csv(DB_FILE, index=False)
            st.balloons()
    else:
        st.warning("Je n'ai pas trouvé de prix. Essaie d'ajouter la console (ex: 'Zelda NES')")
