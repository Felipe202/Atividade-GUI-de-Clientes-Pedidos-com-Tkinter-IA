import tkinter as tk
import ttkbootstrap as ttk
from tkinter import messagebox
from datetime import date
from db import list_clientes, insert_pedido, insert_item_pedido, list_pedidos, get_itens_pedido


class PedidosView(ttk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Gerenciar Pedidos")
        self.geometry("900x600")
        self.resizable(False, False)

        ttk.Label(self, text="Pedidos", font=("Segoe UI", 16, "bold")).pack(pady=10)

        frame_top = ttk.Frame(self, padding=10)
        frame_top.pack(fill="x")

        ttk.Button(frame_top, text="Novo Pedido", bootstyle="success", command=self.novo_pedido).pack(side="left", padx=5)
        ttk.Button(frame_top, text="Atualizar Lista", bootstyle="info", command=self.carregar_pedidos).pack(side="left", padx=5)
        ttk.Button(frame_top, text="Fechar", bootstyle="secondary", command=self.destroy).pack(side="right", padx=5)

        colunas = ("id", "cliente", "data", "total")
        self.tree = ttk.Treeview(self, columns=colunas, show="headings", bootstyle="dark")
        for col in colunas:
            self.tree.heading(col, text=col.capitalize())
            self.tree.column(col, width=200, anchor="center")

        scroll = ttk.Scrollbar(self, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        self.tree.pack(fill="both", expand=True, pady=10, padx=10)
        scroll.pack(side="right", fill="y")

        self.carregar_pedidos()

    def carregar_pedidos(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for p in list_pedidos():
            self.tree.insert("", "end", values=p)

    def novo_pedido(self):
        PedidoForm(self, self.carregar_pedidos)


class PedidoForm(ttk.Toplevel):
    def __init__(self, master, callback):
        super().__init__(master)
        self.title("Novo Pedido")
        self.geometry("800x600")
        self.callback = callback
        self.total = tk.DoubleVar(value=0.0)
        self.itens = []

        # Cliente + Data
        frame_info = ttk.Frame(self, padding=10)
        frame_info.pack(fill="x")

        ttk.Label(frame_info, text="Cliente:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        clientes = list_clientes()
        self.combo_cliente = ttk.Combobox(frame_info, values=[c[1] for c in clientes], width=40, bootstyle="info")
        self.combo_cliente.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(frame_info, text="Data:").grid(row=0, column=2, sticky="w", padx=5, pady=5)
        self.entry_data = ttk.Entry(frame_info, width=15)
        self.entry_data.insert(0, date.today().strftime("%Y-%m-%d"))
        self.entry_data.grid(row=0, column=3, padx=5, pady=5)

        # Tabela de Itens
        frame_itens = ttk.Labelframe(self, text="Itens do Pedido", padding=10, bootstyle="dark")
        frame_itens.pack(fill="both", expand=True, padx=10, pady=10)

        colunas = ("produto", "quantidade", "preco_unit", "subtotal")
        self.tree_itens = ttk.Treeview(frame_itens, columns=colunas, show="headings", bootstyle="dark")
        for col in colunas:
            self.tree_itens.heading(col, text=col.capitalize())
            self.tree_itens.column(col, width=150, anchor="center")

        scroll_itens = ttk.Scrollbar(frame_itens, command=self.tree_itens.yview)
        self.tree_itens.configure(yscrollcommand=scroll_itens.set)
        self.tree_itens.pack(side="left", fill="both", expand=True)
        scroll_itens.pack(side="right", fill="y")

        # Form de item
        frame_add = ttk.Frame(self, padding=10)
        frame_add.pack(fill="x")

        ttk.Label(frame_add, text="Produto:").grid(row=0, column=0, padx=5, pady=5)
        self.entry_produto = ttk.Entry(frame_add, width=30)
        self.entry_produto.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(frame_add, text="Qtd:").grid(row=0, column=2, padx=5, pady=5)
        self.entry_qtd = ttk.Entry(frame_add, width=10)
        self.entry_qtd.grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(frame_add, text="Preço Unit:").grid(row=0, column=4, padx=5, pady=5)
        self.entry_preco = ttk.Entry(frame_add, width=10)
        self.entry_preco.grid(row=0, column=5, padx=5, pady=5)

        ttk.Button(frame_add, text="Adicionar", bootstyle="success", command=self.adicionar_item).grid(row=0, column=6, padx=5)
        ttk.Button(frame_add, text="Remover Selecionado", bootstyle="danger", command=self.remover_item).grid(row=0, column=7, padx=5)

        # Total + Botões
        frame_bottom = ttk.Frame(self, padding=10)
        frame_bottom.pack(fill="x")

        ttk.Label(frame_bottom, text="Total: R$", font=("Segoe UI", 12, "bold")).pack(side="left", padx=5)
        ttk.Label(frame_bottom, textvariable=self.total, font=("Segoe UI", 12, "bold")).pack(side="left")

        ttk.Button(frame_bottom, text="Salvar Pedido", bootstyle="success", command=self.salvar_pedido).pack(side="right", padx=5)
        ttk.Button(frame_bottom, text="Cancelar", bootstyle="secondary", command=self.destroy).pack(side="right", padx=5)

    def adicionar_item(self):
        produto = self.entry_produto.get().strip()
        qtd = self.entry_qtd.get().strip()
        preco = self.entry_preco.get().strip()

        if not produto or not qtd or not preco:
            messagebox.showwarning("Atenção", "Preencha todos os campos do item.")
            return

        try:
            qtd = float(qtd)
            preco = float(preco)
        except ValueError:
            messagebox.showerror("Erro", "Quantidade e preço devem ser números.")
            return

        subtotal = qtd * preco
        self.tree_itens.insert("", "end", values=(produto, qtd, preco, subtotal))
        self.itens.append((produto, qtd, preco))
        self.atualizar_total()

        self.entry_produto.delete(0, "end")
        self.entry_qtd.delete(0, "end")
        self.entry_preco.delete(0, "end")

    def remover_item(self):
        selecionado = self.tree_itens.selection()
        if not selecionado:
            return
        for s in selecionado:
            self.tree_itens.delete(s)
        self.itens = [self.tree_itens.item(i)["values"][:3] for i in self.tree_itens.get_children()]
        self.atualizar_total()

    def atualizar_total(self):
        total = 0.0
        for i in self.tree_itens.get_children():
            valores = self.tree_itens.item(i)["values"]
            total += float(valores[3])
        self.total.set(round(total, 2))

    def salvar_pedido(self):
        cliente_nome = self.combo_cliente.get().strip()
        data_pedido = self.entry_data.get().strip()

        if not cliente_nome:
            messagebox.showerror("Erro", "Selecione um cliente.")
            return
        if not self.itens:
            messagebox.showwarning("Aviso", "Adicione ao menos um item.")
            return

        try:
            pedido_id = insert_pedido(cliente_nome, data_pedido, self.total.get())
            for produto, qtd, preco in self.itens:
                insert_item_pedido(pedido_id, produto, qtd, preco)
            messagebox.showinfo("Sucesso", "Pedido salvo com sucesso.")
            self.callback()
            self.destroy()
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao salvar pedido: {e}")
