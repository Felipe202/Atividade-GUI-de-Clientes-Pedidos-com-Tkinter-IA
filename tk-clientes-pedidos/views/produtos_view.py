# views/produtos_view.py
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import ttkbootstrap as tb
from tkinter import ttk
from ttkbootstrap.constants import *
from ttkbootstrap.constants import *
from tkinter import messagebox, Toplevel
from db import list_produtos, insert_produto, update_produto, delete_produto, get_produto


class ProdutosView(ttk.Frame):
    def __init__(self, master):
        super().__init__(master, padding=15)
        self.pack(fill=BOTH, expand=True)
        self.create_widgets()
        self.carregar_produtos()

    def create_widgets(self):
        # 🔍 Barra de busca
        frame_busca = ttk.Frame(self)
        frame_busca.pack(fill=X, pady=10)

        ttk.Label(frame_busca, text="Buscar:").pack(side=LEFT, padx=5)
        self.entry_busca = ttk.Entry(frame_busca)
        self.entry_busca.pack(side=LEFT, fill=X, expand=True, padx=5)
        ttk.Button(frame_busca, text="Pesquisar", bootstyle="info", command=self.carregar_produtos).pack(side=LEFT, padx=5)

        # 🧾 Treeview de produtos
        self.tree = ttk.Treeview(self, columns=("id", "nome", "preco", "estoque"), show="headings", bootstyle="dark")
        self.tree.pack(fill=BOTH, expand=True, pady=10)

        self.tree.heading("id", text="ID")
        self.tree.heading("nome", text="Nome")
        self.tree.heading("preco", text="Preço (R$)")
        self.tree.heading("estoque", text="Estoque")

        self.tree.column("id", width=40, anchor=CENTER)
        self.tree.column("nome", width=200)
        self.tree.column("preco", width=100, anchor=E)
        self.tree.column("estoque", width=100, anchor=E)

        # 🧩 Botões de ação
        frame_botoes = ttk.Frame(self)
        frame_botoes.pack(fill=X, pady=10)

        ttk.Button(frame_botoes, text="Novo", bootstyle="success", command=self.novo_produto).pack(side=LEFT, padx=5)
        ttk.Button(frame_botoes, text="Editar", bootstyle="warning", command=self.editar_produto).pack(side=LEFT, padx=5)
        ttk.Button(frame_botoes, text="Excluir", bootstyle="danger", command=self.excluir_produto).pack(side=LEFT, padx=5)

    def carregar_produtos(self):
        filtro = self.entry_busca.get()
        for i in self.tree.get_children():
            self.tree.delete(i)

        produtos = list_produtos(filtro)
        for p in produtos:
            self.tree.insert("", END, values=p)

    def novo_produto(self):
        ProdutoForm(self, self.carregar_produtos)

    def editar_produto(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Aviso", "Selecione um produto para editar.")
            return
        item = self.tree.item(sel[0])
        produto_id = item["values"][0]
        ProdutoForm(self, self.carregar_produtos, produto_id)

    def excluir_produto(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Aviso", "Selecione um produto para excluir.")
            return
        produto_id = self.tree.item(sel[0])["values"][0]
        if messagebox.askyesno("Confirmação", "Deseja realmente excluir este produto?"):
            delete_produto(produto_id)
            self.carregar_produtos()


class ProdutoForm(Toplevel):
    def __init__(self, parent, on_save, produto_id=None):
        super().__init__(parent)
        self.title("Cadastro de Produto")
        self.geometry("400x280")
        self.resizable(False, False)
        self.produto_id = produto_id
        self.on_save = on_save

        self.create_widgets()

        if produto_id:
            self.preencher_dados(produto_id)

    def create_widgets(self):
        frame_form = ttk.Labelframe(self, text="Informações do Produto", padding=15, bootstyle="dark")
        frame_form.pack(fill=BOTH, expand=True, padx=10, pady=10)

        ttk.Label(frame_form, text="Nome:").grid(row=0, column=0, sticky=W, pady=4)
        self.entry_nome = ttk.Entry(frame_form)
        self.entry_nome.grid(row=0, column=1, sticky=EW, pady=4)

        ttk.Label(frame_form, text="Preço (R$):").grid(row=1, column=0, sticky=W, pady=4)
        self.entry_preco = ttk.Entry(frame_form)
        self.entry_preco.grid(row=1, column=1, sticky=EW, pady=4)

        ttk.Label(frame_form, text="Estoque:").grid(row=2, column=0, sticky=W, pady=4)
        self.entry_estoque = ttk.Entry(frame_form)
        self.entry_estoque.grid(row=2, column=1, sticky=EW, pady=4)

        frame_form.columnconfigure(1, weight=1)

        ttk.Button(self, text="Salvar", bootstyle="success", command=self.salvar).pack(pady=10)

    def preencher_dados(self, produto_id):
        produto = get_produto(produto_id)
        if produto:
            self.entry_nome.insert(0, produto[1])
            self.entry_preco.insert(0, produto[2])
            self.entry_estoque.insert(0, produto[3])

    def salvar(self):
        nome = self.entry_nome.get().strip()
        preco = self.entry_preco.get().strip()
        estoque = self.entry_estoque.get().strip()

        if not nome or not preco:
            messagebox.showwarning("Atenção", "Preencha nome e preço.")
            return

        try:
            preco = float(preco)
            estoque = int(estoque) if estoque else 0
        except ValueError:
            messagebox.showerror("Erro", "Preço e estoque devem ser numéricos.")
            return

        if self.produto_id:
            update_produto(self.produto_id, nome, preco, estoque)
        else:
            insert_produto(nome, preco, estoque)

        self.on_save()
        self.destroy()
