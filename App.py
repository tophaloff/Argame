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
st.set_page_config(page_title="Argame Pro", page_icon="🎮", layout="wide")

DB_FILE = "ma_collection.csv"

# --- FONCTIONS TECHNIQUES ---

def get_price(query):
    """Cherche le prix sur PriceCharting et convertit en €"""
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
            # Nettoyage et conversion ($ -> € / 1.08)
            val_loose = float(p_loose.replace('$','').replace(',','')) / 1.08
            val_cib = float(p_cib.replace('$','').replace(',','')) / 1.08
            return {"nom": name, "loose": round(val_loose, 2), "cib": round(val_cib, 2)}
    except: return None
    return None

def load_db():
    if os.path.exists(DB_FILE): return pd.read_csv(DB_FILE)
    return pd.DataFrame(columns=["Jeu", "Prix Loose (€)", "Prix CIB (€)", "Date Ajout"])

# --- INTERFACE ---
st.sidebar.title("🎮 Argame")
menu = st.sidebar.radio("Navigation", ["🔍 Scanner & Rechercher", "📦 Ma Collection"])

if menu == "🔍 Scanner & Rechercher":
    st.title("Scanner un jeu")
    
    # Recherche Manuelle
    manual_query = st.text_input("Recherche manuelle (nom ou code-barres)")
    
    # Scanner
    if st.button("📸 Ouvrir l'appareil photo"):
        img_file = st.camera_input("Scanner le code-barre ou l'étiquette")
        if img_file:
            file_bytes = np.asarray(bytearray(img_file.read()), dtype=np.uint8)
            img = cv2.imdecode(file_bytes, 1)
            
            # 1. Test Code-barre
            barcodes = decode(img)
            query = barcodes[0].data.decode('utf-8') if barcodes else ""
            
            # 2. Test OCR si pas de code-barre
            if not query:
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                query = pytesseract.image_to_string(gray).strip()
            
            if len(query) > 2: manual_query = query

    if manual_query:
        with st.spinner("Recherche de la cote..."):
            res = get_price(manual_query)
            if res:
                st.success(f"Trouvé : {res['nom']}")
                c1, c2 = st.columns(2)
                c1.metric("Loose", f"{res['loose']} €")
                c2.metric("Complet (CIB)", f"{res['cib']} €")
                
                # Ajout à la collection
                if st.button(f"➕ Ajouter {res['nom']} à ma collection"):
                    db = load_db()
                    new_row = {"Jeu": res['nom'], "Prix Loose (€)": res['loose'], "Prix CIB (€)": res['cib'], "Date Ajout": datetime.now().strftime("%d/%m/%Y")}
                    db = pd.concat([db, pd.DataFrame([new_row])], ignore_index=True)
                    db.to_csv(DB_FILE, index=False)
                    st.balloons()
            else:
                st.error("Jeu non trouvé. Essayez d'être plus précis.")

else: # --- PAGE COLLECTION ---
    st.title("📦 Ma Collection")
    db = load_db()
    
    if not db.empty:
        # Stats rapides
        total_loose = db["Prix Loose (€)"].sum()
        st.subheader(f"Valeur totale estimée (Loose) : {round(total_loose, 2)} €")
        
        # Actions
        col_actu, col_del = st.columns(2)
        
        if col_actu.button("🔄 Actualiser tous les prix"):
            new_prices_loose = []
            new_prices_cib = []
            bar = st.progress(0)
            for i, row in db.iterrows():
                upd = get_price(row['Jeu'])
                new_prices_loose.append(upd['loose'] if upd else row['Prix Loose (€)'])
                new_prices_cib.append(upd['cib'] if upd else row['Prix CIB (€)'])
                bar.progress((i + 1) / len(db))
            db["Prix Loose (€)"] = new_prices_loose
            db["Prix CIB (€)"] = new_prices_cib
            db.to_csv(DB_FILE, index=False)
            st.rerun()

        # Affichage avec option de suppression
        for index, row in db.iterrows():
            with st.expander(f"{row['Jeu']} - {row['Prix Loose (€)']} €"):
                st.write(f"Ajouté le : {row['Date Ajout']}")
                if st.button(f"🗑️ Supprimer", key=f"del_{index}"):
                    db = db.drop(index)
                    db.to_csv(DB_FILE, index=False)
                    st.rerun()
    else:
        st.info("Votre collection est vide. Commencez par scanner un jeu !")
