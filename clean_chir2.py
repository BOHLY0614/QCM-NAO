import re

def prefixer_options(fichier):
    # Lire le contenu du fichier
    with open(fichier, 'r') as f:
        lignes = f.readlines()
    
    nouvelles_lignes = []
    i = 0
    n = len(lignes)
    prefixes = ['A. ', 'B. ', 'C. ', 'D. ', 'E. ']
    
    while i < n:
        ligne = lignes[i]
        # Vérifier si la ligne commence par un numéro de question (ex: "1.", "2.", "3*.")
        if re.match(r'^\d+\*?\.', ligne.strip()):
            nouvelles_lignes.append(ligne)
            i += 1
            
            # Traiter les 5 lignes suivantes comme options
            for j, prefixe in enumerate(prefixes):
                if i < n:
                    # Nettoyer et formater l'option
                    option = lignes[i].strip()
                    if option:
                        nouvelles_lignes.append(f"{prefixe}{option}\n")
                    i += 1
        else:
            nouvelles_lignes.append(ligne)
            i += 1
    
    # Réécrire le fichier modifié
    with open(fichier, 'w') as f:
        f.writelines(nouvelles_lignes)

# Exemple d'utilisation
prefixer_options('RAW TXT/Chir_plast_en2.txt')