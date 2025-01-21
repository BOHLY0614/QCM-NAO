import re

def process_file(input_file, cleaned_file, answers_file):
    with open(input_file, 'r', encoding='utf-8') as infile, \
         open(cleaned_file, 'w', encoding='utf-8') as outfile_cleaned, \
         open(answers_file, 'w', encoding='utf-8') as outfile_answers:

        for line in infile:
            # Recherche des lignes contenant "REP:"
            match = re.search(r"REP:\s*([A-Z]+)", line)
            if match:
                # Sauvegarde les réponses sous forme A,B
                answers = ",".join(match.group(1))
                outfile_answers.write(answers + "\n")

                # Supprime "REP:" et ce qui suit dans la ligne
                line = re.sub(r"REP:.*", "", line)
            
            # Écrit la ligne nettoyée dans le fichier des questions
            outfile_cleaned.write(line)

# Noms des fichiers
input_file = "cardio2.txt"
cleaned_file = "yala.txt"
answers_file = "editc2.txt"

# Traitement du fichier
process_file(input_file, cleaned_file, answers_file)

print("Traitement terminé. Les fichiers questions_cleaned.txt et answers.txt ont été créés.")
