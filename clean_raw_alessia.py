import re

def process_file(input_file, cleaned_file, answers_file):
    with open(input_file, 'r', encoding='utf-8') as infile, \
         open(cleaned_file, 'w', encoding='utf-8') as outfile_cleaned, \
         open(answers_file, 'w', encoding='utf-8') as outfile_answers:

        for line in infile:
            if line[:5] == "Rep :":
                answers = ",".join(line.replace("Rep :","").replace(" ","").upper())
                outfile_answers.write(answers[:-2] + "\n")

                line = re.sub(r"Rep :.*", "", line) + "\n"
            outfile_cleaned.write(line)


input_file = r"alessia/data_raw/Sem_partial.txt"
cleaned_file = "Sem_partial.txt"
answers_file = "REP_Sem_partial.txt"

process_file(input_file, cleaned_file, answers_file)

print("Traitement terminé")
