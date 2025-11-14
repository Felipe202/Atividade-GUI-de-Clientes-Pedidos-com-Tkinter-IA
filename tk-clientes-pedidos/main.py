import os
import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap import Style
from tkinter import messagebox

# inicializa DB (garanta que db.init_db exista)
from db import create_tables as init_db

# views (assumindo que os arquivos em views/ estejam com os nomes abaixo)
from views.dashboard_view import DashboardView
from views.history_view import HistoryView
from views.reports_view import ReportsView
from views.ia_view import IAView
from views.clientes_view import ClientesView
from views.produtos_view import ProdutosView
from views.pedidos_view import PedidosView

# init DB
init_db()


def is_toplevel_class(cls):
    """Retorna True se cls é subclass de Toplevel (tk or ttk)."""
    try:
        mro = getattr(cls, "__mro__", ())
        return any(base.__name__.lower().endswith("toplevel") for base in mro)
    except Exception:
        return False


class App(ttk.Window):
    def __init__(self, theme="darkly"):
        super().__init__(themename=theme)
        self.title("Santana imports - LTDA")
        self.geometry("1100x700")

        # renomeado para evitar conflito com propriedade interna
        self.app_style = Style(theme=theme)

        # menu
        self._build_menu()

        # main area: abre o dashboard por padrão
        self.container = ttk.Frame(self, padding=20)
        self.container.pack(fill="both", expand=True)

        # Inicializa e salva a referência do dashboard
        self.dashboard = None
        self.open_dashboard()

    def _build_menu(self):
        menubar = tk.Menu(self)
        self.config(menu=menubar)

        menu_cad = tk.Menu(menubar, tearoff=0)
        menu_cad.add_command(label="Dashboard", command=lambda: self.open_dashboard())
        menu_cad.add_separator()
        menu_cad.add_command(label="Clientes", command=lambda: self.open_view(ClientesView, "Clientes"))
        menu_cad.add_command(label="Produtos", command=lambda: self.open_view(ProdutosView, "Produtos"))
        # CHAMADA MODIFICADA: USANDO open_pedidos_view
        menu_cad.add_command(label="Pedidos", command=lambda: self.open_pedidos_view())
        menubar.add_cascade(label="Cadastros", menu=menu_cad)

        menu_reports = tk.Menu(menubar, tearoff=0)
        menu_reports.add_command(label="Relatórios", command=lambda: self.open_view(ReportsView, "Relatórios"))
        menubar.add_cascade(label="Relatórios", menu=menu_reports)

        menu_ia = tk.Menu(menubar, tearoff=0)
        menu_ia.add_command(label="IA / Análises", command=lambda: self.open_view(IAView, "IA / Análises"))
        menubar.add_cascade(label="IA", menu=menu_ia)

        menubar.add_command(label="Histórico", command=lambda: self.open_view(HistoryView, "Histórico"))

        # Tema submenu
        menu_theme = tk.Menu(menubar, tearoff=0)
        menu_theme.add_command(label="Modo Escuro", command=lambda: self.set_theme("darkly"))
        menu_theme.add_command(label="Modo Claro", command=lambda: self.set_theme("flatly"))
        menubar.add_cascade(label="Modo", menu=menu_theme)

        menubar.add_command(label="Sair", command=self.on_exit)

    def open_dashboard(self):
        """Abre o Dashboard no container principal e garante que a referência self.dashboard seja atualizada."""

        # Remove a view atual do container
        for w in self.container.winfo_children():
            w.destroy()

        try:
            # Cria a nova instância do DashboardView (que é um Frame)
            new_dashboard = DashboardView(self.container)
            new_dashboard.pack(fill="both", expand=True)

            # ATUALIZA A REFERÊNCIA: ESSENCIAL PARA O CALLBACK EM open_pedidos_view
            self.dashboard = new_dashboard

        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível abrir Dashboard: {e}")

    def open_pedidos_view(self):
        """Abre PedidosView, injetando o método refresh do Dashboard."""

        # Garante que o dashboard existe e possui o método refresh
        if not self.dashboard or not hasattr(self.dashboard, 'refresh'):
            messagebox.showwarning("Aviso", "O Dashboard não está pronto para receber atualizações.")
            return

        try:
            # Obtém o método refresh do DashboardView
            dashboard_refresh_func = self.dashboard.refresh

            # Chama a PedidosView passando o callback (ela é Toplevel)
            PedidosView(self, dashboard_callback=dashboard_refresh_func)

        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao abrir Pedidos: {e}")

    def open_view(self, view_cls, title=""):
        """
        Abre uma view. Se view_cls for um Frame-like, coloca em Toplevel e instancia.
        (Mantido como fallback para as outras views)
        """
        try:
            if is_toplevel_class(view_cls):
                # view é Toplevel-like: chama diretamente com parent = self
                view_cls(self)
            else:
                # view é Frame-like: crie um Toplevel e coloque o Frame dentro
                win = ttk.Toplevel(self)
                win.title(title or getattr(view_cls, "__name__", "Janela"))
                try:
                    view_cls(win)  # frame que empacota dentro do Toplevel
                except TypeError:
                    # fallback: talvez a classe seja Toplevel mesmo
                    try:
                        view_cls(self)
                    except Exception as e:
                        messagebox.showerror("Erro", f"Falha ao abrir a view: {e}")
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao abrir a view: {e}")

    def set_theme(self, theme_name: str):
        try:
            self.app_style.theme_use(theme_name)
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível aplicar o modo: {e}")

    def on_exit(self):
        if messagebox.askyesno("Sair", "Deseja realmente sair?"):
            self.destroy()


if __name__ == "__main__":
    # garante working dir no root do projeto (opcional)
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    app = App(theme="darkly")  # abre no tema escuro por padrão
    app.mainloop()