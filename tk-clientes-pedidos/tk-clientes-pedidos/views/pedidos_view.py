import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import tkinter as tk
from tkinter import ttk, messagebox
from db import list_clientes, insert_pedido_with_items, list_pedidos, get_itens_pedido, delete_pedido

class PedidosView(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.pack(fill="both", expand=True)
        self.create_widgets()
        self.load_pedidos()

    def create_widgets(self):
        top = ttk.Frame(self)
        top.pack(fill="x", pady=6, padx=6)
        ttk.Label(top, text="Buscar Cliente:").pack(side="left")
        self.search_var = tk.StringVar()
        ttk.Entry(top, textvariable=self.search_var).pack(side="left", padx=5)
        ttk.Button(top, text="Buscar", command=self.load_pedidos).pack(side="left", padx=5)
        ttk.Button(top, text="Novo Pedido", command=self.on_new).pack(side="right", padx=5)

        columns = ("id","cliente_id","cliente","data","total")
        self.tree = ttk.Treeview(self, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col.title())
        self.tree.column("id", width=40, anchor="center")
        self.tree.pack(fill="both", expand=True, padx=6, pady=6)

        btns = ttk.Frame(self)
        btns.pack(fill="x", padx=6, pady=(0,6))
        ttk.Button(btns, text="Ver Itens", command=self.on_view_items).pack(side="left")
        ttk.Button(btns, text="Excluir", command=self.on_delete).pack(side="left", padx=5)

    def load_pedidos(self):
        for r in self.tree.get_children():
            self.tree.delete(r)
        q = self.search_var.get().strip()
        rows = list_pedidos()
        if q:
            rows = [r for r in rows if q.lower() in r[2].lower()]
        for r in rows:
            self.tree.insert("", "end", values=r)

    def get_selected_id(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Aviso","Selecione um pedido")
            return None
        return int(self.tree.item(sel[0])["values"][0])

    def on_new(self):
        PedidoForm(self, "novo")

    def on_view_items(self):
        pid = self.get_selected_id()
        if pid:
            itens = get_itens_pedido(pid)
            msg = "\n".join([f"{i[1]} | Qtd: {i[2]} | R$: {i[3]:.2f}" for i in itens])
            messagebox.showinfo("Itens do Pedido", msg if msg else "Sem itens")

    def on_delete(self):
        pid = self.get_selected_id()
        if pid and messagebox.askyesno("Confirmar", "Excluir pedido?"):
            delete_pedido(pid)
            self.load_pedidos()

class PedidoForm(tk.Toplevel):
    def __init__(self, parent, modo):
        super().__init__(parent)
        self.parent = parent
        self.modo = modo
        self.title("Novo Pedido")
        self.geometry("400x400")
        self.items = []
        self.create_form()

    def create_form(self):
        pad={"padx":8,"pady":6}
        tk.Label(self, text="Cliente").grid(row=0,column=0,**pad,sticky="w")
        clientes = list_clientes()
        self.clientes_map = {f"{c[1]}": c[0] for c in clientes}
        self.cliente_var = tk.StringVar()
        ttk.Combobox(self, textvariable=self.cliente_var, values=list(self.clientes_map.keys())).grid(row=0,column=1,**pad)

        tk.Label(self, text="Data").grid(row=1,column=0,**pad,sticky="w")
        import datetime
        self.data_var = tk.StringVar(value=datetime.date.today().isoformat())
        tk.Entry(self, textvariable=self.data_var).grid(row=1,column=1,**pad)

        # Tabela de itens
        tk.Label(self, text="Itens").grid(row=2,column=0,sticky="w", **pad)
        self.tree = ttk.Treeview(self, columns=("produto","quantidade","preco"), show="headings")
        for c in ("produto","quantidade","preco"):
            self.tree.heading(c,text=c.title())
        self.tree.grid(row=3,column=0,columnspan=2, padx=6, pady=6)

        btns_itens = tk.Frame(self)
        btns_itens.grid(row=4,column=0,columnspan=2)
        tk.Button(btns_itens,text="Adicionar Item",command=self.add_item).pack(side="left",padx=5)
        tk.Button(btns_itens,text="Remover Item",command=self.remove_item).pack(side="left",padx=5)

        # Total
        tk.Label(self,text="Total").grid(row=5,column=0,sticky="w",**pad)
        self.total_var = tk.StringVar(value="0.00")
        tk.Entry(self,textvariable=self.total_var,state="readonly").grid(row=5,column=1,**pad)

        # Salvar / Cancelar
        frm_btn = tk.Frame(self)
        frm_btn.grid(row=6,column=0,columnspan=2,pady=10)
        tk.Button(frm_btn,text="Salvar",command=self.save).pack(side="left",padx=5)
        tk.Button(frm_btn,text="Cancelar",command=self.destroy).pack(side="left",padx=5)

    def add_item(self):
        def salvar_item():
            p = produto_var.get().strip()
            try:
                q = int(quant_var.get())
                preco = float(preco_var.get())
            except ValueError:
                messagebox.showerror("Erro","Quantidade ou preço inválido")
                return
            self.items.append((p,q,preco))
            self.tree.insert("", "end", values=(p,q,preco))
            self.update_total()
            win.destroy()

        win = tk.Toplevel(self)
        win.title("Adicionar Item")
        tk.Label(win,text="Produto").grid(row=0,column=0,padx=8,pady=6,sticky="w")
        produto_var = tk.StringVar()
        tk.Entry(win,textvariable=produto_var).grid(row=0,column=1,padx=8,pady=6)
        tk.Label(win,text="Quantidade").grid(row=1,column=0,padx=8,pady=6,sticky="w")
        quant_var = tk.StringVar()
        tk.Entry(win,textvariable=quant_var).grid(row=1,column=1,padx=8,pady=6)
        tk.Label(win,text="Preço Unit").grid(row=2,column=0,padx=8,pady=6,sticky="w")
        preco_var = tk.StringVar()
        tk.Entry(win,textvariable=preco_var).grid(row=2,column=1,padx=8,pady=6)
        tk.Button(win,text="Salvar",command=salvar_item).grid(row=3,column=0,columnspan=2,pady=10)

    def remove_item(self):
        sel = self.tree.selection()
        if sel:
            idx = self.tree.index(sel[0])
            del self.items[idx]
            self.tree.delete(sel[0])
            self.update_total()

    def update_total(self):
        total = sum(q*preco for _,q,preco in self.items)
        self.total_var.set(f"{total:.2f}")

    def save(self):
        cliente_nome = self.cliente_var.get().strip()
        if not cliente_nome or not self.items:
            messagebox.showerror("Erro","Cliente e pelo menos 1 item são obrigatórios")
            return
        cliente_id = self.parent.clientes_map[cliente_nome] if hasattr(self.parent,'clientes_map') else None
        if cliente_id is None:
            # Fallback
            clientes = list_clientes()
            cliente_map = {c[1]:c[0] for c in clientes}
            cliente_id = cliente_map.get(cliente_nome)
        insert_pedido_with_items(cliente_id, self.data_var.get(), float(self.total_var.get()), self.items)
        self.parent.load_pedidos()
        self.destroy()
