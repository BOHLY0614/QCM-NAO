import re

def normaliser_contenu(contenu):
    """Normalise le contenu pour la comparaison (minuscules, suppression espaces/ponctuation)"""
    contenu = contenu.lower()
    contenu = re.sub(r'[^\w\s]', '', contenu)  # Supprime la ponctuation
    contenu = re.sub(r'\s+', ' ', contenu)      # Réduit les espaces multiples
    return contenu.strip()

def traiter_fichier(input_file, output_file):
    """Lit le fichier, détecte les doublons et écrit un fichier sans répétitions"""
    blocs = []
    current_bloc = []
    duplicates = []
    seen_content = {}
    
    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():  # Ignore les lignes vides
                current_bloc.append(line)
                if line.startswith('REP:'):
                    # Extraire le contenu sans numéro/formatage
                    full_content = ''.join(current_bloc[1:-1])  # Ignore ligne de numéro et REP
                    normalized = normaliser_contenu(full_content)
                    
                    # Vérifier les doublons
                    if normalized in seen_content:
                        orig_num = seen_content[normalized]
                        duplicates.append((current_bloc[0].split('.')[0], orig_num))
                    else:
                        num_question = current_bloc[0].split('.')[0]
                        seen_content[normalized] = num_question
                        blocs.append(current_bloc)
                    
                    current_bloc = []
    
    # Écrire le fichier sans doublons
    with open(output_file, 'w', encoding='utf-8') as f_out:
        for bloc in blocs:
            for line in bloc:
                f_out.write(line)
            f_out.write('\n')  # Séparateur entre les blocs
    
    return duplicates

# Utilisation
input_filename = 'QCM NAO\Raw TXT\Chir gen 1-2 & Tara.txt'
output_filename = 'questions_sans_doublons.txt'

doublons = traiter_fichier(input_filename, output_filename)

if doublons:
    print("Doublons détectés :")
    for dup in doublons:
        print(f"- Question {dup[0]} est un doublon de la question {dup[1]}")
else:
    print("Aucun doublon détecté")

print(f"\nFichier nettoyé créé : {output_filename}")