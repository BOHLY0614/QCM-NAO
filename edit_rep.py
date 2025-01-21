input_file = "reponses.txt"
output_file = "edit.txt"

with open(input_file, "r") as f:
    with open(output_file, "w") as g:
        for line in f:
            # Vérifie si la ligne commence par "Chapitre"
            if line.startswith("Chapitre"):
                continue
            # Supprime les chiffres et les points
            line = line.replace(".", "").replace("1", "").replace("2", "").replace("3", "").replace("4", "").replace("5", "").replace("6", "").replace("7", "").replace("8", "").replace("9", "").replace("0", "")
            # Supprime les espaces
            line = line.replace(" ", "")
            # Ajoute les réponses à un tableau
            reponses = line.split(";")
            # Écrit les réponses dans le fichier de sortie
            for reponse in reponses:
                g.write(reponse + "\n")