import streamlit as st
import requests
from bs4 import BeautifulSoup
import cv2
import numpy as np
from pyzbar.pyzbar import decode
import pytesseract
import pandas as pd
import os
from datetime import datetime

# --- CONFIGURATION & STYLE ---
st.set_page_config(page_title="Argame Retro", page_icon="🎮")

st.markdown("""
    <style>
    .stApp { background-color: #9ca0a8 !important; }
    * { color: #000 !important; font-family: 'Helvetica', sans-serif !important; font-weight: bold !important; }
    [data-testid="stSidebar"] { background-color: #bdc3c7 !important; }
    .stAlert, div[data-testid="stExpander"] { background-color: #8bac0f !important; border: 2px solid #333 !important; }
    div.stButton > button { background-color: #8b1d44 !important; color: white !important; border: 2px solid #000 !important; }
    </style>
    """, unsafe_allow_html=True)

DB_FILE = "ma_collection.csv"
COLUMNS = ["Jeu", "Prix Loose (€)", "Prix CIB (€)", "Date"]

# --- GESTION DE LA BASE DE DONNÉES (CORRECTION ERREUR) ---
def load_db():
    if os.path.exists(DB_FILE):
        try:
            df = pd.read_csv(DB_FILE)
            # Vérifie que toutes les colonnes sont présentes pour éviter l'erreur
            if all(col in df.columns for col in COLUMNS):
                return df
        except:
            pass
    # Si le fichier est corrompu ou absent, on en crée un tout neuf
    return pd.DataFrame(columns=COLUMNS)

# --- MOTEUR DE PRIX ---
def get_price(query):
    query = query.strip()
    url = f"https://www.pricecharting.com/search-products?q={query.replace(' ', '+')}&type=videogames"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, 'html.parser')
        name, p_loose, p_cib = "", "0", "0"
        
        row = soup.find('tr', id=lambda x: x and x.startswith('product-'))
        if row:
            name = row.find('td', class_='title').text.strip()
            p_loose = row.find('td', class_='price numeric loose').text.strip()
            p_cib = row.find('td', class_='price numeric cib').text.strip()
        else:
            title_tag = soup.find('h1', class_='title')
            if title_tag:
                name = title_tag.text.strip()
                l_tag = soup.find('td', id='loose_price')
                c_tag = soup.find('td', id='cib_price')
                p_loose = l_tag.text.strip() if l_tag else "0"
                p_cib = c_tag.text.strip() if c_tag else "0"

        if name:
            l = float(p_loose.replace('$','').replace(',','').strip()) / 1.08
            c = float(p_cib.replace('$','').replace(',','').strip()) / 1.08
            return {"nom": name, "loose": round(l, 2), "cib": round(c, 2)}
    except: return None
    return None

# --- NAVIGATION ---
with st.sidebar:
    st.title("🕹️ MENU")
    page = st.radio("ALLER À :", ["🔍 CHERCHER / SCANNER", "📦 MA COLLECTION"])

# --- PAGE RECHERCHE & SCAN ---
if page == "🔍 CHERCHER / SCANNER":
    st.title("📟 RECHERCHE")
    
    # Zone de recherche manuelle par défaut
    jeu_cherche = st.text_input("NOM DU JEU :", placeholder="Ex: Super Mario World")
    
    # BOUTON DE CONSENTEMENT POUR L'APPAREIL PHOTO
    st.write("---")
    if "camera_on" not in st.session_state:
        st.session_state.camera_on = False

    if not st.session_state.camera_on:
        if st.button("📸 ACTIVER LE SCANNER (APPAREIL PHOTO)"):
            st.session_state.camera_on = True
            st.rerun()
    else:
        if st.button("❌ FERMER LA CAMERA"):
            st.session_state.camera_on = False
            st.rerun()
        
        img_file = st.camera_input("SCANNE LE CODE-BARRE OU LE TITRE")
        if img_file:
            file_bytes = np.asarray(bytearray(img_file.read()), dtype=np.uint8)
            img = cv2.imdecode(file_bytes, 1)
            barcodes = decode(img)
            if barcodes:
                jeu_cherche = barcodes[0].data.decode('utf-8')
                st.success(f"Code détecté : {jeu_cherche}")
            else:
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                jeu_cherche = pytesseract.image_to_string(gray).strip()

    if jeu_cherche:
        with st.spinner('Recherche...'):
            res = get_price(jeu_cherche)
            if res:
                st.markdown(f"### 🎯 {res['nom']}")
                col1, col2 = st.columns(2)
                col1.metric("LOOSE", f"{res['loose']} €")
                col2.metric("COMPLET", f"{res['cib']} €")
                
                if st.button("➕ AJOUTER À LA COLLECTION"):
                    db = load_db()
                    new_row = {"Jeu": res['nom'], "Prix Loose (€)": res['loose'], "Prix CIB (€)": res['cib'], "Date": datetime.now().strftime("%d/%m/%Y")}
                    db = pd.concat([db, pd.DataFrame([new_row])], ignore_index=True)
                    db.to_csv(DB_FILE, index=False)
                    st.toast("Ajouté !")

# --- PAGE COLLECTION (SANS ERREUR) ---
else:
    st.title("📦 MA COLLECTION")
    db = load_db()
    if not db.empty:
        total = db["Prix Loose (€)"].sum()
        st.subheader(f"VALEUR TOTALE : {round(total, 2)} €")
        
        # Affichage propre sous forme de tableau
        st.dataframe(db, use_container_width=True, hide_index=True)
        
        if st.button("🗑️ TOUT EFFACER"):
            if os.path.exists(DB_FILE): os.remove(DB_FILE)
            st.rerun()
    else:
        st.info("Ta collection est vide.")
