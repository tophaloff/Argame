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

# --- CONFIGURATION & STYLE GAMEBOY OPTIMISÉ ---
st.set_page_config(page_title="Argame Retro", page_icon="🎮", layout="centered")

st.markdown("""
    <style>
    /* Police Google Fonts style Retro */
    @import url('https://fonts.googleapis.com/css2?family=VT323&display=swap');

    .main {
        background-color: #9ca0a8; 
    }
    
    /* Global Text Style */
    html, body, [class*="css"], .stMarkdown, p, h1, h2, h3 {
        font-family: 'VT323', monospace !important;
        color: #1a1a1a !important; /* Noir profond pour la lisibilité */
        font-size: 1.2rem;
    }

    /* Écran LCD Vert (Zones d'info) */
    .stAlert, .css-1r6slb0, div[data-testid="stExpander"] {
        background-color: #8bac0f !important;
        border: 2px solid #333 !important;
        color: #0f380f !important;
    }

    /* Boutons A/B (Rouge) */
    div.stButton > button {
        background-color: #8b1d44 !important;
        color: #ffffff !important;
        border-radius: 5px;
        border: 2px solid #333;
        font-size: 1.5rem !important;
        width: 100%;
    }

    /* Inputs */
    .stTextInput>div>div>input {
        background-color: #cadc9f !important;
        color: #0f380f !important;
        border: 2px solid #333 !important;
    }
    
    /* Metrics (Prix) */
    div[data-testid="stMetricValue"] {
        color: #0f380f !important;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

DB_FILE = "ma_collection.csv"

# --- FONCTIONS TECHNIQUES ---

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
    
    if st.button("🔴 CAMERA"):
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
            st.warning("RIEN TROUVÉ")

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
