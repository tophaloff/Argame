import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
from datetime import datetime

# --- CONFIG ET STYLE ---
st.set_page_config(page_title="Argame Pro", page_icon="🎮")
st.markdown("""
    <style>
    .stApp { background-color: #9ca0a8; }
    * { color: #000 !important; font-family: monospace; }
    .stMetric { background: #8bac0f; padding: 10px; border: 2px solid #333; }
    div.stButton > button { background-color: #8b1d44 !important; color: white !important; }
    </style>
    """, unsafe_allow_html=True)

# --- LE MOTEUR DE RECHERCHE CORRIGÉ ---
def get_price_v2(query):
    query = query.strip()
    # On force la recherche en anglais/US car le site est US
    url = f"https://www.pricecharting.com/search-products?q={query.replace(' ', '+')}&type=videogames"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            return None
            
        soup = BeautifulSoup(response.text, 'html.parser')

        # CAS 1 : On est sur une liste de résultats
        product_table = soup.find('table', id='product_list')
        if product_table:
            first_row = product_table.find('tr', id=lambda x: x and x.startswith('product-'))
            if first_row:
                name = first_row.find('td', class_='title').text.strip()
                p_loose = first_row.find('td', class_='price numeric loose').text.strip()
                p_cib = first_row.find('td', class_='price numeric cib').text.strip()
                return clean_data(name, p_loose, p_cib)

        # CAS 2 : On est direct sur la fiche d'un jeu
        name_box = soup.find('h1', class_='title')
        if name_box:
            name = name_box.text.strip()
            # On cherche les prix dans le tableau récapitulatif
            p_loose = soup.find('td', id='loose_price').text.strip() if soup.find('td', id='loose_price') else "0"
            p_cib = soup.find('td', id='cib_price').text.strip() if soup.find('td', id='cib_price') else "0"
            return clean_data(name, p_loose, p_cib)

    except Exception as e:
        return None
    return None

def clean_data(name, p_loose, p_cib):
    # Nettoyage des symboles $ et conversion
    try:
        l = float(p_loose.replace('$','').replace(',','').strip()) / 1.08
        c = float(p_cib.replace('$','').replace(',','').strip()) / 1.08
        return {"nom": name, "loose": round(l, 2), "cib": round(c, 2)}
    except:
        return None

# --- INTERFACE ---
st.title("📟 ARGAME SEARCH")

recherche = st.text_input("Tape le nom d'un jeu (ex: Mario 64)")

if recherche:
    with st.spinner('Connexion au serveur de prix...'):
        resultat = get_price_v2(recherche)
        
        if resultat:
            st.success(f"Jeu trouvé : {resultat['nom']}")
            col1, col2 = st.columns(2)
            col1.metric("LOOSE (€)", f"{resultat['loose']} €")
            col2.metric("COMPLET (€)", f"{resultat['cib']} €")
            
            if st.button("➕ Enregistrer"):
                st.write("Sauvegardé !") # (Ajoute ici ta logique de CSV)
        else:
            st.error("Désolé, aucun prix trouvé pour ce nom. Essaie d'être plus précis (ex: 'Sonic Genesis' au lieu de 'Sonic')")

st.info("Note : L'application interroge les bases de données internationales. Les noms anglais fonctionnent mieux.")
