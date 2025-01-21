class Question:
    def __init__(self,chapitre,id,question, options, correct_answers):
        self.chapitre = chapitre
        self.id = id
        self.question = question
        self.options = options
        self.correct_answers = correct_answers
    
    def to_dict(self):
        return {
            "chapitre": self.chapitre,
            "id": self.id,
            "question": self.question,
            "options": self.options,
            "correct_answers": self.correct_answers
        }