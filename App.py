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
st.set_page_config(page_title="Argame Retro", page_icon="🎮", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #9ca0a8 !important; }
    html, body, [class*="css"], .stMarkdown, p, h1, h2, h3, label, span {
        color: #000000 !important;
        font-family: 'Helvetica', sans-serif !important;
        font-weight: bold !important;
    }
    [data-testid="stSidebar"] { background-color: #bdc3c7 !important; }
    .stAlert, div[data-testid="stExpander"] {
        background-color: #8bac0f !important;
        border: 3px solid #333 !important;
    }
    div.stButton > button {
        background-color: #8b1d44 !important;
        color: white !important;
        border: 2px solid #000 !important;
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

DB_FILE = "ma_collection.csv"

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

def load_db():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    return pd.DataFrame(columns=["Jeu", "Prix Loose (€)", "Prix CIB (€)", "Date"])

# --- MENU ---
with st.sidebar:
    st.title("🕹️ MENU")
    page = st.sidebar.radio("ALLER À :", ["🔍 SCANNER / CHERCHER", "📦 MA COLLECTION"])

# --- PAGE SCANNER ---
if page == "🔍 SCANNER / CHERCHER":
    st.title("📟 SCANNER UN JEU")
    
    # 1. Option Photo / Scan
    img_file = st.camera_input("SCANNE LE CODE-BARRE OU LE TITRE")
    
    query_found = ""
    
    if img_file:
        file_bytes = np.asarray(bytearray(img_file.read()), dtype=np.uint8)
        img = cv2.imdecode(file_bytes, 1)
        
        # Détection Code-Barres
        barcodes = decode(img)
        if barcodes:
            query_found = barcodes[0].data.decode('utf-8')
            st.info(f"Code-barres détecté : {query_found}")
        else:
            # OCR si pas de code-barre
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            query_found = pytesseract.image_to_string(gray).strip()
            if len(query_found) > 3:
                st.info(f"Texte lu sur l'image : {query_found}")

    # 2. Option Manuelle (ou pré-remplie par le scan)
    st.write("---")
    jeu_cherche = st.text_input("NOM DU JEU (OU VALEUR SCANNEE) :", value=query_found)
    
    if jeu_cherche:
        with st.spinner('Recherche du prix...'):
            res = get_price(jeu_cherche)
            if res:
                st.success(f"TROUVÉ : {res['nom']}")
                col1, col2 = st.columns(2)
                col1.metric("LOOSE", f"{res['loose']} €")
                col2.metric("COMPLET", f"{res['cib']} €")
                
                if st.button("➕ AJOUTER À LA COLLECTION"):
                    db = load_db()
                    new_row = {"Jeu": res['nom'], "Prix Loose (€)": res['loose'], "Prix CIB (€)": res['cib'], "Date": datetime.now().strftime("%d/%m/%Y")}
                    db = pd.concat([db, pd.DataFrame([new_row])], ignore_index=True)
                    db.to_csv(DB_FILE, index=False)
                    st.toast("C'est dans la boîte !")
            else:
                st.error("Rien trouvé. Vérifie l'orthographe ou tape le nom manuellement.")

else: # --- PAGE COLLECTION ---
    st.title("📦 MA COLLECTION")
    db = load_db()
    if not db.empty:
        total = db["Prix Loose (€)"].sum()
        st.subheader(f"VALEUR TOTALE : {round(total, 2)} €")
        st.dataframe(db, use_container_width=True)
        if st.button("🗑️ TOUT SUPPRIMER"):
            if os.path.exists(DB_FILE): os.remove(DB_FILE)
            st.rerun()
    else:
        st.info("Ta collection est vide.")
