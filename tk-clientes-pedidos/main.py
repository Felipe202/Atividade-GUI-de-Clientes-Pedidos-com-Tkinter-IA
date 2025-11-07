# main.py
import tkinter as tk
from tkinter import ttk, messagebox
from db import init_db
from views.clientes_view import ClientesView
from views.pedidos_view import PedidosView
from views.produtos_view import ProdutosFrame
from views.dashboard_view import DashboardFrame
from views.reports_view import ReportsFrame
from views.history_view import HistoryFrame
from views.ia_view import IAView
from utils import log_action

def open_window(frame_class, title):
    w = tk.Toplevel(root)
    w.title(title)
    frame_class(w)

def on_closing():
    if messagebox.askokcancel("Sair", "Deseja sair do aplicativo?"):
        log_action("Exit", "App")
        root.destroy()

if __name__ == "__main__":
    init_db()
    root = tk.Tk()
    root.title("Sistema - Clientes, Pedidos, Produtos (Fase 2)")
    root.geometry("900x600")

    # Menu Bar
    menubar = tk.Menu(root)
    cad = tk.Menu(menubar, tearoff=0)
    cad.add_command(label="Clientes", command=lambda: open_window(ClientesView, "Clientes"))
    cad.add_command(label="Pedidos", command=lambda: open_window(PedidosView, "Pedidos"))
    cad.add_command(label="Produtos", command=lambda: open_window(ProdutosFrame, "Produtos"))
    menubar.add_cascade(label="Cadastros", menu=cad)

    rel = tk.Menu(menubar, tearoff=0)
    rel.add_command(label="Dashboard", command=lambda: open_window(DashboardFrame, "Dashboard"))
    rel.add_command(label="Relatórios", command=lambda: open_window(ReportsFrame, "Relatórios"))
    menubar.add_cascade(label="Relatórios", menu=rel)

    ia_menu = tk.Menu(menubar, tearoff=0)
    ia_menu.add_command(label="IA / Análises", command=lambda: open_window(IAView, "IA / Análises"))
    menubar.add_cascade(label="IA", menu=ia_menu)

    menubar.add_command(label="Histórico", command=lambda: open_window(HistoryFrame, "Histórico"))
    menubar.add_command(label="Sair", command=on_closing)
    root.config(menu=menubar)

    # inicia com Dashboard
    DashboardFrame(root)

    root.protocol("WM_DELETE_WINDOW", on_closing)
    log_action("Start", "App")
    root.mainloop()

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sistema de Clientes, Pedidos e Produtos")
        self.geometry("900x600")
        self.configure(bg="#f2f2f2")

        # ttk style
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TFrame", background="#f2f2f2")
        style.configure("TLabel", background="#f2f2f2", font=("Segoe UI", 10))
        style.configure("TButton", padding=6, font=("Segoe UI", 10, "bold"))
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))
        style.configure("Accent.TButton", background="#0078D7", foreground="white")

        self._build_menu()
        self._build_main_frame()

    def _build_menu(self):
        menubar = tk.Menu(self)
        self.config(menu=menubar)

        menu_cadastros = tk.Menu(menubar, tearoff=0)
        menu_cadastros.add_command(label="Clientes", command=self.abrir_clientes)
        menu_cadastros.add_command(label="Pedidos", command=self.abrir_pedidos)
        menu_cadastros.add_command(label="Produtos", command=self.abrir_produtos)
        menubar.add_cascade(label="Cadastros", menu=menu_cadastros)

        menubar.add_command(label="Sair", command=self.on_close)

    def _build_main_frame(self):
        frame = ttk.Frame(self, padding=20)
        frame.pack(expand=True, fill="both")

        title = ttk.Label(frame, text="Bem-vindo ao Sistema", font=("Segoe UI", 16, "bold"))
        title.pack(pady=30)

        ttk.Label(frame, text="Escolha uma opção no menu acima para começar.").pack(pady=10)

    def abrir_clientes(self):
        ClientesView(self)

    def abrir_pedidos(self):
        PedidosView(self)

    def abrir_produtos(self):
        ProdutosView(self)

    def on_close(self):
        if messagebox.askyesno("Sair", "Deseja realmente sair?"):
            self.destroy()