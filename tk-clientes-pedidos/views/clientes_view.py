import tkinter as tk
import ttkbootstrap as ttk
from tkinter import messagebox
from db import list_clientes, insert_cliente, update_cliente, delete_cliente




class ClientesView(ttk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Gerenciar Clientes")
        self.geometry("700x500")
        self.resizable(False, False)

        ttk.Label(self, text="Clientes", font=("Segoe UI", 16, "bold")).pack(pady=10)

        # Frame de busca
        frame_busca = ttk.Frame(self, padding=10)
        frame_busca.pack(fill="x")

        ttk.Label(frame_busca, text="Buscar:").pack(side="left", padx=5)
        self.entry_busca = ttk.Entry(frame_busca, width=40)
        self.entry_busca.pack(side="left", padx=5)
        ttk.Button(frame_busca, text="Pesquisar", bootstyle="info", command=self.buscar_clientes).pack(side="left", padx=5)

        # Treeview
        colunas = ("id", "nome", "email", "telefone")
        self.tree = ttk.Treeview(self, columns=colunas, show="headings", bootstyle="dark")
        for col in colunas:
            self.tree.heading(col, text=col.capitalize())
            self.tree.column(col, width=150, anchor="center")

        scroll = ttk.Scrollbar(self, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        self.tree.pack(fill="both", expand=True, pady=10, padx=10)
        scroll.pack(side="right", fill="y")

        # Botões
        frame_btns = ttk.Frame(self)
        frame_btns.pack(pady=10)
        ttk.Button(frame_btns, text="Novo", bootstyle="success", command=self.novo_cliente).pack(side="left", padx=5)
        ttk.Button(frame_btns, text="Editar", bootstyle="warning", command=self.editar_cliente).pack(side="left", padx=5)
        ttk.Button(frame_btns, text="Excluir", bootstyle="danger", command=self.excluir_cliente).pack(side="left", padx=5)
        ttk.Button(frame_btns, text="Fechar", bootstyle="secondary", command=self.destroy).pack(side="left", padx=5)

        self.carregar_clientes()

    def carregar_clientes(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for c in list_clientes():
            self.tree.insert("", "end", values=c)

    def buscar_clientes(self):
        termo = self.entry_busca.get().lower()
        for item in self.tree.get_children():
            self.tree.delete(item)
        for c in list_clientes():
            if termo in c[1].lower() or termo in c[2].lower():
                self.tree.insert("", "end", values=c)

    def novo_cliente(self):
        ClienteForm(self, "novo", self.carregar_clientes)

    def editar_cliente(self):
        selecionado = self.tree.selection()
        if not selecionado:
            messagebox.showwarning("Aviso", "Selecione um cliente.")
            return
        cliente_id = self.tree.item(selecionado)["values"][0]
        ClienteForm(self, "editar", self.carregar_clientes, cliente_id)

    def excluir_cliente(self):
        selecionado = self.tree.selection()
        if not selecionado:
            messagebox.showwarning("Aviso", "Selecione um cliente.")
            return
        cliente_id = self.tree.item(selecionado)["values"][0]
        if messagebox.askyesno("Confirmar", "Deseja excluir este cliente?"):
            delete_cliente(cliente_id)
            self.carregar_clientes()


class ClienteForm(ttk.Toplevel):
    def __init__(self, master, modo, callback, cliente_id=None):
        super().__init__(master)
        self.title("Cadastro de Cliente")
        self.geometry("400x300")
        self.callback = callback
        self.modo = modo
        self.cliente_id = cliente_id

        ttk.Label(self, text="Nome:").pack(pady=5)
        self.nome = ttk.Entry(self, width=40)
        self.nome.pack()

        ttk.Label(self, text="Email:").pack(pady=5)
        self.email = ttk.Entry(self, width=40)
        self.email.pack()

        ttk.Label(self, text="Telefone:").pack(pady=5)
        self.telefone = ttk.Entry(self, width=40)
        self.telefone.pack()

        frame_btns = ttk.Frame(self)
        frame_btns.pack(pady=15)
        ttk.Button(frame_btns, text="Salvar", bootstyle="success", command=self.salvar).pack(side="left", padx=5)
        ttk.Button(frame_btns, text="Cancelar", bootstyle="secondary", command=self.destroy).pack(side="left", padx=5)

        if modo == "editar" and cliente_id:
            cliente = get_cliente(cliente_id)
            if cliente:
                self.nome.insert(0, cliente[1])
                self.email.insert(0, cliente[2])
                self.telefone.insert(0, cliente[3])

    def salvar(self):
        nome, email, tel = self.nome.get(), self.email.get(), self.telefone.get()
        if not nome:
            messagebox.showerror("Erro", "Nome é obrigatório.")
            return
        if self.modo == "novo":
            insert_cliente(nome, email, tel)
        else:
            update_cliente(self.cliente_id, nome, email, tel)
        self.callback()
        self.destroy()
