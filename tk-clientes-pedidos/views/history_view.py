# views/history_view.py
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox
from db import list_pedidos, get_itens_pedido, list_clientes


class HistoryView(ttk.Frame):
    def __init__(self, master):
        super().__init__(master, padding=20)
        self.pack(fill=BOTH, expand=True)
        self.create_widgets()
        self.load_history()

    def create_widgets(self):
        title = ttk.Label(
            self,
            text="🕓 Histórico de Pedidos",
            font=("Segoe UI", 18, "bold"),
            bootstyle="inverse-primary",
        )
        title.pack(anchor="w", pady=(0, 20))

        top_frame = ttk.Frame(self)
        top_frame.pack(fill=X, pady=5)

        ttk.Label(top_frame, text="Buscar por cliente:", font=("Segoe UI", 10)).pack(
            side=LEFT, padx=(0, 5)
        )

        self.search_entry = ttk.Entry(top_frame, width=30)
        self.search_entry.pack(side=LEFT, padx=(0, 10))

        ttk.Button(
            top_frame, text="Filtrar", bootstyle="info-outline", command=self.load_history
        ).pack(side=LEFT)

        ttk.Button(
            top_frame, text="Recarregar", bootstyle="secondary-outline", command=self.refresh
        ).pack(side=LEFT, padx=(10, 0))

        # Treeview para histórico
        columns = ("id", "cliente", "data", "total")
        self.tree = ttk.Treeview(
            self,
            columns=columns,
            show="headings",
            bootstyle="dark",
            height=15,
        )
        self.tree.pack(fill=BOTH, expand=True, pady=10)

        for col, text in zip(columns, ["ID", "Cliente", "Data", "Total (R$)"]):
            self.tree.heading(col, text=text)
            self.tree.column(col, width=150 if col != "id" else 60)

        ttk.Button(
            self, text="Ver Itens do Pedido", bootstyle="success", command=self.ver_itens
        ).pack(pady=(5, 0))

    def load_history(self):
        try:
            filtro = self.search_entry.get().lower().strip()
            pedidos = list_pedidos()
            clientes = {c[0]: c[1] for c in list_clientes()}

            for i in self.tree.get_children():
                self.tree.delete(i)

            for p in pedidos:
                pid, cid, _, data, total = p
                nome_cliente = clientes.get(cid, "—")
                if filtro and filtro not in nome_cliente.lower():
                    continue
                self.tree.insert("", "end", values=(pid, nome_cliente, data, f"{total:.2f}"))
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao carregar histórico: {e}")

    def refresh(self):
        self.search_entry.delete(0, "end")
        self.load_history()

    def ver_itens(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione um pedido para visualizar.")
            return

        pedido_id = self.tree.item(selected[0], "values")[0]
        itens = get_itens_pedido(pedido_id)

        if not itens:
            messagebox.showinfo("Itens", "Nenhum item encontrado para este pedido.")
            return

        popup = ttk.Toplevel(self)
        popup.title(f"Itens do Pedido {pedido_id}")
        popup.geometry("500x300")

        tree = ttk.Treeview(
            popup,
            columns=("produto", "quantidade", "preco_unit"),
            show="headings",
            bootstyle="dark",
        )
        tree.pack(fill=BOTH, expand=True, padx=10, pady=10)

        for col, text in zip(
            ("produto", "quantidade", "preco_unit"),
            ["Produto", "Qtd", "Preço Unitário (R$)"],
        ):
            tree.heading(col, text=text)
            tree.column(col, width=150)

        for item in itens:
            _, produto, qtd, preco = item
            tree.insert("", "end", values=(produto, qtd, f"{preco:.2f}"))
