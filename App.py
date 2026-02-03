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
    .stApp, [data-testid="stSidebar"] { background-color: #9ca0a8 !important; }
    * { color: #000000 !important; font-family: 'Courier New', monospace !important; font-weight: bold !important; }
    .stAlert, div[data-testid="stExpander"] { background-color: #8bac0f !important; border: 2px solid #333 !important; }
    div.stButton > button { background-color: #8b1d44 !important; color: white !important; border: 2px solid #000 !important; }
    </style>
    """, unsafe_allow_html=True)

DB_FILE = "ma_collection.csv"

# --- FONCTION DE RECHERCHE AMÉLIORÉE ---
def get_price(query):
    # On nettoie la recherche (enlève les retours à la ligne et espaces inutiles)
    query = query.strip().replace('\n', ' ')
    if not query or len(query) < 3: 
        return None
        
    url = f"https://www.pricecharting.com/search-products?q={query.replace(' ', '+')}&type=videogames"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    try:
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # 1. On cherche d'abord dans un tableau de résultats
        row = soup.find('tr', id=lambda x: x and x.startswith('product-'))
        
        # 2. Si on est directement sur la page du produit (PriceCharting redirige parfois)
        if not row:
            name_tag = soup.find('h1', class_='title')
            if name_tag:
                name = name_tag.text.strip()
                p_loose = soup.find('td', id='loose_price').find('span', class_='price').text.strip()
                p_cib = soup.find('td', id='cib_price').find('span', class_='price').text.strip()
                val_loose = float(p_loose.replace('$','').replace(',','')) / 1.08
                val_cib = float(p_cib.replace('$','').replace(',','')) / 1.08
                return {"nom": name, "loose": round(val_loose, 2), "cib": round(val_cib, 2)}
        
        # 3. Extraction classique depuis la liste
        if row:
            name = row.find('td', class_='title').text.strip()
            p_loose = row.find('td', class_='price numeric loose').text.strip()
            p_cib = row.find('td', class_='price numeric cib').text.strip()
            val_loose = float(p_loose.replace('$','').replace(',','')) / 1.08
            val_cib = float(p_cib.replace('$','').replace(',','')) / 1.08
            return {"nom": name, "loose": round(val_loose, 2), "cib": round(val_cib, 2)}
            
    except Exception as e:
        st.sidebar.error(f"Erreur technique: {e}")
        return None
    return None

def load_db():
    cols = ["Jeu", "Prix Loose (€)", "Prix CIB (€)", "Date Ajout"]
    if os.path.exists(DB_FILE):
        try:
            df = pd.read_csv(DB_FILE)
            if all(c in df.columns for c in cols): return df
        except: pass
    return pd.DataFrame(columns=cols)

# --- INTERFACE ---
st.sidebar.title("🕹️ MENU")
page = st.sidebar.radio("MODES", ["🔍 SCANNER", "📦 MA COLLECTION"])

if page == "🔍 SCANNER":
    st.title("📟 NOUVEAU SCAN")
    
    # Zone de texte pour taper à la main si le scan échoue
    manual_query = st.text_input("NOM DU JEU (ex: Zelda NES)")
    
    if st.button("🔴 CAMERA"):
        img_file = st.camera_input("SCAN")
        if img_file:
            file_bytes = np.asarray(bytearray(img_file.read()), dtype=np.uint8)
            img = cv2.imdecode(file_bytes, 1)
            
            # Détection Code-Barres
            barcodes = decode(img)
            if barcodes:
                query = barcodes[0].data.decode('utf-8')
                st.info(f"Code-barres détecté : {query}")
                manual_query = query
            else:
                # Si pas de code-barres, on tente l'OCR (lecture du titre)
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                query = pytesseract.image_to_string(gray).strip()
                if len(query) > 2:
                    st.info(f"Texte lu : {query}")
                    manual_query = query

    if manual_query:
        with st.spinner(f"RECHERCHE DE '{manual_query}'..."):
            res = get_price(manual_query)
            if res:
                st.markdown(f"### 🎯 {res['nom']}")
                c1, c2 = st.columns(2)
                c1.metric("LOOSE", f"{res['loose']}€")
                c2.metric("CIB", f"{res['cib']}€")
                if st.button("➕ AJOUTER"):
                    db = load_db()
                    new_row = {"Jeu": res['nom'], "Prix Loose (€)": res['loose'], "Prix CIB (€)": res['cib'], "Date Ajout": datetime.now().strftime("%d/%m/%Y")}
                    db = pd.concat([db, pd.DataFrame([new_row])], ignore_index=True)
                    db.to_csv(DB_FILE, index=False)
                    st.success("ENREGISTRÉ !")
            else:
                st.error("AUCUN RÉSULTAT. ESSAYEZ UN NOM PLUS PRÉCIS.")

else:
    st.title("📦 MA COLLECTION")
    # ... (Le reste du code pour la collection reste le même)
