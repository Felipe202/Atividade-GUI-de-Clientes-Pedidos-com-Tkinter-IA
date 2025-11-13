import tkinter as tk
import ttkbootstrap as ttk
from tkinter import messagebox
from datetime import date
from db import list_clientes, insert_pedido, insert_item_pedido, list_pedidos, list_produtos
import sys, os


# Ajuste do path para importação do db (Se necessário, mantenha esta linha)
# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class PedidosView(ttk.Toplevel):
    # Recebe o callback do dashboard
    def __init__(self, master, dashboard_callback=None):
        super().__init__(master)
        self.title("Gerenciar Pedidos")
        self.geometry("900x600")
        self.resizable(False, False)

        self.dashboard_callback = dashboard_callback  # Salva a função de refresh do Dashboard

        ttk.Label(self, text="Pedidos", font=("Segoe UI", 16, "bold")).pack(pady=10)

        frame_top = ttk.Frame(self, padding=10)
        frame_top.pack(fill="x")

        ttk.Button(frame_top, text="Novo Pedido", bootstyle="success", command=self.novo_pedido).pack(side="left",
                                                                                                      padx=5)
        ttk.Button(frame_top, text="Atualizar Lista", bootstyle="info", command=self.carregar_pedidos).pack(side="left",
                                                                                                            padx=5)
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
        # limpa
        for item in self.tree.get_children():
            self.tree.delete(item)

        # busca dados e insere
        for p in list_pedidos():
            # A tupla do DB é: (id, cliente_id, cliente_nome, data, total)
            if len(p) != 5:
                print(f"Erro: Tupla de pedido inesperada: {p}")
                continue

            try:
                # CORRIGIDO: Usa '_' para IGNORAR o cliente_id (índice 1), garantindo que os campos exibidos estejam corretos.
                pid, _, cliente_str, data_str, total_val = p

                # Formata o total
                total_display = f"R$ {float(total_val):.2f}"

                # Valores a serem inseridos na Treeview
                tree_values = (pid, cliente_str, data_str, total_display)

                # Insere o pedido. Ele será inserido na ordem que foi retornado pelo DB (já ordenado).
                self.tree.insert("", "end", values=tree_values)

            except Exception as e:
                print(f"[ERRO PEDIDOS VIEW] Falha ao processar linha do pedido: {p}. Erro: {e}")

        # Garante que o Treeview está limpo e inserido corretamente se o DB retornou vazio
        if not self.tree.get_children():
            # Apenas insere uma linha informativa se não houver dados, para não deixar a tabela vazia
            pass

    def novo_pedido(self):
        # Passa dois callbacks: para a lista desta janela e para o Dashboard
        PedidoForm(self, self.carregar_pedidos, self.dashboard_callback)


class PedidoForm(ttk.Toplevel):
    # Recebe dois callbacks
    def __init__(self, master, pedidos_callback, dashboard_callback):
        super().__init__(master)
        self.title("Novo Pedido")
        self.geometry("800x600")
        self.callback_pedidos = pedidos_callback
        self.callback_dashboard = dashboard_callback
        self.total = tk.DoubleVar(value=0.0)
        self.itens = []

        # produtos e dicionário nome->(id,preco)
        self.produtos = list_produtos()
        self.produto_dict = {p[1]: (p[0], p[2]) for p in self.produtos}

        # clientes e dicionário nome->id (normaliza)
        clientes = list_clientes()
        self.clientes_dict = {}
        for c in clientes:
            nome = (c[1] or "").strip()
            if nome:
                self.clientes_dict[nome] = c[0]

        # layout
        frame_info = ttk.Frame(self, padding=10)
        frame_info.pack(fill="x")

        ttk.Label(frame_info, text="Cliente:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.combo_cliente = ttk.Combobox(frame_info, values=list(self.clientes_dict.keys()), width=40,
                                          bootstyle="info")
        self.combo_cliente.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(frame_info, text="Data:").grid(row=0, column=2, sticky="w", padx=5, pady=5)
        self.entry_data = ttk.Entry(frame_info, width=15)
        self.entry_data.insert(0, date.today().strftime("%Y-%m-%d"))
        self.entry_data.grid(row=0, column=3, padx=5, pady=5)

        # itens
        frame_itens = ttk.Labelframe(self, text="Itens do Pedido", padding=10, bootstyle="dark")
        frame_itens.pack(fill="both", expand=True, padx=10, pady=10)

        col_itens = ("produto", "quantidade", "preco_unit", "subtotal")
        self.tree_itens = ttk.Treeview(frame_itens, columns=col_itens, show="headings", bootstyle="dark")
        for col in col_itens:
            self.tree_itens.heading(col, text=col.capitalize())
            self.tree_itens.column(col, width=150, anchor="center")

        scroll_itens = ttk.Scrollbar(frame_itens, command=self.tree_itens.yview)
        self.tree_itens.configure(yscrollcommand=scroll_itens.set)
        self.tree_itens.pack(side="left", fill="both", expand=True)
        scroll_itens.pack(side="right", fill="y")

        frame_add = ttk.Frame(self, padding=10)
        frame_add.pack(fill="x")

        ttk.Label(frame_add, text="Produto:").grid(row=0, column=0, padx=5, pady=5)
        self.produto_var = ttk.StringVar()
        self.combo_produto = ttk.Combobox(frame_add, textvariable=self.produto_var, width=30, state="readonly")
        self.combo_produto["values"] = list(self.produto_dict.keys())
        self.combo_produto.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(frame_add, text="Qtd:").grid(row=0, column=2, padx=5, pady=5)
        self.entry_qtd = ttk.Entry(frame_add, width=10)
        self.entry_qtd.grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(frame_add, text="Preço Unit:").grid(row=0, column=4, padx=5, pady=5)
        self.preco_var = ttk.StringVar()
        self.entry_preco = ttk.Entry(frame_add, textvariable=self.preco_var, width=10, state="readonly")
        self.entry_preco.grid(row=0, column=5, padx=5, pady=5)

        def on_produto_selected(event=None):
            nome = self.produto_var.get()
            if nome in self.produto_dict:
                preco = self.produto_dict[nome][1]
                self.preco_var.set(f"{preco:.2f}")

        self.combo_produto.bind("<<ComboboxSelected>>", on_produto_selected)

        ttk.Button(frame_add, text="Adicionar", bootstyle="success", command=self.adicionar_item).grid(row=0, column=6,
                                                                                                       padx=5)
        ttk.Button(frame_add, text="Remover Selecionado", bootstyle="danger", command=self.remover_item).grid(row=0,
                                                                                                              column=7,
                                                                                                              padx=5)

        # CORREÇÃO: Movido para o __init__ para aparecer na abertura
        frame_bottom = ttk.Frame(self, padding=10)
        frame_bottom.pack(fill="x")

        ttk.Label(frame_bottom, text="Total: R$", font=("Segoe UI", 12, "bold")).pack(side="left", padx=5)
        ttk.Label(frame_bottom, textvariable=self.total, font=("Segoe UI", 12, "bold")).pack(side="left")

        ttk.Button(frame_bottom, text="Salvar Pedido", bootstyle="success", command=self.salvar_pedido).pack(
            side="right", padx=5)
        ttk.Button(frame_bottom, text="Cancelar", bootstyle="secondary", command=self.destroy).pack(side="right",
                                                                                                    padx=5)
        # FIM DA CORREÇÃO

    def remover_item(self):
        selecionado = self.tree_itens.selection()
        if not selecionado:
            return
        for s in selecionado:
            self.tree_itens.delete(s)
        self.itens = [self.tree_itens.item(i)["values"][:3] for i in self.tree_itens.get_children()]
        self.atualizar_total()

        # O frame_bottom não é mais criado aqui.
        # Código removido:
        # frame_bottom = ttk.Frame(self, padding=10)
        # frame_bottom.pack(fill="x")
        # ttk.Label(frame_bottom, text="Total: R$", font=("Segoe UI", 12, "bold")).pack(side="left", padx=5)
        # ttk.Label(frame_bottom, textvariable=self.total, font=("Segoe UI", 12, "bold")).pack(side="left")
        # ttk.Button(frame_bottom, text="Salvar Pedido", bootstyle="success", command=self.salvar_pedido).pack(
        #     side="right", padx=5)
        # ttk.Button(frame_bottom, text="Cancelar", bootstyle="secondary", command=self.destroy).pack(side="right",
        #                                                                                             padx=5)

    def adicionar_item(self):
        produto_nome = self.produto_var.get().strip()
        qtd = self.entry_qtd.get().strip()
        preco = self.preco_var.get().strip()
        if not produto_nome or not qtd or not preco:
            messagebox.showwarning("Atenção", "Preencha todos os campos do item.")
            return
        try:
            qtd = float(qtd)
            preco = float(preco)
        except ValueError:
            messagebox.showerror("Erro", "Quantidade e preço devem ser números.")
            return
        subtotal = qtd * preco
        self.tree_itens.insert("", "end", values=(produto_nome, qtd, preco, subtotal))
        # Atualiza self.itens a partir do Treeview para garantir consistência
        self.itens = [self.tree_itens.item(i)["values"][:3] for i in self.tree_itens.get_children()]
        self.atualizar_total()
        self.combo_produto.set("")
        self.entry_qtd.delete(0, "end")
        self.preco_var.set("")

    def atualizar_total(self):
        total = 0.0
        for i in self.tree_itens.get_children():
            valores = self.tree_itens.item(i)["values"]
            # usa o subtotal precalculado (índice 3)
            try:
                total += float(valores[3])
            except Exception:
                try:
                    # fallback: calcula se subtotal não for válido
                    total += float(valores[1]) * float(valores[2])
                except Exception:
                    pass
        self.total.set(round(total, 2))

    def salvar_pedido(self):
        cliente_nome = self.combo_cliente.get().strip()
        data_pedido = self.entry_data.get().strip()

        # INICIALIZA cliente_id
        cliente_id = None

        if not cliente_nome:
            messagebox.showerror("Erro", "Selecione um cliente.")
            return
        if not self.itens:
            messagebox.showwarning("Aviso", "Adicione ao menos um item.")
            return

        # Tenta mapear cliente pelo nome
        cliente_id = self.clientes_dict.get(cliente_nome)

        if cliente_id is None:
            # Tenta buscar o cliente no DB (busca permissiva)
            for c in list_clientes():
                if cliente_nome.lower() == (c[1] or "").lower():  # Busca exata ou menos permissiva
                    cliente_id = c[0]
                    break

        if cliente_id is None:
            messagebox.showerror("Erro", f"Cliente '{cliente_nome}' não encontrado.")
            return

        # Bloco Try/Except correto para salvar no DB e chamar callbacks
        try:
            # 1. SALVA O PEDIDO NO DB
            pedido_id = insert_pedido(cliente_id, data_pedido, self.total.get())
            for produto_nome, qtd, preco in self.itens:
                insert_item_pedido(pedido_id, produto_nome, qtd, preco)

            messagebox.showinfo("Sucesso", "Pedido salvo com sucesso.")

            # 2. ATUALIZA A LISTA NA JANELA ATUAL
            if callable(self.callback_pedidos):
                self.callback_pedidos()

            # 3. ATUALIZA O DASHBOARD PRINCIPAL (LOG DE DIAGNÓSTICO AQUI)
            if callable(self.callback_dashboard):
                print("--- [DIAGNÓSTICO] Chamando self.callback_dashboard() ---")
                self.callback_dashboard()

            self.destroy()

        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao salvar pedido: {e}")