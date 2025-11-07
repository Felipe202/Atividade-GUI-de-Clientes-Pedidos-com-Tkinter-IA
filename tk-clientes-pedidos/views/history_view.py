# views/history_view.py
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import tkinter as tk
from tkinter import ttk, messagebox
from utils import LOG_FILE, log_action
import os

class HistoryFrame(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.pack(fill="both", expand=True, padx=8, pady=8)
        self.create_widgets()
        self.load_history()

    def create_widgets(self):
        self.text = tk.Text(self, wrap="none", height=20)
        self.text.pack(fill="both", expand=True)
        btns = ttk.Frame(self)
        btns.pack(fill="x", pady=6)
        ttk.Button(btns, text="Limpar Histórico", command=self.clear_history).pack(side="left", padx=6)
        ttk.Button(btns, text="Recarregar", command=self.load_history).pack(side="left", padx=6)

    def load_history(self):
        self.text.delete("1.0", "end")
        if not os.path.exists(LOG_FILE):
            self.text.insert("end", "Nenhum histórico encontrado.")
            return
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            self.text.insert("end", f.read())

    def clear_history(self):
        if not messagebox.askyesno("Confirmar", "Deseja limpar o histórico?"):
            return
        open(LOG_FILE, "w").close()
        self.load_history()
        log_action("Clear", "History")
