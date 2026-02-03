import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
from datetime import datetime

# --- CONFIGURATION ---
st.set_page_config(page_title="Argame Retro", page_icon="🎮", layout="centered")

# --- DESIGN GAMEBOY (Le retour du look que tu aimes) ---
st.markdown("""
    <style>
    .stApp { background-color: #9ca0a8 !important; }
    
    /* Force tout le texte en NOIR et LISIBLE */
    html, body, [class*="css"], .stMarkdown, p, h1, h2, h3, label, span {
        color: #000000 !important;
        font-family: 'Helvetica', sans-serif !important;
        font-weight: bold !important;
    }

    /* Le menu latéral en gris clair */
    [data-testid="stSidebar"] {
        background-color: #bdc3c7 !important;
    }

    /* Écran vert LCD pour les résultats */
    .stAlert, div[data-testid="stExpander"] {
        background-color: #8bac0f !important;
        border: 3px solid #333 !important;
    }

    /* Boutons rouges A/B */
    div.stButton > button {
        background-color: #8b1d44 !important;
        color: white !important;
        border: 2px solid #000 !important;
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

DB_FILE = "ma_collection.csv"

# --- MOTEUR DE RECHERCHE "TOUT TERRAIN" ---
def get_price(query):
    query = query.strip()
    url = f"https://www.pricecharting.com/search-products?q={query.replace(' ', '+')}&type=videogames"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    
    try:
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, 'html.parser')

        # On cherche les prix dans n'importe quel format (liste ou fiche)
        name = ""
        p_loose = "0"
        p_cib = "0"

        # Si c'est une liste
        row = soup.find('tr', id=lambda x: x and x.startswith('product-'))
        if row:
            name = row.find('td', class_='title').text.strip()
            p_loose = row.find('td', class_='price numeric loose').text.strip()
            p_cib = row.find('td', class_='price numeric cib').text.strip()
        else:
            # Si c'est une fiche directe
            title_tag = soup.find('h1', class_='title')
            if title_tag:
                name = title_tag.text.strip()
                # On cherche les prix par ID
                loose_tag = soup.find('td', id='loose_price')
                cib_tag = soup.find('td', id='cib_price')
                p_loose = loose_tag.text.strip() if loose_tag else "0"
                p_cib = cib_tag.text.strip() if cib_tag else "0"

        if name:
            # Nettoyage et conversion $ -> €
            l = float(p_loose.replace('$','').replace(',','').strip()) / 1.08
            c = float(p_cib.replace('$','').replace(',','').strip()) / 1.08
            return {"nom": name, "loose": round(l, 2), "cib": round(c, 2)}
    except:
        return None
    return None

def load_db():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    return pd.DataFrame(columns=["Jeu", "Prix Loose (€)", "Prix CIB (€)", "Date"])

# --- MENU DÉROULANT (SIDEBAR) ---
with st.sidebar:
    st.title("🕹️ MENU")
    page = st.radio("ALLER À :", ["🔍 SCANNER / CHERCHER", "📦 MA COLLECTION"])

# --- LOGIQUE DES PAGES ---
if page == "🔍 SCANNER / CHERCHER":
    st.title("📟 RECHERCHE")
    
    jeu_cherche = st.text_input("NOM DU JEU :", placeholder="Ex: Tetris Gameboy")
    
    if jeu_cherche:
        with st.spinner('Recherche...'):
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
                    st.toast("Jeu ajouté !")
            else:
                st.error("Jeu non trouvé. Essayez un nom plus court (ex: 'Mario 64' au lieu de 'Super Mario 64 version PAL')")

else:
    st.title("📦 MA COLLECTION")
    db = load_db()
    if not db.empty:
        total = db["Prix Loose (€)"].sum()
        st.subheader(f"VALEUR TOTALE : {round(total, 2)} €")
        st.dataframe(db) # Affiche la liste proprement
        if st.button("🗑️ VIDER TOUT"):
            os.remove(DB_FILE)
            st.rerun()
    else:
        st.info("La collection est vide.")
