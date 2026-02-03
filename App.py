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

# --- CONFIGURATION & STYLE GAMEBOY ---
st.set_page_config(page_title="Argame Retro", page_icon="🎮", layout="centered")

# Injection CSS pour le look GameBoy
st.markdown("""
    <style>
    /* Fond de la coque GameBoy */
    .main {
        background-color: #9ca0a8; 
    }
    /* Style de l'écran (vert LCD) */
    .stApp {
        background-color: #9ca0a8;
    }
    div.stButton > button {
        background-color: #8b1d44; /* Rouge boutons A/B */
        color: white;
        border-radius: 20px;
        border: 2px solid #555;
        font-weight: bold;
        box-shadow: 2px 2px 0px #333;
    }
    div.stButton > button:hover {
        background-color: #a02050;
        color: white;
    }
    /* Style des zones de texte */
    .stTextInput>div>div>input {
        background-color: #8bac0f; /* Vert écran LCD */
        color: #0f380f;
        font-family: 'Courier New', Courier, monospace;
        border: 2px solid #333;
    }
    /* Cartes de collection */
    .css-1r6slb0 {
        background-color: #8bac0f;
        border: 3px solid #333;
        padding: 10px;
    }
    h1, h2, h3 {
        color: #333;
        text-transform: uppercase;
        font-family: 'Courier New', Courier, monospace;
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
            # Correction : on vérifie que toutes les colonnes existent
            if all(c in df.columns for c in cols):
                return df
            else:
                # Si colonnes manquantes, on reset proprement
                return pd.DataFrame(columns=cols)
        except:
            return pd.DataFrame(columns=cols)
    return pd.DataFrame(columns=cols)

# --- INTERFACE ---
st.sidebar.markdown("### 🕹️ CONTROLS")
menu = st.sidebar.radio("SELECT MODE", ["🔍 SCANNER", "📦 COLLECTION"])

if menu == "🔍 SCANNER":
    st.title("📟 Argame Scanner")
    
    manual_query = st.text_input("INSERT GAME NAME OR EAN")
    
    if st.button("🔴 START CAMERA"):
        img_file = st.camera_input("POINT AT BARCODE OR LABEL")
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
            st.markdown(f"**FOUND:** {res['nom']}")
            col1, col2 = st.columns(2)
            col1.metric("LOOSE", f"{res['loose']} €")
            col2.metric("CIB", f"{res['cib']} €")
            
            if st.button("➕ SAVE TO COLLECTION"):
                db = load_db()
                new_row = {"Jeu": res['nom'], "Prix Loose (€)": res['loose'], "Prix CIB (€)": res['cib'], "Date Ajout": datetime.now().strftime("%d/%m/%Y")}
                db = pd.concat([db, pd.DataFrame([new_row])], ignore_index=True)
                db.to_csv(DB_FILE, index=False)
                st.success("SAVED!")
        else:
            st.error("NOT FOUND")

else:
    st.title("📦 MY GAMES")
    db = load_db()
    
    if not db.empty:
        total = db["Prix Loose (€)"].sum()
        st.subheader(f"TOTAL VALUE: {round(total, 2)} €")
        
        if st.button("🔄 UPDATE ALL PRICES"):
            with st.spinner("UPDATING..."):
                for i, row in db.iterrows():
                    upd = get_price(row['Jeu'])
                    if upd:
                        db.at[i, "Prix Loose (€)"] = upd['loose']
                        db.at[i, "Prix CIB (€)"] = upd['cib']
                db.to_csv(DB_FILE, index=False)
                st.rerun()

        st.markdown("---")
        for index, row in db.iterrows():
            with st.expander(f"🎮 {row['Jeu']}"):
                st.write(f"Loose: {row['Prix Loose (€)']} € | CIB: {row['Prix CIB (€)']} €")
                if st.button(f"🗑️ DELETE", key=f"del_{index}"):
                    db = db.drop(index)
                    db.to_csv(DB_FILE, index=False)
                    st.rerun()
    else:
        st.info("EMPTY COLLECTION")
