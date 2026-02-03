import streamlit as st
import requests
from bs4 import BeautifulSoup
import cv2
import numpy as np
from pyzbar.pyzbar import decode
import pytesseract

# --- FONCTION DE PRÉ-TRAITEMENT IMAGE ---
def preprocess_for_ocr(opencv_image):
    # 1. Conversion en niveaux de gris
    gray = cv2.cvtColor(opencv_image, cv2.COLOR_BGR2GRAY)
    # 2. Augmentation du contraste et réduction du bruit
    gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
    return gray

def get_price(query):
    if not query or len(query) < 3: return None
    search_url = f"https://www.pricecharting.com/search-products?q={query.replace(' ', '+')}&type=videogames"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        res = requests.get(search_url, headers=headers)
        soup = BeautifulSoup(res.text, 'html.parser')
        row = soup.find('tr', id=lambda x: x and x.startswith('product-'))
        if row:
            name = row.find('td', class_='title').text.strip()
            p_loose = row.find('td', class_='price numeric loose').text.strip()
            p_cib = row.find('td', class_='price numeric cib').text.strip()
            l_euro = f"{float(p_loose.replace('$','').replace(',',''))/1.08:.2f} €"
            c_euro = f"{float(p_cib.replace('$','').replace(',',''))/1.08:.2f} €"
            return name, l_euro, c_euro
    except: return None
    return None

st.title("🎮 Argame")

# --- INTERFACE SCAN ---
if "show_cam" not in st.session_state:
    st.session_state.show_cam = False

if st.button("📸 Scanner un jeu (Code-barre ou Étiquette)"):
    st.session_state.show_cam = True

if st.session_state.show_cam:
    img_file = st.camera_input("Prenez une photo bien nette")
    
    if img_file:
        file_bytes = np.asarray(bytearray(img_file.read()), dtype=np.uint8)
        img = cv2.imdecode(file_bytes, 1)
        
        # Tentative 1 : Code-barre
        barcodes = decode(img)
        if barcodes:
            code = barcodes[0].data.decode('utf-8')
            st.success(f"Code-barre détecté : {code}")
            res = get_price(code)
            if res: st.metric(res[0], f"{res[1]} (Loose)")
        
        # Tentative 2 : OCR Optimisé
        else:
            processed_img = preprocess_for_ocr(img)
            # On montre l'image traitée pour aider l'utilisateur à voir ce que l'IA voit
            with st.expander("Voir ce que l'IA analyse"):
                st.image(processed_img, caption="Image filtrée")
            
            text = pytesseract.image_to_string(processed_img, config='--psm 3')
            clean_text = text.strip().replace('\n', ' ')
            
            if len(clean_text) > 2:
                st.info(f"Texte lu : {clean_text}")
                res = get_price(clean_text)
                if res:
                    st.success(f"Jeu identifié : {res[0]}")
                    st.write(f"Prix estimé : **{res[1]}**")
            else:
                st.error("Lecture impossible. Rapprochez-vous du titre du jeu.")
