import streamlit as st
import requests
from bs4 import BeautifulSoup
import cv2
import numpy as np
import pandas as pd
import os
from datetime import datetime
import pytesseract

# --- CONFIG & STYLE ---
st.set_page_config(page_title="Argame Retro Pro", page_icon="🎮")

# Initialisation de la mémoire de session pour éviter que les résultats disparaissent
if 'search_result' not in st.session_state:
    st.session_state.search_result = None

DB_FILE = "ma_collection.csv"
COLUMNS = ["Jeu", "Prix Loose (€)", "Prix CIB (€)", "Date"]

def load_db():
    if os.path.exists(DB_FILE):
        try: return pd.read_csv(DB_FILE)
        except: return pd.DataFrame(columns=COLUMNS)
    return pd.DataFrame(columns=COLUMNS)

def get_price(query):
    if not query or len(query) < 2: return None
    query = query.replace("Playstation 5", "PS5").replace("Playstation 4", "PS4").strip()
    url = f"https://www.pricecharting.com/search-products?q={query.replace(' ', '+')}&type=videogames"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, 'html.parser')
        name_tag = soup.find('h1', class_='title')
        if name_tag:
            name = name_tag.text.strip()
            l_val = soup.find('td', id='loose_price').text.strip() if soup.find('td', id='loose_price') else "0"
            c_val = soup.find('td', id='cib_price').text.strip() if soup.find('td', id='cib_price') else "0"
        else:
            row = soup.find('tr', id=lambda x: x and x.startswith('product-'))
            if row:
                name = row.find('td', class_='title').text.strip()
                l_val = row.find('td', class_='price numeric loose').text.strip()
                c_val = row.find('td', class_='price numeric cib').text.strip()
            else: return None
        clean_p = lambda x: float(x.replace('$','').replace(',','').replace('N/A','0').strip() or 0)
        return {"nom": name, "loose": round(clean_p(l_val)/1.08, 2), "cib": round(clean_p(c_val)/1.08, 2)}
    except: return None

# --- UI ---
st.title("🕹️ ARGAME RETRO PRO")
menu = st.sidebar.radio("MENU", ["🔍 RECHERCHE & SCAN", "📦 MA COLLECTION"])

if menu == "🔍 RECHERCHE & SCAN":
    methode = st.radio("Méthode :", ["⌨️ Saisie Manuelle", "📸 Photo"])
    
    with st.container():
        if methode == "⌨️ Saisie Manuelle":
            with st.form("search_form"):
                jeu_saisi = st.text_input("Nom du jeu :")
                if st.form_submit_button("🔍 CHERCHER"):
                    st.session_state.search_result = get_price(jeu_saisi)
        else:
            img_file = st.file_uploader("Prends une photo", type=['jpg', 'jpeg', 'png'])
            if img_file:
                # Analyse seulement si l'image change
                file_bytes = np.asarray(bytearray(img_file.read()), dtype=np.uint8)
                img = cv2.imdecode(file_bytes, 1)
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                text = pytesseract.image_to_string(gray).strip()
                if text:
                    st.session_state.search_result = get_price(text)

    # Affichage du résultat stocké en mémoire
    res = st.session_state.search_result
    if res:
        st.markdown(f"### 🎯 {res['nom']}")
        c1, c2 = st.columns(2)
        c1.metric("LOOSE", f"{res['loose']} €")
        c2.metric("COMPLET", f"{res['cib']} €")
        
        if st.button("➕ AJOUTER À LA COLLECTION"):
            db = load_db()
            new_row = {"Jeu": res['nom'], "Prix Loose (€)": res['loose'], "Prix CIB (€)": res['cib'], "Date": datetime.now().strftime("%d/%m/%Y")}
            pd.concat([db, pd.DataFrame([new_row])], ignore_index=True).to_csv(DB_FILE, index=False)
            st.success("Ajouté !")
            st.session_state.search_result = None # Reset après ajout

else:
    st.title("📦 MA COLLECTION")
    db = load_db()
    if not db.empty:
        st.metric("VALEUR TOTALE (LOOSE)", f"{round(db['Prix Loose (€)'].sum(), 2)} €")
        st.dataframe(db, use_container_width=True, hide_index=True)
        if st.button("🗑️ TOUT EFFACER"):
            if os.path.exists(DB_FILE): os.remove(DB_FILE)
            st.rerun()
