import streamlit as st
import pandas as pd
import os
from datetime import datetime
# (Garde tes imports précédents : requests, bs4, cv2, etc.)

# --- GESTION DE LA BASE DE DONNÉES ---
DB_FILE = "ma_collection.csv"

def load_collection():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    return pd.DataFrame(columns=["Jeu", "Prix_Initial", "Prix_Actuel", "Date"])

def save_to_collection(name, price):
    df = load_collection()
    new_entry = pd.DataFrame({
        "Jeu": [name], 
        "Prix_Initial": [price], 
        "Prix_Actuel": [price], 
        "Date": [datetime.now().strftime("%d/%m/%Y")]
    })
    df = pd.concat([df, new_entry], ignore_index=True)
    df.to_csv(DB_FILE, index=False)
    st.success(f"✅ {name} ajouté à ta collection !")

# --- INTERFACE ---
st.sidebar.title("Menu Argame")
page = st.sidebar.radio("Aller vers", ["Scanner un jeu", "Ma Collection"])

if page == "Scanner un jeu":
    st.title("📸 Nouveau Scan")
    # (Remets ici ton code de scan/OCR actuel)
    
    # Simulation d'un résultat trouvé :
    nom_trouve = "Zelda Ocarina of Time" # Exemple
    prix_trouve = "45.00 €"
    
    st.write(f"Jeu : {nom_trouve} | Prix : {prix_trouve}")
    if st.button("➕ Ajouter à ma collection"):
        save_to_collection(nom_trouve, prix_trouve)

elif page == "Ma Collection":
    st.title("📦 Ma Collection")
    df = load_collection()
    
    if not df.empty:
        st.table(df)
        if st.button("🔄 Actualiser tous les prix"):
            with st.spinner("Mise à jour des cotes en cours..."):
                # Ici on lancera la boucle de recherche pour chaque ligne
                st.info("Cette fonction va scanner PriceCharting pour chaque jeu...")
    else:
        st.write("Ta collection est vide pour le moment.")
