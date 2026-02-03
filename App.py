def load_db():
    cols = ["Jeu", "Prix Loose (€)", "Prix CIB (€)", "Date Ajout"]
    if os.path.exists(DB_FILE):
        try:
            df = pd.read_csv(DB_FILE)
            # On vérifie si toutes les colonnes sont là
            if all(c in df.columns for c in cols):
                return df
        except:
            pass
    # Si le fichier est vide ou corrompu, on en crée un nouveau
    return pd.DataFrame(columns=cols)
