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

# --- CONFIGURATION & STYLE GAMEBOY ULTIME ---
st.set_page_config(page_title="Argame Retro", page_icon="🎮", layout="centered")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=VT323&display=swap');

    /* Fond de la console */
    .stApp {
        background-color: #9ca0a8 !important;
    }

    /* TOUT LE TEXTE EN NOIR PAR DÉFAUT */
    * {
        font-family: 'VT323', monospace !important;
        color: #000000 !important;
        font-size: 1.3rem !important;
    }

    /* TITRES PLUS GRANDS */
    h1, h2, h3 {
        font-size: 2.5rem !important;
        text-transform: uppercase;
        color: #1a1a1a !important;
    }

    /* L'ÉCRAN VERT LCD (Conteneurs de texte) */
    .stAlert, div[data-testid="stExpander"], div[data-baseweb="notification"] {
        background-color: #8bac0f !important;
        border: 3px solid #333 !important;
        border-radius: 0px !important;
    }
    
    /* CORRECTION LISIBILITÉ MESSAGES (Rouge/Bleu/Jaune) */
    div[data-testid="stNotificationContent"] p, .stAlert p {
        color: #0f380f !important; /* Vert foncé sur fond vert LCD */
        font-weight: bold !important;
        font-size: 1.5rem !important;
    }

    /* INPUT (Zone de saisie) */
    input {
        background-color: #cadc9f !important;
        color: #0f380f !important;
        border: 3px solid #333 !important;
        font-size: 1.4rem !important;
    }

    /* BOUTONS (Rouge bordeaux) */
    div.stButton > button {
        background-color: #8b1d44 !important;
        color: #ffffff !important;
        border: 3px solid #333;
        font-size: 1.6rem !important;
        text-transform: uppercase;
        box-shadow: 4px 4px 0px #444;
    }

    /* METRICS (Prix) */
    div[data-testid="stMetric"] label, div[data-testid="stMetricValue"] {
        color: #0f380f !important;
        background-color: #8bac0f;
    }
    </style>
    """, unsafe_allow_html=True)

# --- GARDE LE RESTE DU CODE (get_price, load_db, etc.) IDENTIQUE ---
# ... (Tes fonctions techniques ici) ...

DB_FILE = "ma_collection.csv"

def get_price(query):
    if not query or len(query) < 3: return None
    url = f"https://www.pricecharting.com/search-products?q={query.replace(' ', '+')}&type=videogames"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        res = requests.get(url, headers=headers, timeout=5)
        soup = BeautifulSoup(res.text, 'html.parser')
        row = soup.find('tr', id=lambda x: x and x.startswith('product-'))
        if row:
            name = row.find('td', class_='title').text.strip()
            p_loose = row.find('td', class_='price numeric loose').text.strip()
            p_cib = row.find('td', class_='price numeric cib').text.strip()
            val_loose = float(p_loose.replace('$','').replace(',','')) / 1.08
            val_cib = float(p_cib.replace('$','').replace(',','')) / 1.08
            return {"nom": name, "loose": round(val_loose, 2), "cib": round(val_cib, 2)}
    except: return None
    return None

def load_db():
    cols = ["Jeu", "Prix Loose (€)", "Prix CIB (€)", "Date Ajout"]
    if os.path.exists(DB_FILE):
        try:
            df = pd.read_csv(DB_FILE)
            if all(c in df.columns for c in cols):
                return df
        except: pass
    return pd.DataFrame(columns=cols)

# --- INTERFACE ---
st.sidebar.title("🕹️ MENU")
menu = st.sidebar.radio("", ["🔍 SCAN", "📦 COLLECTION"])

if menu == "🔍 SCAN":
    st.header("📟 SCANNER")
    manual_query = st.text_input("NOM DU JEU / EAN", placeholder="Ex: Pokemon Blue")
    
    if st.button("🔴 START CAMERA"):
        img_file = st.camera_input("SCAN")
        if img_file:
            file_bytes = np.asarray(bytearray(img_file.read()), dtype=np.uint8)
            img = cv2.imdecode(file_bytes, 1)
            barcodes = decode(img)
            query = barcodes[0].data.decode('utf-8') if barcodes else ""
            if not query:
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                query = pytesseract.image_to_string(gray).strip()
            if len(query) > 2: manual_query = query

    if manual_query:
        res = get_price(manual_query)
        if res:
            st.markdown(f"### 🎮 {res['nom']}")
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
            st.error("RIEN TROUVÉ")

else:
    st.header("📦 MA COLLECTION")
    db = load_db()
    
    if not db.empty:
        total = db["Prix Loose (€)"].sum()
        st.subheader(f"VALEUR TOTALE: {round(total, 2)} €")
        
        if st.button("🔄 ACTUALISER LES COTES"):
            with st.spinner("MAJ..."):
                for i, row in db.iterrows():
                    upd = get_price(row['Jeu'])
                    if upd:
                        db.at[i, "Prix Loose (€)"] = upd['loose']
                        db.at[i, "Prix CIB (€)"] = upd['cib']
                db.to_csv(DB_FILE, index=False)
                st.rerun()

        for index, row in db.iterrows():
            with st.expander(f"• {row['Jeu']}"):
                st.write(f"Loose: {row['Prix Loose (€)']}€ | CIB: {row['Prix CIB (€)']}€")
                if st.button(f"🗑️ SUPPRIMER", key=f"del_{index}"):
                    db = db.drop(index)
                    db.to_csv(DB_FILE, index=False)
                    st.rerun()
    else:
        st.info("COLLECTION VIDE")
