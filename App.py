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
import time

# --- CONFIGURATION & STYLE ---
st.set_page_config(page_title="Argame Retro", page_icon="🎮", layout="centered")

# Style amélioré : ajout d'effets sur les boutons et conteneurs
st.markdown("""
    <style>
    .stApp { background-color: #9ca0a8 !important; }
    * { color: #000 !important; font-family: 'Helvetica', sans-serif !important; font-weight: bold !important; }
    [data-testid="stSidebar"] { background-color: #bdc3c7 !important; }
    .stMetric { background-color: #ffffff55; padding: 10px; border-radius: 5px; border: 1px solid #333; }
    div.stButton > button { 
        background-color: #8b1d44 !important; 
        color: white !important; 
        border: 2px solid #000 !important;
        width: 100%;
        transition: 0.3s;
    }
    div.stButton > button:hover { transform: scale(1.02); border-color: white !important; }
    </style>
    """, unsafe_allow_html=True)

DB_FILE = "ma_collection.csv"
COLUMNS = ["Jeu", "Prix Loose (€)", "Prix CIB (€)", "Date"]

# --- LOGIQUE DE DONNÉES AMÉLIORÉE ---
def load_db():
    if os.path.exists(DB_FILE):
        try:
            df = pd.read_csv(DB_FILE)
            return df[COLUMNS] if all(col in df.columns for col in COLUMNS) else pd.DataFrame(columns=COLUMNS)
        except: return pd.DataFrame(columns=COLUMNS)
    return pd.DataFrame(columns=COLUMNS)

def save_to_db(res):
    db = load_db()
    # Vérification des doublons sur le nom du jeu
    if res['nom'] in db['Jeu'].values:
        return False, "Ce jeu est déjà dans ta collection !"
    
    new_row = {
        "Jeu": res['nom'], 
        "Prix Loose (€)": res['loose'], 
        "Prix CIB (€)": res['cib'], 
        "Date": datetime.now().strftime("%d/%m/%Y")
    }
    db = pd.concat([db, pd.DataFrame([new_row])], ignore_index=True)
    db.to_csv(DB_FILE, index=False)
    return True, f"✅ {res['nom']} ajouté !"

# --- MOTEUR DE PRIX (PLUS ROBUSTE) ---
@st.cache_data(ttl=3600) # Cache les résultats pendant 1h pour éviter de spammer le site
def get_price(query):
    query = query.strip()
    url = f"https://www.pricecharting.com/search-products?q={query.replace(' ', '+')}&type=videogames"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    
    try:
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code != 200: return None
        
        soup = BeautifulSoup(r.text, 'html.parser')
        name, p_loose, p_cib = None, "0", "0"
        
        # Cas 1 : Liste de résultats
        row = soup.find('tr', id=lambda x: x and x.startswith('product-'))
        if row:
            name = row.find('td', class_='title').text.strip()
            p_loose = row.find('td', class_='price numeric loose').text.strip()
            p_cib = row.find('td', class_='price numeric cib').text.strip()
        # Cas 2 : Fiche produit directe
        else:
            title_tag = soup.find('h1', class_='title')
            if title_tag:
                name = title_tag.text.strip()
                l_tag = soup.find('td', id='loose_price')
                c_tag = soup.find('td', id='cib_price')
                p_loose = l_tag.text.strip() if l_tag else "0"
                p_cib = c_tag.text.strip() if c_tag else "0"

        if name:
            # Nettoyage et conversion (Taux USD/EUR estimé)
            clean = lambda x: float(x.replace('$','').replace(',','').replace('N/A','0').strip() or 0)
            return {"nom": name, "loose": round(clean(p_loose)/1.08, 2), "cib": round(clean(p_cib)/1.08, 2)}
    except Exception as e:
        return None
    return None

# --- INTERFACE ---
with st.sidebar:
    st.markdown("# 🎮 ARGAME")
    page = st.radio("NAVIGATION", ["🔍 SCAN & CHERCHE", "📦 COLLECTION"])
    st.info(f"Fichier : `{DB_FILE}`")

if page == "🔍 SCAN & CHERCHE":
    st.title("📟 RECHERCHE RETRO")
    
    tab1, tab2 = st.tabs(["⌨️ RECHERCHE MANUELLE", "📸 SCANNER"])
    
    with tab1:
        jeu_cherche = st.text_input("NOM DU JEU :", key="manual_search")
        
    with tab2:
        img_file = st.camera_input("SCANNE LE CODE-BARRE")
        if img_file:
            file_bytes = np.asarray(bytearray(img_file.read()), dtype=np.uint8)
            img = cv2.imdecode(file_bytes, 1)
            barcodes = decode(img)
            if barcodes:
                jeu_cherche = barcodes[0].data.decode('utf-8')
                st.success(f"Code-barre trouvé : {jeu_cherche}")
            else:
                # Tentative OCR simplifiée
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                jeu_cherche = pytesseract.image_to_string(gray).strip()
                st.write(f"Texte détecté : {jeu_cherche}")

    if jeu_cherche:
        res = get_price(jeu_cherche)
        if res:
            st.divider()
            st.subheader(f"🎯 {res['nom']}")
            c1, c2 = st.columns(2)
            c1.metric("LOOSE", f"{res['loose']} €")
            c2.metric("COMPLET (CIB)", f"{res['cib']} €")
            
            if st.button("➕ AJOUTER À MA COLLECTION"):
                success, msg = save_to_db(res)
                if success: st.success(msg)
                else: st.warning(msg)
        else:
            st.error("Jeu non trouvé. Essaye d'être plus précis (ex: Console + Nom).")

else:
    st.title("📦 MA COLLECTION")
    db = load_db()
    
    if not db.empty:
        valeur_totale = db["Prix Loose (€)"].sum()
        st.metric("VALEUR ESTIMÉE (LOOSE)", f"{round(valeur_totale, 2)} €")
        
        st.dataframe(db, use_container_width=True, hide_index=True)
        
        if st.button("🗑️ RÉINITIALISER LA COLLECTION"):
            if os.path.exists(DB_FILE): os.remove(DB_FILE)
            st.rerun()
    else:
        st.info("Ta collection est vide pour le moment.")
