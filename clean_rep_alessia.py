# Chemin vers votre fichier
file_path = 'alessia/data_raw/droit_c3.txt'

# Lire le contenu du fichier
with open(file_path, 'r', encoding='utf-8') as file:
    lines = file.readlines()

# Traiter chaque ligne
processed_lines = []
for line in lines:
    if line.strip().startswith(('1.', '2.', '3.', '4.', '5.')):
        # Remplacer les numéros par des lettres
        if line.strip().startswith('1.'):
            line = line.replace('1.', 'a.', 1)
        elif line.strip().startswith('2.'):
            line = line.replace('2.', 'b.', 1)
        elif line.strip().startswith('3.'):
            line = line.replace('3.', 'c.', 1)
        elif line.strip().startswith('4.'):
            line = line.replace('4.', 'd.', 1)
        elif line.strip().startswith('5.'):
            line = line.replace('5.', 'e.', 1)
    processed_lines.append(line)

# Écrire les modifications dans le fichier
with open(file_path, 'w', encoding='utf-8') as file:
    file.writelines(processed_lines)
