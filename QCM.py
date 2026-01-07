import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import time
import os
import ctypes
import re
import random # Utilisé pour le mélange des options d'affichage

# Import de notre nouveau module logique
import backend

LARGE_FONT = ("Arial", 16)
TITLE_FONT = ("Arial", 24, "bold")
BUTTON_FONT = ("Arial", 14)
RESULT_FONT = ("Arial", 18)

class QCMApp(tk.Tk):
    def __init__(self):
        super().__init__()

        try:
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
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # --- THÈMES ---
        self.theme_mode = "light"
        self.themes = {
            "light": {
                "bg": "#ffffff", "fg": "#000000", "button_bg": "#f0f0f0", "button_fg": "#000000",
                "primary": "#1a73e8", "text_bg": "#ffffff", "correct": "#2ecc71", "incorrect": "#e74c3c",
                "scrollbar": "#c0c0c0", "canvas": "#ffffff", "entry": "#ffffff", "toolbar": "#e0e0e0",
                "hover": "#306eac", "checkbox": "#1a73e8", "selected_bg": "#f0f8ff",
                "correct_bg": "#2e7d32", "correct_fg": "#2e7d32", 
                "incorrect_bg": "#c62828", "incorrect_fg": "#c62828"
            },
            "dark": {
                "bg": "#1e1e1e", "fg": "#ffffff", "button_bg": "#3d3d3d", "button_fg": "#ffffff",
                "primary": "#4a9cff", "text_bg": "#2d2d2d", "correct": "#27ae60", "incorrect": "#c0392b",
                "scrollbar": "#606060", "canvas": "#1e1e1e", "entry": "#333333", "toolbar": "#333333",
                "hover": "#306eac", "checkbox": "#6ab0ff", "selected_bg": "#2a3a4a",
                "correct_bg": "#1b5e20", "correct_fg": "#a5d6a7",
                "incorrect_bg": "#7f0000", "incorrect_fg": "#ff8a80"
            }
        }
        
        # Barre d'outils
        self.toolbar_frame = ttk.Frame(self)
        self.toolbar_frame.pack(fill='x', padx=10, pady=5)
        
        self.theme_button = tk.Button(
            self.toolbar_frame, text="☀️", command=self.toggle_theme,
            font=("Arial", 14), bd=0, relief="flat", padx=10, pady=5
        )
        self.theme_button.pack(side='right', padx=5, pady=5)
        
        self.apply_theme()
        
        # --- CHARGEMENT DES DONNÉES VIA BACKEND ---
        json_dir = backend.get_json_dir(__file__)
        self.chapter_files, self.chapters = backend.load_chapters(json_dir)
        self.question_stats = backend.load_stats()

        self.num_questions_var = tk.IntVar(value=20)
        self.shuffle_options_var = tk.BooleanVar(value=False)
        self.create_main_menu()
        
        self.bind("<Configure>", self.on_window_resize)

    # --- GESTION DES THÈMES (Inchangé ou presque) ---
    def apply_theme(self):
        theme = self.themes[self.theme_mode]
        self.configure(background=theme['bg'])
        self.style = ttk.Style()
        self.style.theme_use('default')
        
        self.style.configure("TFrame", background=theme['bg'])
        self.style.configure("TLabel", background=theme['bg'], foreground=theme['fg'])
        self.style.configure("TButton", background=theme['button_bg'], foreground=theme['button_fg'],
                             borderwidth=1, relief="solid", font=BUTTON_FONT)
        self.style.map("TButton", background=[('active', theme['primary'])])
        self.style.configure("Large.TButton", font=BUTTON_FONT, padding=10)
        
        self.style.configure("TCheckbutton", background=theme['bg'], foreground=theme['fg'],
                             indicatorbackground=theme['bg'], indicatorforeground=theme['checkbox'],
                             selectcolor=theme['selected_bg'])
        self.style.configure("Large.TCheckbutton", font=LARGE_FONT)
        self.style.configure("TScrollbar", background=theme['scrollbar'], troughcolor=theme['bg'])
        self.style.configure("Hover.TFrame", background=theme['hover'])
        
        self.style.configure("Custom.Horizontal.TProgressbar", background=theme['primary'],
                             troughcolor=theme['bg'], bordercolor=theme['bg'],
                             lightcolor=theme['primary'], darkcolor=theme['primary'])
        
        self.theme_button.configure(bg=theme['toolbar'], fg=theme['fg'],
                                    activebackground=theme['toolbar'], activeforeground=theme['fg'])
        self.update_all_widgets()

    def update_all_widgets(self):
        theme = self.themes[self.theme_mode]
        for widget in self.winfo_children():
            self.update_widget_colors(widget, theme)

    def update_widget_colors(self, widget, theme):
        try:
            widget_type = widget.winfo_class()
            if widget_type == 'Frame': widget.configure(background=theme['bg'])
            elif widget_type == 'Label': widget.configure(background=theme['bg'], foreground=theme['fg'])
            elif widget_type == 'Button':
                if widget != self.theme_button: # Ne pas écraser le bouton thème s'il est géré manuellement
                     widget.configure(bg=theme['button_bg'], fg=theme['button_fg'],
                                     activebackground=theme['primary'], activeforeground=theme['button_fg'])
            elif widget_type == 'Checkbutton':
                widget.configure(bg=theme['bg'], fg=theme['fg'], activebackground=theme['bg'],
                                activeforeground=theme['fg'], selectcolor=theme['selected_bg'])
            elif widget_type == 'Canvas': widget.configure(bg=theme['canvas'], highlightthickness=0)
            elif widget_type == 'Scrollbar': widget.configure(bg=theme['scrollbar'], troughcolor=theme['bg'])
            elif widget_type == 'Progressbar': widget.configure(style="Custom.Horizontal.TProgressbar")
        except: pass
        
        for child in widget.winfo_children():
            self.update_widget_colors(child, theme)

    def toggle_theme(self):
        self.theme_mode = "dark" if self.theme_mode == "light" else "light"
        self.apply_theme()
        self.theme_button.configure(text="☀️" if self.theme_mode == "light" else "🌙")
        if hasattr(self, 'feedback_mode') and self.feedback_mode:
            self.update_feedback_colors()

    def update_feedback_colors(self):
        theme = self.themes[self.theme_mode]
        if self.is_correct: self.feedback_label.configure(foreground=theme['correct'])
        else: self.feedback_label.configure(foreground=theme['incorrect'])
        
        correct_answers = self.current_correct_answers_list
        for i in range(len(self.option_labels)):
            option_char = chr(65 + i)
            if option_char in correct_answers:
                self.option_frames[i].configure(style="Correct.TFrame")
                self.option_labels[i].configure(foreground=theme['correct_fg'], font=("Arial", 16, "bold"))
            elif self.selected_answers[i].get():
                self.option_frames[i].configure(style="Incorrect.TFrame")
                self.option_labels[i].configure(foreground=theme['incorrect_fg'], font=("Arial", 16, "bold"))
            else:
                self.option_frames[i].configure(style="TFrame")
                self.option_labels[i].configure(foreground=theme['fg'], font=LARGE_FONT)

    def on_window_resize(self, event):
        self.update_wraplengths()

    def update_wraplengths(self):
        if hasattr(self, 'question_label') and self.question_label.winfo_exists():
            new_width = self.winfo_width() - 100
            self.question_label.configure(wraplength=new_width)
            if hasattr(self, 'scrollable_frame') and self.scrollable_frame.winfo_exists():
                for child in self.scrollable_frame.winfo_children():
                    if child.winfo_exists():
                        for subchild in child.winfo_children():
                            if isinstance(subchild, ttk.Label) and subchild.winfo_exists():
                                subchild.configure(wraplength=new_width - 50)

    # --- MENU PRINCIPAL ---
    def create_main_menu(self):
        self.main_menu_frame = ttk.Frame(self)
        self.main_menu_frame.pack(expand=True, fill='both')
        self.main_menu_frame.grid_columnconfigure(0, weight=1)
        self.main_menu_frame.grid_rowconfigure(0, weight=1)
        self.main_menu_frame.grid_rowconfigure(1, weight=1)

        settings_frame = ttk.Frame(self.main_menu_frame)
        settings_frame.pack(pady=10, anchor='ne')
        
        ttk.Label(settings_frame, text="Nombre de questions:", font=LARGE_FONT).pack(side='left', padx=5)
        num_spinbox = ttk.Spinbox(settings_frame, from_=1, to=100, textvariable=self.num_questions_var, width=5, font=LARGE_FONT)
        num_spinbox.pack(side='left', padx=5)

        shuffle_check = tk.Checkbutton(
            settings_frame, text="Shuffle", variable=self.shuffle_options_var,
            font=("Arial", 12), bg=self.themes[self.theme_mode]['bg'], fg=self.themes[self.theme_mode]['fg'],
            selectcolor=self.themes[self.theme_mode]['bg'], activebackground=self.themes[self.theme_mode]['bg'],
            activeforeground=self.themes[self.theme_mode]['fg']
        )
        shuffle_check.pack(pady=(10, 20))

        ttk.Label(self.main_menu_frame, text="Choisissez un chapitre", font=TITLE_FONT).pack(pady=40)

        button_frame = ttk.Frame(self.main_menu_frame)
        button_frame.pack(pady=20)

        for i, chapter_path in enumerate(self.chapter_files):
            filename = os.path.basename(chapter_path)
            display_name = os.path.splitext(filename)[0]
            ttk.Button(button_frame, text=display_name, command=lambda i=i: self.start_quiz(i), style="Large.TButton").pack(pady=10, fill='x')

        ttk.Button(button_frame, text="Mélange de tous les chapitres", command=self.mix_all_chapters, style="Large.TButton").pack(pady=10, fill='x')

    # --- LOGIQUE QUIZ ---
    def start_quiz(self, chapter_index):   
        self.main_menu_frame.pack_forget()
        self.last_chapter_index = chapter_index 
        self.quiz_frame = ttk.Frame(self)
        self.quiz_frame.pack(fill='both', expand=True, padx=20, pady=20)
        self.quiz_frame.grid_columnconfigure(0, weight=1)
        self.quiz_frame.grid_rowconfigure(0, weight=1)

        self.current_question = 0
        num_questions = self.num_questions_var.get()
        
        if chapter_index == -1:
            # Chapitre mixte déjà préparé
            pass 
        else:
            raw_chapter = list(self.chapters[self.chapter_files[chapter_index]])
            # Utilisation de backend pour la sélection intelligente
            self.current_chapter = backend.smart_select_questions(raw_chapter, num_questions, self.question_stats)
            
        self.total_questions = len(self.current_chapter)
        self.score = 0
        self.start_time = time.time()
        self.feedback_mode = False
        self.final_time = None
        self.show_question()

    def mix_all_chapters(self):
        all_chapters = [self.chapters[file] for file in self.chapter_files]
        mixed_questions = [question for chapter in all_chapters for question in chapter]
        num_questions = self.num_questions_var.get()
        # Utilisation de backend pour le mélange
        self.current_chapter = backend.smart_select_questions(mixed_questions, num_questions, self.question_stats)
        self.start_quiz(-1)

    def restart_quiz(self):
        self.clear_frame(self.quiz_frame)
        self.quiz_frame.pack_forget()
        if self.last_chapter_index == -1:
            self.mix_all_chapters()
        else:
            self.start_quiz(self.last_chapter_index)

    def show_question(self):
        self.feedback_mode = False
        self.clear_frame(self.quiz_frame)

        main_container = ttk.Frame(self.quiz_frame)
        main_container.pack(fill='both', expand=True)
        main_container.grid_columnconfigure(0, weight=1)
        main_container.grid_rowconfigure(0, weight=1)
        
        theme = self.themes[self.theme_mode]
        canvas = tk.Canvas(main_container, bg=theme['canvas'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_container, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)

        self.scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        canvas.bind("<Configure>", lambda e: (canvas.itemconfig("all", width=e.width), self.scrollable_frame.configure(width=e.width)))

        self.current_question_data = self.current_chapter[self.current_question]
        
        # --- MÉLANGE DES RÉPONSES (Logique d'affichage locale) ---
        raw_options = self.current_question_data["options"]
        raw_correct = self.current_question_data["correct_answers"]
        
        if self.shuffle_options_var.get():
            indexed_options = list(enumerate(raw_options))
            random.shuffle(indexed_options)
            self.display_options = [text for _, text in indexed_options]
            original_correct_indices = [ord(c) - 65 for c in raw_correct]
            self.current_correct_answers_list = []
            for new_index, (old_index, text) in enumerate(indexed_options):
                if old_index in original_correct_indices:
                    self.current_correct_answers_list.append(chr(65 + new_index))
        else:
            self.display_options = list(raw_options)
            self.current_correct_answers_list = list(raw_correct)

        self.question_label = ttk.Label(
            self.scrollable_frame, text=self.current_question_data["question"],
            font=LARGE_FONT, wraplength=self.winfo_width() - 100, justify="left", anchor="w"
        )
        self.question_label.pack(fill='x', padx=20, pady=20, anchor='w')

        self.selected_answers = [tk.BooleanVar() for _ in self.display_options]
        self.option_frames = []
        self.option_labels = []
        self.option_checkbuttons = []
        
        for i, option_text in enumerate(self.display_options):
            clean_text = re.sub(r'^[A-E0-9][\.\)]\s*', '', option_text)
            
            option_frame = ttk.Frame(self.scrollable_frame)
            option_frame.pack(fill='x', padx=20, pady=5, anchor='w')
            self.option_frames.append(option_frame)
            
            answer_checkbutton = ttk.Checkbutton(option_frame, variable=self.selected_answers[i], style="Large.TCheckbutton")
            answer_checkbutton.pack(side='left', anchor='w', padx=(0, 10))
            self.option_checkbuttons.append(answer_checkbutton)
            
            display_label = f"{chr(65+i)}. {clean_text}"
            option_label = ttk.Label(
                option_frame, text=display_label, font=LARGE_FONT,
                wraplength=self.winfo_width() - 150, justify="left", anchor="w"
            )
            option_label.pack(side='left', fill='x', expand=True, anchor='w')
            self.option_labels.append(option_label)
            
            option_label.bind("<Button-1>", lambda e, idx=i: self.option_checkbuttons[idx].invoke())
            for w in (option_frame, answer_checkbutton, option_label):
                w.bind("<Enter>", lambda e, idx=i: self.on_option_hover(idx))
                w.bind("<Leave>", lambda e, idx=i: self.on_option_leave(idx))

        button_frame = ttk.Frame(main_container)
        button_frame.grid(row=1, column=0, columnspan=2, pady=20, sticky="ew")
        
        self.validate_button = ttk.Button(button_frame, text="Valider", command=self.check_answer, style="Large.TButton")
        self.validate_button.pack(pady=20)

        edit_button = tk.Button(
            button_frame, text="✏️ Corriger une erreur", command=self.open_editor,
            font=("Arial", 10, "italic"), fg="gray", bd=0, bg=self.themes[self.theme_mode]['bg'],
            activebackground=self.themes[self.theme_mode]['bg'], cursor="hand2"
        )
        edit_button.pack(side='top', pady=5)

        progress_frame = ttk.Frame(main_container)
        progress_frame.grid(row=2, column=0, columnspan=2, sticky="ew", padx=20, pady=10)
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, maximum=100, style="Custom.Horizontal.TProgressbar", mode='determinate')
        self.progress_bar.pack(fill='x', expand=True)
        self.progress_var.set(((self.current_question + 1) / len(self.current_chapter)) * 100)

        bottom_frame = ttk.Frame(main_container)
        bottom_frame.grid(row=3, column=0, columnspan=2, sticky="ew", padx=20, pady=10)

        self.time_label_var = tk.StringVar()
        self.update_timer()
        ttk.Label(bottom_frame, textvariable=self.time_label_var, font=LARGE_FONT).pack(side='left')
        remaining = len(self.current_chapter) - self.current_question
        ttk.Label(bottom_frame, text=f"Questions restantes : {remaining}", font=LARGE_FONT).pack(side='right')

        self.update_wraplengths()

    def check_answer(self):
        self.feedback_mode = True
        theme = self.themes[self.theme_mode]
        self.style.configure("Correct.TFrame", background=theme['correct_bg'])
        self.style.configure("Incorrect.TFrame", background=theme['incorrect_bg'])
        
        correct_answers = self.current_correct_answers_list
        user_answers = [chr(i + 65) for i, selected in enumerate(self.selected_answers) if selected.get()]

        # Mise à jour des stats via backend
        question_key = backend.get_question_key(self.current_question_data)
        question_stats = self.question_stats.get(str(question_key), {"correct": 0, "incorrect": 0})

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

        self.question_stats[str(question_key)] = question_stats
        
        feedback_frame = ttk.Frame(self.scrollable_frame)
        feedback_frame.pack(fill='x', padx=20, pady=10, anchor='w')
        self.feedback_label = ttk.Label(feedback_frame, text=feedback_text, font=("Arial", 18, "bold"), foreground=feedback_color)
        self.feedback_label.pack(side='left')
        
        for cb in self.option_checkbuttons: cb.configure(state=tk.DISABLED)
        self.validate_button.configure(text="Continuer", command=self.next_question)
        self.update_feedback_colors()

    def next_question(self):
        self.current_question += 1
        if self.current_question < len(self.current_chapter):
            self.show_question()
        else:
            self.final_time = time.time() - self.start_time
            self.show_final_score()

    def show_final_score(self):
        self.clear_frame(self.quiz_frame)
        center_frame = ttk.Frame(self.quiz_frame)
        center_frame.pack(expand=True, fill='both')
        center_frame.grid_columnconfigure(0, weight=1)
        
        # Labels de fin
        ttk.Label(center_frame, text=f"Score final : {self.score}/{len(self.current_chapter)}", font=TITLE_FONT).pack(pady=20)
        
        total_time = int(self.final_time)
        hours, remainder = divmod(total_time, 3600)
        minutes, seconds = divmod(remainder, 60)
        ttk.Label(center_frame, text=f"Temps total : {hours}h {minutes}m {seconds}s", font=RESULT_FONT).pack(pady=10)

        button_frame = ttk.Frame(center_frame)
        button_frame.pack(pady=20)
        
        ttk.Button(button_frame, text="Recommencer ce QCM", command=self.restart_quiz, style="Large.TButton").pack(pady=10, fill='x')
        ttk.Button(button_frame, text="Retour au menu principal", command=self.return_to_main_menu, style="Large.TButton").pack(pady=10, fill='x')
        ttk.Button(button_frame, text="Quitter", command=self.quit, style="Large.TButton").pack(pady=10, fill='x')
        
        # Sauvegarde stats via backend
        backend.save_stats(self.question_stats)

    def return_to_main_menu(self):
        self.clear_frame(self.quiz_frame)
        self.quiz_frame.pack_forget()
        self.create_main_menu()

    def open_editor(self):
        editor = tk.Toplevel(self)
        editor.title("Éditeur de question")
        editor.geometry("600x700")
        theme = self.themes[self.theme_mode]
        editor.configure(bg=theme['bg'])
        
        lbl_style = {"bg": theme['bg'], "fg": theme['fg'], "font": ("Arial", 12, "bold")}
        
        tk.Label(editor, text="Question :", **lbl_style).pack(anchor="w", padx=10, pady=5)
        txt_question = scrolledtext.ScrolledText(editor, height=5, font=("Arial", 12))
        txt_question.insert("1.0", self.current_question_data["question"])
        txt_question.pack(fill="x", padx=10)

        tk.Label(editor, text="Options :", **lbl_style).pack(anchor="w", padx=10, pady=(10, 5))
        entries_options = []
        vars_correct = []
        options_frame = tk.Frame(editor, bg=theme['bg'])
        options_frame.pack(fill="x", padx=10)

        current_opts = self.current_question_data["options"]
        correct_answers = self.current_question_data["correct_answers"]

        for i in range(5):
            row_frame = tk.Frame(options_frame, bg=theme['bg'])
            row_frame.pack(fill="x", pady=2)
            letter = chr(65 + i)
            tk.Label(row_frame, text=f"{letter}.", font=("Arial", 12, "bold"), bg=theme['bg'], fg=theme['fg']).pack(side="left")
            entry = tk.Entry(row_frame, font=("Arial", 12))
            val = current_opts[i] if i < len(current_opts) else ""
            entry.insert(0, val)
            entry.pack(side="left", fill="x", expand=True, padx=5)
            entries_options.append(entry)
            var = tk.BooleanVar(value=letter in correct_answers)
            vars_correct.append(var)
            tk.Checkbutton(row_frame, text="Correcte", variable=var, bg=theme['bg'], fg=theme['fg'], selectcolor=theme['bg']).pack(side="right")

        def save_changes():
            new_q = txt_question.get("1.0", "end-1c").strip()
            new_opts = [e.get().strip() for e in entries_options if e.get().strip()]
            new_correct = [chr(65+i) for i, var in enumerate(vars_correct) if var.get()]
            
            if not new_q or not new_opts or not new_correct:
                messagebox.showwarning("Erreur", "Remplir tous les champs.", parent=editor)
                return

            # Mise à jour mémoire
            self.current_question_data["question"] = new_q
            self.current_question_data["options"] = new_opts
            self.current_question_data["correct_answers"] = new_correct
            
            # Appel backend pour sauvegarde disque
            success, msg = backend.update_question_in_file(self.current_question_data, new_q, new_opts, new_correct)
            if success:
                print(msg)
                editor.destroy()
                self.show_question()
            else:
                messagebox.showerror("Erreur", msg, parent=editor)

        btn_frame = tk.Frame(editor, bg=theme['bg'])
        btn_frame.pack(pady=20)
        tk.Button(btn_frame, text="Sauvegarder", command=save_changes, bg="#2ecc71", fg="white", font=BUTTON_FONT).pack(side="left", padx=10)
        tk.Button(btn_frame, text="Annuler", command=editor.destroy, bg="#e74c3c", fg="white", font=BUTTON_FONT).pack(side="left", padx=10)

    # --- UTILITAIRES INTERFACE ---
    def update_timer(self):
        if hasattr(self, 'start_time') and not hasattr(self, 'final_time'):
            if not self.winfo_exists(): return
            elapsed_time = int(time.time() - self.start_time)
            hours, remainder = divmod(elapsed_time, 3600)
            minutes, seconds = divmod(remainder, 60)
            self.time_label_var.set(f"Temps écoulé : {hours}h {minutes}m {seconds}s")
            self.after(1000, self.update_timer)

    def on_option_hover(self, idx):
        if not self.feedback_mode: self.option_frames[idx].configure(style="Hover.TFrame")
    def on_option_leave(self, idx):
        if not self.feedback_mode: self.option_frames[idx].configure(style="TFrame")
    def clear_frame(self, frame):
        for widget in frame.winfo_children(): widget.destroy()

if __name__ == "__main__":
    app = QCMApp()
    app.mainloop()