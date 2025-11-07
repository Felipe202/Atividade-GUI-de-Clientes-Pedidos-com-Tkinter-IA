import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import tkinter as tk
from tkinter import ttk, messagebox
from db import list_clientes, insert_cliente, update_cliente, delete_cliente

class ClientesView(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.pack(fill="both", expand=True)
        self.create_widgets()
        self.load_clientes()

    def create_widgets(self):
        top = ttk.Frame(self)
        top.pack(fill="x", pady=6, padx=6)
        ttk.Label(top, text="Buscar:").pack(side="left")
        self.search_var = tk.StringVar()
        ttk.Entry(top, textvariable=self.search_var).pack(side="left", padx=5)
        ttk.Button(top, text="Buscar", command=self.load_clientes).pack(side="left", padx=5)
        ttk.Button(top, text="Novo", command=self.on_new).pack(side="right", padx=5)

        columns = ("id","nome","email","telefone")
        self.tree = ttk.Treeview(self, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col.title())
        self.tree.column("id", width=40, anchor="center")
        self.tree.pack(fill="both", expand=True, padx=6, pady=6)

        btns = ttk.Frame(self)
        btns.pack(fill="x", padx=6, pady=(0,6))
        ttk.Button(btns, text="Editar", command=self.on_edit).pack(side="left")
        ttk.Button(btns, text="Excluir", command=self.on_delete).pack(side="left", padx=5)

    def load_clientes(self):
        for r in self.tree.get_children():
            self.tree.delete(r)
        q = self.search_var.get().strip()
        rows = list_clientes(q)
        for r in rows:
            self.tree.insert("", "end", values=r)

    def get_selected_id(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Aviso","Selecione um cliente")
            return None
        return int(self.tree.item(sel[0])["values"][0])

    def on_new(self):
        ClienteForm(self, "novo")

    def on_edit(self):
        cid = self.get_selected_id()
        if cid:
            ClienteForm(self, "editar", cid)

    def on_delete(self):
        cid = self.get_selected_id()
        if cid and messagebox.askyesno("Confirmar", "Excluir cliente?"):
            delete_cliente(cid)
            self.load_clientes()

class ClienteForm(tk.Toplevel):
    def __init__(self, parent, modo, cliente_id=None):
        super().__init__(parent)
        self.parent = parent
        self.modo = modo
        self.cliente_id = cliente_id
        self.title("Cliente")
        self.geometry("300x200")
        self.create_form()
        if modo=="editar":
            self.load_data()

    def create_form(self):
        pad={"padx":8,"pady":6}
        tk.Label(self, text="Nome").grid(row=0,column=0,**pad,sticky="w")
        self.nome_var = tk.StringVar()
        tk.Entry(self,textvariable=self.nome_var).grid(row=0,column=1,**pad)
        tk.Label(self, text="Email").grid(row=1,column=0,**pad,sticky="w")
        self.email_var = tk.StringVar()
        tk.Entry(self,textvariable=self.email_var).grid(row=1,column=1,**pad)
        tk.Label(self, text="Telefone").grid(row=2,column=0,**pad,sticky="w")
        self.telefone_var = tk.StringVar()
        tk.Entry(self,textvariable=self.telefone_var).grid(row=2,column=1,**pad)
        frm_btn = tk.Frame(self)
        frm_btn.grid(row=3,column=0,columnspan=2,pady=10)
        tk.Button(frm_btn,text="Salvar",command=self.save).pack(side="left",padx=5)
        tk.Button(frm_btn,text="Cancelar",command=self.destroy).pack(side="left",padx=5)

    def load_data(self):
        clientes = list_clientes()
        c = [x for x in clientes if x[0]==self.cliente_id]
        if c:
            self.nome_var.set(c[0][1])
            self.email_var.set(c[0][2])
            self.telefone_var.set(c[0][3])

    def save(self):
        nome = self.nome_var.get().strip()
        email = self.email_var.get().strip()
        telefone = self.telefone_var.get().strip()
        if not nome:
            messagebox.showerror("Erro","Nome obrigatório")
            return
        if self.modo=="novo":
            insert_cliente(nome,email,telefone)
        else:
            update_cliente(self.cliente_id,nome,email,telefone)
        self.parent.load_clientes()
        self.destroy()
