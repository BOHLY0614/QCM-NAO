import tkinter as tk
from tkinter import ttk, scrolledtext
import json
import random
import time
import os

nombreq = 20

# Définition des styles globaux
LARGE_FONT = ("Arial", 16)
TITLE_FONT = ("Arial", 24, "bold")
BUTTON_FONT = ("Arial", 14)
RESULT_FONT = ("Arial", 18)

class QCMApp(tk.Tk):
    def __init__(self):
        super().__init__()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        self.geometry(f"{screen_width}x{screen_height}")
        self.title("Quiz QCM")
        self.configure(padx=20, pady=20)
        
        # Configuration pour un redimensionnement adaptatif
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Initialisation du thème
        self.theme_mode = "light"  # 'light' ou 'dark'
        self.themes = {
            "light": {
                "bg": "#ffffff",
                "fg": "#000000",
                "button_bg": "#f0f0f0",
                "button_fg": "#000000",
                "primary": "#1a73e8",
                "text_bg": "#ffffff",
                "correct": "#2ecc71",
                "incorrect": "#e74c3c",
                "scrollbar": "#c0c0c0",
                "canvas": "#ffffff",
                "entry": "#ffffff",
                "toolbar": "#e0e0e0",
                "hover": "#1e82ec",     # Couleur de survol plus visible
                "checkbox": "#1a73e8",   # Couleur des cases à cocher
                "selected_bg": "#f0f8ff" # Fond pour options sélectionnées
            },
            "dark": {
                "bg": "#1e1e1e",
                "fg": "#ffffff",
                "button_bg": "#3d3d3d",
                "button_fg": "#ffffff",
                "primary": "#4a9cff",
                "text_bg": "#2d2d2d",
                "correct": "#27ae60",
                "incorrect": "#c0392b",
                "scrollbar": "#606060",
                "canvas": "#1e1e1e",     # Même couleur que le fond
                "entry": "#333333",
                "toolbar": "#333333",
                "hover": "#1a73e8",      # Couleur de survol
                "checkbox": "#6ab0ff",   # Couleur des cases à cocher
                "selected_bg": "#2a3a4a" # Fond pour options sélectionnées
            }
        }
        
        # Créer une barre d'outils pour le bouton de thème
        self.toolbar_frame = ttk.Frame(self)
        self.toolbar_frame.pack(fill='x', padx=10, pady=5)
        
        # Bouton de bascule de thème en haut à droite
        self.theme_button = tk.Button(
            self.toolbar_frame,
            text="☀️" if self.theme_mode == "light" else "🌙",
            command=self.toggle_theme,
            font=("Arial", 14),
            bd=0,
            relief="flat",
            padx=10,
            pady=5
        )
        self.theme_button.pack(side='right', padx=5, pady=5)
        
        self.apply_theme()
        
        # Charger les données
        self.chapter_files = ["QCM NAO/JSON/Chirurgie Cardio.json", "QCM NAO/JSON/Chirurgie Gen.json"] 
        self.chapters = self.load_chapters()
        self.load_question_stats()
        self.create_main_menu()
        
        # Liaison pour le redimensionnement
        self.bind("<Configure>", self.on_window_resize)

    def apply_theme(self):
        """Applique le thème actuel à tous les widgets"""
        theme = self.themes[self.theme_mode]
        
        # Configurer la fenêtre principale
        self.configure(background=theme['bg'])
        
        # Configurer les styles ttk
        self.style = ttk.Style()
        self.style.theme_use('default')  # Important pour éviter les conflits
        
        # Configuration des styles
        self.style.configure(
            "TFrame", 
            background=theme['bg']
        )
        self.style.configure(
            "TLabel", 
            background=theme['bg'], 
            foreground=theme['fg']
        )
        self.style.configure(
            "TButton", 
            background=theme['button_bg'],
            foreground=theme['button_fg'],
            borderwidth=1,
            relief="solid",
            font=BUTTON_FONT
        )
        self.style.map(
            "TButton",
            background=[('active', theme['primary'])]
        )
        self.style.configure(
            "Large.TButton", 
            font=BUTTON_FONT, 
            padding=10
        )
        
        # Style pour les cases à cocher - plus visible
        self.style.configure(
            "TCheckbutton", 
            background=theme['bg'], 
            foreground=theme['fg'],
            indicatorbackground=theme['bg'],
            indicatorforeground=theme['checkbox'],
            selectcolor=theme['selected_bg']
        )
        self.style.configure(
            "Large.TCheckbutton", 
            font=LARGE_FONT
        )
        self.style.configure(
            "TScrollbar", 
            background=theme['scrollbar'],
            troughcolor=theme['bg']
        )
        
        # Style pour le survol
        self.style.configure(
            "Hover.TFrame", 
            background=theme['hover']
        )
        
        # Mettre à jour la barre d'outils
        self.theme_button.configure(
            bg=theme['toolbar'],
            fg=theme['fg'],
            activebackground=theme['toolbar'],
            activeforeground=theme['fg']
        )
        
        # Appliquer à tous les widgets existants
        self.update_all_widgets()

    def update_all_widgets(self):
        """Met à jour tous les widgets avec le thème actuel"""
        theme = self.themes[self.theme_mode]
        for widget in self.winfo_children():
            self.update_widget_colors(widget, theme)

    def update_widget_colors(self, widget, theme):
        """Met à jour récursivement les couleurs d'un widget et de ses enfants"""
        widget_type = widget.winfo_class()
        
        # Appliquer les couleurs en fonction du type de widget
        if widget_type == 'Frame':  # tk.Frame
            widget.configure(background=theme['bg'])
        elif widget_type == 'Label':  # tk.Label
            widget.configure(background=theme['bg'], foreground=theme['fg'])
        elif widget_type == 'Button':  # tk.Button
            widget.configure(
                bg=theme['button_bg'], 
                fg=theme['button_fg'],
                activebackground=theme['primary'],
                activeforeground=theme['button_fg']
            )
        elif widget_type == 'Checkbutton':  # tk.Checkbutton
            widget.configure(
                bg=theme['bg'], 
                fg=theme['fg'],
                activebackground=theme['bg'],
                activeforeground=theme['fg'],
                selectcolor=theme['selected_bg']  # Fond de la case
            )
        elif widget_type == 'Canvas':  # tk.Canvas
            widget.configure(bg=theme['canvas'], highlightthickness=0)
        elif widget_type == 'Scrollbar':  # tk.Scrollbar
            widget.configure(
                bg=theme['scrollbar'],
                troughcolor=theme['bg']
            )
        
        # Traiter les enfants récursivement
        for child in widget.winfo_children():
            self.update_widget_colors(child, theme)

    def toggle_theme(self):
        """Bascule entre les modes clair et sombre"""
        self.theme_mode = "dark" if self.theme_mode == "light" else "light"
        self.apply_theme()
        self.theme_button.configure(text="☀️" if self.theme_mode == "light" else "🌙")

    def on_window_resize(self, event):
        """Met à jour les éléments lors du redimensionnement de la fenêtre"""
        # Mettre à jour les wraplengths
        if hasattr(self, 'question_label'):
            self.update_wraplengths()
        
        # Mettre à jour la position des fenêtres modales
        if hasattr(self, 'result_window') and self.result_window.winfo_exists():
            self.center_window(self.result_window)

    def update_wraplengths(self):
        """Met à jour les wraplengths pour l'adaptation responsive"""
        if hasattr(self, 'question_label'):
            new_width = self.winfo_width() - 100
            self.question_label.configure(wraplength=new_width)
            
            # Mettre à jour les wraplengths des options
            for child in self.scrollable_frame.winfo_children():
                if isinstance(child, ttk.Frame):
                    for subchild in child.winfo_children():
                        if isinstance(subchild, ttk.Label):
                            subchild.configure(wraplength=new_width - 50)

    def center_window(self, window):
        """Centre une fenêtre secondaire par rapport à la fenêtre principale"""
        window.update_idletasks()
        main_x = self.winfo_x()
        main_y = self.winfo_y()
        main_width = self.winfo_width()
        main_height = self.winfo_height()
        
        window_width = window.winfo_width()
        window_height = window.winfo_height()
        
        x = main_x + (main_width // 2) - (window_width // 2)
        y = main_y + (main_height // 2) - (window_height // 2)
        
        window.geometry(f"+{x}+{y}")

    def load_chapters(self):
        chapters = {}
        for file in self.chapter_files:
            with open(file, "r", encoding="utf-8") as f:
                chapter_data = json.load(f)
                chapters[file] = chapter_data
        return chapters

    def create_main_menu(self):
        self.main_menu_frame = ttk.Frame(self)
        self.main_menu_frame.pack(expand=True, fill='both')
        
        # Configuration pour un redimensionnement adaptatif
        self.main_menu_frame.grid_columnconfigure(0, weight=1)
        self.main_menu_frame.grid_rowconfigure(0, weight=1)
        self.main_menu_frame.grid_rowconfigure(1, weight=1)

        title = ttk.Label(self.main_menu_frame, text="Choisissez un chapitre", font=TITLE_FONT)
        title.pack(pady=40)

        button_frame = ttk.Frame(self.main_menu_frame)
        button_frame.pack(pady=20)

        for i, chapter_name in enumerate(self.chapter_files):
            chapter_button = ttk.Button(
                button_frame, 
                text=chapter_name[13:-5],
                command=lambda i=i: self.start_quiz(i),
                style="Large.TButton"
            )
            chapter_button.pack(pady=10, fill='x')

        mix_all_button = ttk.Button(
            button_frame, 
            text="Mélange de tous les chapitres",
            command=self.mix_all_chapters,
            style="Large.TButton"
        )
        mix_all_button.pack(pady=10, fill='x')

    def start_quiz(self, chapter):   
        self.main_menu_frame.pack_forget()
        self.quiz_frame = ttk.Frame(self)
        self.quiz_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Configuration pour un redimensionnement adaptatif
        self.quiz_frame.grid_columnconfigure(0, weight=1)
        self.quiz_frame.grid_rowconfigure(0, weight=1)

        self.current_question = 0
        if chapter == -1:
            self.current_chapter = self.mixed_chapter
        else:
            self.current_chapter = self.chapters[self.chapter_files[chapter]]
            random.shuffle(self.current_chapter)
            self.current_chapter = self.current_chapter[:min(nombreq, len(self.current_chapter))]
        self.total_questions = len(self.current_chapter)
        self.score = 0
        self.start_time = time.time()

        self.show_question()

    def show_question(self):
        self.clear_frame(self.quiz_frame)

        # Frame principale avec gestion de redimensionnement
        main_container = ttk.Frame(self.quiz_frame)
        main_container.pack(fill='both', expand=True)
        
        # Configuration pour un redimensionnement adaptatif
        main_container.grid_columnconfigure(0, weight=1)
        main_container.grid_rowconfigure(0, weight=1)  # Pour le contenu
        main_container.grid_rowconfigure(1, weight=0)  # Pour le bouton
        main_container.grid_rowconfigure(2, weight=0)  # Pour la barre d'info

        # Canvas avec barre de défilement
        theme = self.themes[self.theme_mode]
        canvas = tk.Canvas(main_container, bg=theme['canvas'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_container, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        # Mise à jour dynamique de la largeur
        def on_canvas_configure(event):
            canvas.itemconfig("all", width=event.width)
            self.scrollable_frame.configure(width=event.width)
        
        canvas.bind("<Configure>", on_canvas_configure)

        question_data = self.current_chapter[self.current_question]
        
        # Question avec label adaptatif
        self.question_label = ttk.Label(
            self.scrollable_frame, 
            text=question_data["question"],
            font=LARGE_FONT,
            wraplength=self.winfo_width() - 100,  # Largeur adaptative
            justify="left",
            anchor="w"
        )
        self.question_label.pack(fill='x', padx=20, pady=20, anchor='w')

        # Options avec labels adaptatifs
        self.selected_answers = [tk.BooleanVar() for _ in question_data["options"]]
        
        # Liste pour stocker les cadres d'options
        self.option_frames = []
        
        for i, option in enumerate(question_data["options"]):
            option_frame = ttk.Frame(self.scrollable_frame)
            option_frame.pack(fill='x', padx=20, pady=5, anchor='w')
            self.option_frames.append(option_frame)
            
            # Case à cocher avec style personnalisé
            answer_checkbutton = ttk.Checkbutton(
                option_frame, 
                variable=self.selected_answers[i],
                style="Large.TCheckbutton"
            )
            answer_checkbutton.pack(side='left', anchor='w', padx=(0, 10))
            
            # Texte de l'option avec adaptation dynamique
            option_label = ttk.Label(
                option_frame, 
                text=option,
                font=LARGE_FONT,
                wraplength=self.winfo_width() - 150,  # Largeur adaptative
                justify="left",
                anchor="w"
            )
            option_label.pack(side='left', fill='x', expand=True, anchor='w')
            
            # Lier le label à la case à cocher
            option_label.bind("<Button-1>", lambda e, cb=answer_checkbutton: cb.invoke())
            
            # Ajouter des événements de survol pour l'option
            for w in (option_frame, answer_checkbutton, option_label):
                w.bind("<Enter>", lambda e, idx=i: self.on_option_hover(idx))
                w.bind("<Leave>", lambda e, idx=i: self.on_option_leave(idx))

        # Bouton Suivant
        button_frame = ttk.Frame(main_container)
        button_frame.grid(row=1, column=0, columnspan=2, pady=20, sticky="ew")
        
        next_button = ttk.Button(
            button_frame, 
            text="Suivant", 
            command=self.check_answer,
            style="Large.TButton"
        )
        next_button.pack(pady=20)

        # Barre d'information en bas
        bottom_frame = ttk.Frame(main_container)
        bottom_frame.grid(row=2, column=0, columnspan=2, sticky="ew", padx=20, pady=10)

        elapsed_time = int(time.time() - self.start_time)
        hours, remainder = divmod(elapsed_time, 3600)
        minutes, seconds = divmod(remainder, 60)
        time_label = ttk.Label(
            bottom_frame, 
            text=f"Temps écoulé : {hours}h {minutes}m {seconds}s",
            font=LARGE_FONT
        )
        time_label.pack(side='left')

        remaining_questions = len(self.current_chapter) - self.current_question
        remaining_label = ttk.Label(
            bottom_frame, 
            text=f"Questions restantes : {remaining_questions}",
            font=LARGE_FONT
        )
        remaining_label.pack(side='right')

        # Mise à jour dynamique du wraplength
        self.update_wraplengths()

    def on_option_hover(self, option_index):
        """Effet visuel lorsque la souris survole une option"""
        theme = self.themes[self.theme_mode]
        self.option_frames[option_index].configure(style="Hover.TFrame")

    def on_option_leave(self, option_index):
        """Effet visuel lorsque la souris quitte une option"""
        # Retour au style normal
        self.option_frames[option_index].configure(style="TFrame")

    def check_answer(self):
        correct_answers = self.current_chapter[self.current_question]["correct_answers"]
        user_answers = [chr(i + 65) for i, selected in enumerate(self.selected_answers) if selected.get()]

        question_id = self.current_chapter[self.current_question]["id"]
        question_stats = self.question_stats.get(question_id, {"correct": 0, "incorrect": 0})

        is_correct = sorted(correct_answers) == sorted(user_answers)
        
        if is_correct:
            question_stats["correct"] += 1
            self.score += 1
            result_text = "Bonne réponse !"
        else:
            question_stats["incorrect"] += 1
            result_text = f"Mauvaise réponse...\nLa bonne réponse est : {', '.join(correct_answers)}"

        self.question_stats[question_id] = question_stats
        self.show_result(result_text, is_correct)

    def show_result(self, result_text, is_correct):
        self.result_window = tk.Toplevel(self)
        self.result_window.title("Résultat")
        self.result_window.geometry("800x400")
        self.result_window.resizable(True, True)
        
        # Ajouter la barre d'outils pour le bouton de thème
        toolbar_frame = ttk.Frame(self.result_window)
        toolbar_frame.pack(fill='x', padx=10, pady=5)
        
        theme_button = tk.Button(
            toolbar_frame,
            text="☀️" if self.theme_mode == "light" else "🌙",
            command=self.toggle_theme,
            font=("Arial", 14),
            bd=0,
            relief="flat",
            padx=10,
            pady=5
        )
        theme_button.pack(side='right', padx=5, pady=5)
        
        # Appliquer le thème
        theme = self.themes[self.theme_mode]
        self.result_window.configure(background=theme['bg'])
        theme_button.configure(
            bg=theme['toolbar'],
            fg=theme['fg'],
            activebackground=theme['toolbar'],
            activeforeground=theme['fg']
        )
        
        center_frame = ttk.Frame(self.result_window)
        center_frame.pack(expand=True, fill='both', padx=50, pady=50)

        # Zone de texte adaptative pour le résultat
        result_frame = ttk.Frame(center_frame)
        result_frame.pack(fill='both', expand=True)
        
        # Choisir la couleur en fonction de la réponse
        result_color = theme['correct'] if is_correct else theme['incorrect']
        
        self.result_label = ttk.Label(
            result_frame, 
            text=result_text,
            font=RESULT_FONT,
            wraplength=700,
            justify="center",
            foreground=result_color
        )
        self.result_label.pack(fill='both', expand=True, pady=20)
        
        # Mise à jour dynamique du wraplength
        def update_result_wraplength(event):
            self.result_label.configure(wraplength=event.width - 100)
        
        self.result_window.bind("<Configure>", update_result_wraplength)

        continue_button = ttk.Button(
            center_frame, 
            text="Continuer", 
            command=self.close_result_window,
            style="Large.TButton"
        )
        continue_button.pack(pady=20)
        
        # Centrer la fenêtre
        self.center_window(self.result_window)
        
        self.result_window.transient(self)
        self.result_window.grab_set()
        self.wait_window(self.result_window)

    def close_result_window(self):
        """Ferme la fenêtre de résultat et passe à la question suivante"""
        self.result_window.destroy()
        
        self.current_question += 1
        if self.current_question < len(self.current_chapter):
            self.show_question()
        else:
            self.show_final_score()

    def mix_all_chapters(self):
        all_chapters = [self.chapters[file] for file in self.chapter_files]
        mixed_questions = [question for chapter in all_chapters for question in chapter]
        random.shuffle(mixed_questions)
        self.mixed_chapter = random.sample(mixed_questions, min(70, len(mixed_questions)))
        self.start_quiz(-1)

    def show_final_score(self):
        self.clear_frame(self.quiz_frame)

        center_frame = ttk.Frame(self.quiz_frame)
        center_frame.pack(expand=True, fill='both')
        
        # Configuration pour un redimensionnement adaptatif
        center_frame.grid_columnconfigure(0, weight=1)
        center_frame.grid_rowconfigure(0, weight=1)
        center_frame.grid_rowconfigure(1, weight=1)

        score_label = ttk.Label(
            center_frame, 
            text=f"Score final : {self.score}/{len(self.current_chapter)}", 
            font=TITLE_FONT
        )
        score_label.pack(pady=40)

        button_frame = ttk.Frame(center_frame)
        button_frame.pack(pady=20)

        menu_button = ttk.Button(
            button_frame, 
            text="Retour au menu principal", 
            command=self.return_to_main_menu,
            style="Large.TButton"
        )
        menu_button.pack(pady=10, fill='x')

        quit_button = ttk.Button(
            button_frame, 
            text="Quitter", 
            command=self.quit,
            style="Large.TButton"
        )
        quit_button.pack(pady=10, fill='x')
        
        self.save_question_stats()

    def return_to_main_menu(self):
        self.clear_frame(self.quiz_frame)
        self.quiz_frame.pack_forget()
        self.create_main_menu()

    def clear_frame(self, frame):
        for widget in frame.winfo_children():
            widget.destroy()

    def load_question_stats(self):
        if os.path.exists("question_stats.json"):
            with open("question_stats.json", "r") as f:
                self.question_stats = json.load(f)
        else:
            self.question_stats = {}

    def save_question_stats(self):
        with open("question_stats.json", "w") as f:
            json.dump(self.question_stats, f)

if __name__ == "__main__":
    app = QCMApp()
    app.mainloop()