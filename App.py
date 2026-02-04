import streamlit as st
import requests
from bs4 import BeautifulSoup
import cv2
import numpy as np
import pandas as pd
import os
from datetime import datetime
import pytesseract

# --- CONFIGURATION & STYLE RETRO ---
st.set_page_config(page_title="Argame Retro Pro", page_icon="🎮")

st.markdown("""
    <style>
    .stApp { background-color: #9ca0a8 !important; }
    * { color: #000 !important; font-family: 'Helvetica', sans-serif !important; font-weight: bold !important; }
    div.stButton > button { background-color: #8b1d44 !important; color: white !important; width: 100%; border: 2px solid #000; }
    .stMetric { background-color: #ffffff55; padding: 10px; border-radius: 5px; border: 1px solid #333; }
    </style>
    """, unsafe_allow_html=True)

DB_FILE = "ma_collection.csv"
COLUMNS = ["Jeu", "Prix Loose (€)", "Prix CIB (€)", "Date"]

# --- FONCTIONS DE BASE ---
def load_db():
    if os.path.exists(DB_FILE):
        try:
            return pd.read_csv(DB_FILE)
        except: return pd.DataFrame(columns=COLUMNS)
    return pd.DataFrame(columns=COLUMNS)

def get_price(query):
    # Nettoyage pour PriceCharting
    query = query.replace("Playstation 5", "PS5").replace("Playstation 4", "PS4").strip()
    url = f"https://www.pricecharting.com/search-products?q={query.replace(' ', '+')}&type=videogames"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    try:
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, 'html.parser')
        
        # Test 1 : Fiche produit directe
        name_tag = soup.find('h1', class_='title')
        if name_tag:
            name = name_tag.text.strip()
            p_loose = soup.find('td', id='loose_price').text.strip() if soup.find('td', id='loose_price') else "0"
            p_cib = soup.find('td', id='cib_price').text.strip() if soup.find('td', id='cib_price') else "0"
        # Test 2 : Liste de résultats
        else:
            row = soup.find('tr', id=lambda x: x and x.startswith('product-'))
            if row:
                name = row.find('td', class_='title').text.strip()
                p_loose = row.find('td', class_='price numeric loose').text.strip()
                p_cib = row.find('td', class_='price numeric cib').text.strip()
            else: return None

        clean = lambda x: float(x.replace('$','').replace(',','').replace('N/A','0').strip() or 0)
        return {"nom": name, "loose": round(clean(p_loose)/1.08, 2), "cib": round(clean(p_cib)/1.08, 2)}
    except: return None

# --- INTERFACE PRINCIPALE ---
st.title("🕹️ ARGAME PRO")

menu = st.sidebar.radio("MENU", ["🔍 RECHERCHE", "📦 COLLECTION"])

if menu == "🔍 RECHERCHE":
    # Choix de la méthode
    methode = st.radio("Méthode :", ["⌨️ Saisie Manuelle", "📸 Photo (Objectif Arrière)"])
    
    jeu_a_chercher = ""

    if methode == "⌨️ Saisie Manuelle":
        with st.form("search_form"):
            jeu_saisi = st.text_input("Nom du jeu :", placeholder="ex: Star Wars Outlaws PS5")
            valider = st.form_submit_button("LANCER LA RECHERCHE")
            if valider:
                jeu_a_chercher = jeu_saisi

    else:
        # Utiliser file_uploader pour forcer l'accès à l'appareil photo arrière sur mobile
        img_file = st.file_uploader("Prends une photo du titre", type=['jpg', 'jpeg', 'png'])
        if img_file:
            with st.spinner("Lecture de l'image..."):
                file_bytes = np.asarray(bytearray(img_file.read()), dtype=np.uint8)
                img = cv2.imdecode(file_bytes, 1)
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                jeu_a_chercher = pytesseract.image_to_string(gray).strip()
                st.info(f"Texte lu : {jeu_a_chercher}")

    # Exécution de la recherche
    if jeu_a_chercher:
        with st.spinner("Recherche du prix..."):
            res = get_price(jeu_a_chercher)
            if res:
                st.markdown(f"### 🎯 {res['nom']}")
                c1, c2 = st.columns(2)
                c1.metric("LOOSE", f"{res['loose']} €")
                c2.metric("COMPLET", f"{res['cib']} €")
                
                if st.button("➕ AJOUTER À MA COLLECTION"):
                    db = load_db()
                    if res['nom'] not in db['Jeu'].values:
                        new_row = {"Jeu": res['nom'], "Prix Loose (€)": res['loose'], "Prix CIB (€)": res['cib'], "Date": datetime.now().strftime("%d/%m/%Y")}
                        pd.concat([db, pd.DataFrame([new_row])]).to_csv(DB_FILE, index=False)
                        st.success("Jeu enregistré !")
                    else:
                        st.warning("Déjà dans la collection !")
            else:
                st.error("Prix introuvable. Essaye de simplifier le nom.")

else:
    st.title("📦 MA COLLECTION")
    db = load_db()
    if not db.empty:
        st.metric("VALEUR TOTALE", f"{round(db['Prix Loose (€)'].sum(), 2)} €")
        st.dataframe(db, use_container_width=True, hide_index=True)
        if st.button("🗑️ TOUT EFFACER"):
            if os.path.exists(DB_FILE): os.remove(DB_FILE)
            st.rerun()
    else:
        st.info("Ta collection est vide.")
