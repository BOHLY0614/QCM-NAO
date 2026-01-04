import tkinter as tk
from tkinter import ttk, scrolledtext
import json
import random
import time
import os
import ctypes

# Définition des styles globaux
LARGE_FONT = ("Arial", 16)
TITLE_FONT = ("Arial", 24, "bold")
BUTTON_FONT = ("Arial", 14)
RESULT_FONT = ("Arial", 18)

class QCMApp(tk.Tk):
    def __init__(self):
        super().__init__()

        try:
            # On définit un ID unique pour l'app (utilisez ce que vous voulez comme texte)
            myappid = 'QCM NAO' 
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        except Exception:
            pass 

        self.state('zoomed')
        self.title("Quiz QCM")

        try:
            self.iconbitmap("Assets/GF.ico")
        except Exception as e:
            print("Icône non trouvée:", e)
 
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
                "hover": "#306eac",
                "checkbox": "#1a73e8",
                "selected_bg": "#f0f8ff",
                "correct_bg": "#2e7d32",    # Fond pour réponses correctes
                "correct_fg": "#2e7d32",    # Texte pour réponses correctes
                "incorrect_bg": "#c62828",  # Fond pour réponses incorrectes
                "incorrect_fg": "#c62828"   # Texte pour réponses incorrectes
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
                "canvas": "#1e1e1e",
                "entry": "#333333",
                "toolbar": "#333333",
                "hover": "#306eac",
                "checkbox": "#6ab0ff",
                "selected_bg": "#2a3a4a",
                "correct_bg": "#1b5e20",   # Fond pour réponses correctes
                "correct_fg": "#a5d6a7",   # Texte pour réponses correctes
                "incorrect_bg": "#7f0000",  # Fond pour réponses incorrectes
                "incorrect_fg": "#ff8a80"   # Texte pour réponses incorrectes
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
        
        # Charger les données dynamiquement
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        json_dir = os.path.join(self.base_dir, "JSON")
        
        self.chapter_files = []
        if os.path.exists(json_dir):
            files = [f for f in os.listdir(json_dir) if f.endswith('.json')]
            files.sort()
            self.chapter_files = [os.path.join(json_dir, f) for f in files]
        else:
            print(f"Erreur : Le dossier {json_dir} est introuvable.")

        self.chapters = self.load_chapters()
        self.load_question_stats()

        self.num_questions_var = tk.IntVar(value=20)
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
        self.style.theme_use('default')
        
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
        
        # Style pour les cases à cocher
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
        
        # Style pour la barre de progression
        self.style.configure(
            "Custom.Horizontal.TProgressbar",
            background=theme['primary'],
            troughcolor=theme['bg'],
            bordercolor=theme['bg'],
            lightcolor=theme['primary'],
            darkcolor=theme['primary']
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
        if widget_type == 'Frame':
            widget.configure(background=theme['bg'])
        elif widget_type == 'Label':
            widget.configure(background=theme['bg'], foreground=theme['fg'])
        elif widget_type == 'Button':
            widget.configure(
                bg=theme['button_bg'], 
                fg=theme['button_fg'],
                activebackground=theme['primary'],
                activeforeground=theme['button_fg']
            )
        elif widget_type == 'Checkbutton':
            widget.configure(
                bg=theme['bg'], 
                fg=theme['fg'],
                activebackground=theme['bg'],
                activeforeground=theme['fg'],
                selectcolor=theme['selected_bg']
            )
        elif widget_type == 'Canvas':
            widget.configure(bg=theme['canvas'], highlightthickness=0)
        elif widget_type == 'Scrollbar':
            widget.configure(
                bg=theme['scrollbar'],
                troughcolor=theme['bg']
            )
        elif widget_type == 'Progressbar':
            widget.configure(style="Custom.Horizontal.TProgressbar")
        
        # Traiter les enfants récursivement
        for child in widget.winfo_children():
            self.update_widget_colors(child, theme)

    def toggle_theme(self):
        """Bascule entre les modes clair et sombre"""
        self.theme_mode = "dark" if self.theme_mode == "light" else "light"
        self.apply_theme()
        self.theme_button.configure(text="☀️" if self.theme_mode == "light" else "🌙")
        
        # Mettre à jour l'affichage si on est en mode feedback
        if hasattr(self, 'feedback_mode') and self.feedback_mode:
            self.update_feedback_colors()

    def update_feedback_colors(self):
        """Met à jour les couleurs du feedback lors du changement de thème"""
        theme = self.themes[self.theme_mode]
        
        # Mettre à jour le message de résultat
        if self.is_correct:
            self.feedback_label.configure(foreground=theme['correct'])
        else:
            self.feedback_label.configure(foreground=theme['incorrect'])
        
        # Mettre à jour les couleurs des options
        correct_answers = self.current_question_data["correct_answers"]
        for i in range(len(self.option_labels)):
            option_char = chr(65 + i)
            if option_char in correct_answers:
                # Bonne réponse
                self.option_frames[i].configure(style="Correct.TFrame")
                self.option_labels[i].configure(
                    foreground=theme['correct_fg'],
                    font=("Arial", 16, "bold")
                )
            elif self.selected_answers[i].get():
                # Réponse incorrecte sélectionnée
                self.option_frames[i].configure(style="Incorrect.TFrame")
                self.option_labels[i].configure(
                    foreground=theme['incorrect_fg'],
                    font=("Arial", 16, "bold")
                )
            else:
                # Réponse non sélectionnée
                self.option_frames[i].configure(style="TFrame")
                self.option_labels[i].configure(
                    foreground=theme['fg'],
                    font=LARGE_FONT
                )

    def on_window_resize(self, event):
        """Met à jour les éléments lors du redimensionnement de la fenêtre"""
        # Mettre à jour les wraplengths
        if hasattr(self, 'question_label'):
            self.update_wraplengths()

    def update_wraplengths(self):
        """Met à jour les wraplengths pour l'adaptation responsive"""
        if hasattr(self, 'question_label') and self.question_label.winfo_exists():
            new_width = self.winfo_width() - 100
            self.question_label.configure(wraplength=new_width)
            
            if hasattr(self, 'scrollable_frame') and self.scrollable_frame.winfo_exists():
                for child in self.scrollable_frame.winfo_children():
                    if child.winfo_exists():
                        for subchild in child.winfo_children():
                            if isinstance(subchild, ttk.Label) and subchild.winfo_exists():
                                subchild.configure(wraplength=new_width - 50)

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

        # Sélecteur de nombre de questions
        settings_frame = ttk.Frame(self.main_menu_frame)
        settings_frame.pack(pady=10, anchor='ne')
        
        ttk.Label(settings_frame, text="Nombre de questions:", font=LARGE_FONT).pack(side='left', padx=5)
        
        num_spinbox = ttk.Spinbox(
            settings_frame,
            from_=1,
            to=100,
            textvariable=self.num_questions_var,
            width=5,
            font=LARGE_FONT
        )
        num_spinbox.pack(side='left', padx=5)

        title = ttk.Label(self.main_menu_frame, text="Choisissez un chapitre", font=TITLE_FONT)
        title.pack(pady=40)

        button_frame = ttk.Frame(self.main_menu_frame)
        button_frame.pack(pady=20)

        for i, chapter_path in enumerate(self.chapter_files):
            # Récupère le nom du fichier (ex: "Endo.json")
            filename = os.path.basename(chapter_path)
            # Enlève l'extension (ex: "Endo")
            display_name = os.path.splitext(filename)[0]
            
            chapter_button = ttk.Button(
                button_frame, 
                text=display_name,
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
        
        self.last_chapter_index = chapter 

        self.quiz_frame = ttk.Frame(self)
        self.quiz_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Configuration pour un redimensionnement adaptatif
        self.quiz_frame.grid_columnconfigure(0, weight=1)
        self.quiz_frame.grid_rowconfigure(0, weight=1)

        self.current_question = 0
        num_questions = self.num_questions_var.get()
        
        if chapter == -1:
            self.current_chapter = self.mixed_chapter
        else:
            self.current_chapter = list(self.chapters[self.chapter_files[chapter]])
            random.shuffle(self.current_chapter)
            self.current_chapter = self.current_chapter[:min(num_questions, len(self.current_chapter))]
            
        self.total_questions = len(self.current_chapter)
        self.score = 0
        self.start_time = time.time()
        self.feedback_mode = False
        self.final_time = None

        self.show_question()

    def restart_quiz(self):
        """Relance le QCM avec les mêmes paramètres"""
        self.clear_frame(self.quiz_frame)
        self.quiz_frame.pack_forget()
        
        if self.last_chapter_index == -1:
            self.mix_all_chapters()
        else:
            self.start_quiz(self.last_chapter_index)

    def show_question(self):
        self.feedback_mode = False
        self.clear_frame(self.quiz_frame)

        # Frame principale avec gestion de redimensionnement
        main_container = ttk.Frame(self.quiz_frame)
        main_container.pack(fill='both', expand=True)
        
        # Configuration pour un redimensionnement adaptatif
        main_container.grid_columnconfigure(0, weight=1)
        main_container.grid_rowconfigure(0, weight=1)  # Pour le contenu
        main_container.grid_rowconfigure(1, weight=0)  # Pour le bouton
        main_container.grid_rowconfigure(2, weight=0)  # Pour la barre de progression
        main_container.grid_rowconfigure(3, weight=0)  # Pour la barre d'info

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

        self.current_question_data = self.current_chapter[self.current_question]
        
        # Question avec label adaptatif
        self.question_label = ttk.Label(
            self.scrollable_frame, 
            text=self.current_question_data["question"],
            font=LARGE_FONT,
            wraplength=self.winfo_width() - 100,
            justify="left",
            anchor="w"
        )
        self.question_label.pack(fill='x', padx=20, pady=20, anchor='w')

        # Options avec labels adaptatifs
        self.selected_answers = [tk.BooleanVar() for _ in self.current_question_data["options"]]
        
        # Listes pour stocker les éléments d'interface
        self.option_frames = []
        self.option_labels = []
        self.option_checkbuttons = []
        
        for i, option in enumerate(self.current_question_data["options"]):
            option_frame = ttk.Frame(self.scrollable_frame)
            option_frame.pack(fill='x', padx=20, pady=5, anchor='w')
            self.option_frames.append(option_frame)
            
            # Case à cocher
            answer_checkbutton = ttk.Checkbutton(
                option_frame, 
                variable=self.selected_answers[i],
                style="Large.TCheckbutton"
            )
            answer_checkbutton.pack(side='left', anchor='w', padx=(0, 10))
            self.option_checkbuttons.append(answer_checkbutton)
            
            # Texte de l'option
            option_label = ttk.Label(
                option_frame, 
                text=option,
                font=LARGE_FONT,
                wraplength=self.winfo_width() - 150,
                justify="left",
                anchor="w"
            )
            option_label.pack(side='left', fill='x', expand=True, anchor='w')
            self.option_labels.append(option_label)
            
            # Lier le label à la case à cocher
            option_label.bind("<Button-1>", lambda e, idx=i: self.option_checkbuttons[idx].invoke())
            
            # Ajouter des événements de survol pour l'option
            for w in (option_frame, answer_checkbutton, option_label):
                w.bind("<Enter>", lambda e, idx=i: self.on_option_hover(idx))
                w.bind("<Leave>", lambda e, idx=i: self.on_option_leave(idx))

        # Bouton Valider
        button_frame = ttk.Frame(main_container)
        button_frame.grid(row=1, column=0, columnspan=2, pady=20, sticky="ew")
        
        self.validate_button = ttk.Button(
            button_frame, 
            text="Valider", 
            command=self.check_answer,
            style="Large.TButton"
        )
        self.validate_button.pack(pady=20)

        # Barre de progression
        progress_frame = ttk.Frame(main_container)
        progress_frame.grid(row=2, column=0, columnspan=2, sticky="ew", padx=20, pady=10)
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            progress_frame,
            variable=self.progress_var,
            maximum=100,
            style="Custom.Horizontal.TProgressbar",
            mode='determinate'
        )
        self.progress_bar.pack(fill='x', expand=True)
        
        # Mettre à jour la progression
        progress_value = ((self.current_question) / len(self.current_chapter)) * 100
        self.progress_var.set(progress_value)

        # Barre d'information en bas
        bottom_frame = ttk.Frame(main_container)
        bottom_frame.grid(row=3, column=0, columnspan=2, sticky="ew", padx=20, pady=10)

        # Timer dynamique
        self.time_label_var = tk.StringVar()
        self.update_timer()
        
        time_label = ttk.Label(
            bottom_frame, 
            textvariable=self.time_label_var,
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

    def update_timer(self):
        """Met à jour le timer chaque seconde"""
        if hasattr(self, 'start_time') and not hasattr(self, 'final_time'):
            # Vérifier si l'application est toujours en cours
            if not self.winfo_exists():
                return
                
            elapsed_time = int(time.time() - self.start_time)
            hours, remainder = divmod(elapsed_time, 3600)
            minutes, seconds = divmod(remainder, 60)
            self.time_label_var.set(f"Temps écoulé : {hours}h {minutes}m {seconds}s")
            
            # Planifier la prochaine mise à jour dans 1 seconde
            self.after(1000, self.update_timer)

    def on_option_hover(self, option_index):
        """Effet visuel lorsque la souris survole une option"""
        if not self.feedback_mode:
            self.option_frames[option_index].configure(style="Hover.TFrame")

    def on_option_leave(self, option_index):
        """Effet visuel lorsque la souris quitte une option"""
        if not self.feedback_mode:
            self.option_frames[option_index].configure(style="TFrame")

    def check_answer(self):
        self.feedback_mode = True
        theme = self.themes[self.theme_mode]
        
        # Appliquer les styles pour le feedback
        self.style.configure(
            "Correct.TFrame", 
            background=theme['correct_bg']
        )
        self.style.configure(
            "Incorrect.TFrame", 
            background=theme['incorrect_bg']
        )
        
        correct_answers = self.current_question_data["correct_answers"]
        user_answers = [chr(i + 65) for i, selected in enumerate(self.selected_answers) if selected.get()]

        question_id = self.current_question_data["id"]
        question_stats = self.question_stats.get(question_id, {"correct": 0, "incorrect": 0})

        self.is_correct = sorted(correct_answers) == sorted(user_answers)
        
        if self.is_correct:
            question_stats["correct"] += 1
            self.score += 1
            feedback_text = "✓ Bonne réponse !"
            feedback_color = theme['correct']
        else:
            question_stats["incorrect"] += 1
            feedback_text = "✗ Mauvaise réponse"
            feedback_color = theme['incorrect']

        self.question_stats[question_id] = question_stats
        
        # Afficher le feedback global
        feedback_frame = ttk.Frame(self.scrollable_frame)
        feedback_frame.pack(fill='x', padx=20, pady=10, anchor='w')
        
        self.feedback_label = ttk.Label(
            feedback_frame, 
            text=feedback_text,
            font=("Arial", 18, "bold"),
            foreground=feedback_color
        )
        self.feedback_label.pack(side='left')
        
        # Désactiver toutes les cases à cocher
        for cb in self.option_checkbuttons:
            cb.configure(state=tk.DISABLED)
        
        # Mettre à jour le bouton
        self.validate_button.configure(text="Continuer", command=self.next_question)
        
        # Appliquer les couleurs aux options
        for i in range(len(self.option_labels)):
            option_char = chr(65 + i)
            
            if option_char in correct_answers:
                # Bonne réponse - mettre en vert et en gras
                self.option_frames[i].configure(style="Correct.TFrame")
                self.option_labels[i].configure(
                    foreground=theme['correct_fg'],
                    font=("Arial", 16, "bold")
                )
            elif self.selected_answers[i].get():
                # Réponse incorrecte sélectionnée - mettre en rouge
                self.option_frames[i].configure(style="Incorrect.TFrame")
                self.option_labels[i].configure(
                    foreground=theme['incorrect_fg'],
                    font=("Arial", 16, "bold")
                )

    def next_question(self):
        """Passe à la question suivante"""
        self.current_question += 1
        if self.current_question < len(self.current_chapter):
            self.show_question()
        else:
            self.final_time = time.time() - self.start_time
            self.show_final_score()

    def mix_all_chapters(self):
        all_chapters = [self.chapters[file] for file in self.chapter_files]
        mixed_questions = [question for chapter in all_chapters for question in chapter]
        random.shuffle(mixed_questions)
        num_questions = self.num_questions_var.get()
        self.mixed_chapter = random.sample(mixed_questions, min(num_questions, len(mixed_questions)))
        self.start_quiz(-1)

    def show_final_score(self):
        self.clear_frame(self.quiz_frame)

        center_frame = ttk.Frame(self.quiz_frame)
        center_frame.pack(expand=True, fill='both')
        
        # Configuration pour un redimensionnement adaptatif
        center_frame.grid_columnconfigure(0, weight=1)
        center_frame.grid_rowconfigure(0, weight=1)
        center_frame.grid_rowconfigure(1, weight=1)
        center_frame.grid_rowconfigure(2, weight=1)
        center_frame.grid_rowconfigure(3, weight=1)

        score_label = ttk.Label(
            center_frame, 
            text=f"Score final : {self.score}/{len(self.current_chapter)}", 
            font=TITLE_FONT
        )
        score_label.pack(pady=20)

        # Afficher le temps total
        total_time = int(self.final_time)
        hours, remainder = divmod(total_time, 3600)
        minutes, seconds = divmod(remainder, 60)
        time_str = f"Temps total : {hours}h {minutes}m {seconds}s"
        
        time_label = ttk.Label(
            center_frame, 
            text=time_str,
            font=RESULT_FONT
        )
        time_label.pack(pady=10)

        button_frame = ttk.Frame(center_frame)
        button_frame.pack(pady=20)

        restart_button = ttk.Button(
            button_frame, 
            text="Recommencer ce QCM", 
            command=self.restart_quiz,
            style="Large.TButton"
        )
        restart_button.pack(pady=10, fill='x')

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