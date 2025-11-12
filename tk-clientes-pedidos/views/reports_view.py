# views/reports_view.py
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox, filedialog
import csv
from db import list_clientes, list_produtos, list_pedidos


class ReportsView(ttk.Frame):
    def __init__(self, master):
        super().__init__(master, padding=20)
        self.pack(fill=BOTH, expand=True)
        self.create_widgets()

    def create_widgets(self):
        title = ttk.Label(
            self,
            text="📊 Relatórios",
            font=("Segoe UI", 18, "bold"),
            bootstyle="inverse-primary",
        )
        title.pack(anchor="w", pady=(0, 20))

        frame_top = ttk.Frame(self)
        frame_top.pack(fill=X, pady=10)

        ttk.Label(frame_top, text="Selecione o tipo de relatório:", font=("Segoe UI", 10)).pack(side=LEFT, padx=(0, 10))

        self.combo_tipo = ttk.Combobox(
            frame_top,
            values=["Clientes", "Produtos", "Pedidos"],
            state="readonly",
            width=20,
        )
        self.combo_tipo.current(0)
        self.combo_tipo.pack(side=LEFT, padx=(0, 10))

        ttk.Button(frame_top, text="Gerar", bootstyle="info-outline", command=self.gerar_relatorio).pack(side=LEFT)
        ttk.Button(frame_top, text="Exportar CSV", bootstyle="success-outline", command=self.exportar_csv).pack(side=LEFT, padx=(10, 0))

        # Treeview para mostrar os dados
        self.tree = ttk.Treeview(self, show="headings", bootstyle="dark", height=18)
        self.tree.pack(fill=BOTH, expand=True, pady=(15, 0))

    def gerar_relatorio(self):
        tipo = self.combo_tipo.get()
        for i in self.tree.get_children():
            self.tree.delete(i)

        if tipo == "Clientes":
            self.tree["columns"] = ("id", "nome", "email", "telefone")
            for col in self.tree["columns"]:
                self.tree.heading(col, text=col.capitalize())
                self.tree.column(col, width=150)
            dados = list_clientes()
        elif tipo == "Produtos":
            self.tree["columns"] = ("id", "nome", "preco", "estoque")
            for col in self.tree["columns"]:
                self.tree.heading(col, text=col.capitalize())
                self.tree.column(col, width=150)
            dados = list_produtos()
        else:  # Pedidos
            self.tree["columns"] = ("id", "cliente_id", "data", "total")
            for col in self.tree["columns"]:
                self.tree.heading(col, text=col.capitalize())
                self.tree.column(col, width=150)
            dados = list_pedidos()

        for row in dados:
            self.tree.insert("", "end", values=row)

        messagebox.showinfo("Relatório", f"Relatório de {tipo.lower()} gerado com sucesso!")

    def exportar_csv(self):
        tipo = self.combo_tipo.get()
        dados = [self.tree.item(item)["values"] for item in self.tree.get_children()]
        if not dados:
            messagebox.showwarning("Aviso", "Gere um relatório antes de exportar.")
            return

        arquivo = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("Arquivo CSV", "*.csv")],
            title="Salvar Relatório"
        )
        if not arquivo:
            return

        try:
            with open(arquivo, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(self.tree["columns"])
                writer.writerows(dados)
            messagebox.showinfo("Sucesso", f"Relatório exportado para:\n{arquivo}")
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao exportar: {e}")
