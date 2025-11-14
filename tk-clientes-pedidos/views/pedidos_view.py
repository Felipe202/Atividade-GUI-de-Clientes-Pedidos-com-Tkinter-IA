import tkinter as tk
import ttkbootstrap as ttk
from tkinter import messagebox
from datetime import date
# Presumindo que 'db' está no caminho
from db import list_clientes, insert_pedido, insert_item_pedido, list_pedidos, list_produtos, delete_pedido
import sys, os


# PedidosView agora herda de ttk.Toplevel para abrir como uma janela
class PedidosView(ttk.Toplevel):
    VIEW_TITLE = "Pedidos"

    def __init__(self, master, dashboard_callback=None):
        # Inicializa como uma nova janela Toplevel
        super().__init__(master)
        self.title(self.VIEW_TITLE)
        self.geometry("850x550")
        self.transient(master)  # Mantém a janela vinculada à principal

        self.dashboard_callback = dashboard_callback

        # Título da View
        ttk.Label(self, text="Gerenciamento de Pedidos", font=("Segoe UI", 18, "bold")).pack(pady=10)

        # Frame para botões
        frame_top = ttk.Frame(self, padding=(0, 10))
        frame_top.pack(fill="x")

        ttk.Button(frame_top, text="Novo Pedido", bootstyle="success", command=self.novo_pedido).pack(side="left",
                                                                                                      padx=5)
        ttk.Button(frame_top, text="Remover Pedido", bootstyle="danger", command=self.remover_pedido).pack(side="left",
                                                                                                           padx=5)  # NOVO BOTÃO
        ttk.Button(frame_top, text="Atualizar Lista", bootstyle="info", command=self.carregar_pedidos).pack(side="left",
                                                                                                            padx=5)

        # Treeview para listar pedidos
        colunas = ("id", "cliente", "data", "total")
        self.tree = ttk.Treeview(self, columns=colunas, show="headings", bootstyle="dark")

        # Configuração das colunas
        self.tree.heading("id", text="ID", anchor="center")
        self.tree.column("id", width=50, anchor="center")
        self.tree.heading("cliente", text="Cliente")
        self.tree.column("cliente", width=350, anchor="w")
        self.tree.heading("data", text="Data")
        self.tree.column("data", width=150, anchor="center")
        self.tree.heading("total", text="Total")
        self.tree.column("total", width=150, anchor="e")

        # Scrollbar
        scroll = ttk.Scrollbar(self, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)

        # Empacotamento
        self.tree.pack(side="left", fill="both", expand=True, pady=10, padx=(0, 5))
        scroll.pack(side="right", fill="y", pady=10, padx=(0, 0))

        # Carrega os dados na inicialização
        self.carregar_pedidos()

        # Garante que a nova janela seja focada
        self.grab_set()

    def carregar_pedidos(self):
        # limpa treeview
        for item in self.tree.get_children():
            self.tree.delete(item)

        # busca dados e insere
        try:
            for p in list_pedidos():
                if len(p) != 5:
                    print(f"Aviso: Tupla de pedido inesperada: {p}")
                    continue

                pid, _, cliente_str, data_str, total_val = p

                total_display = f"R$ {float(total_val):.2f}"

                tree_values = (pid, cliente_str, data_str, total_display)
                self.tree.insert("", "end", values=tree_values)

        except Exception as e:
            messagebox.showerror("Erro de BD", f"Falha ao carregar pedidos: {e}")

    def remover_pedido(self):
        # Obtém o item selecionado
        selecionado = self.tree.focus()
        if not selecionado:
            messagebox.showwarning("Aviso", "Selecione um pedido na lista para remover.")
            return

        # Obtém o ID do pedido
        valores = self.tree.item(selecionado, 'values')
        if not valores:
            messagebox.showwarning("Erro", "Não foi possível obter os dados do pedido selecionado.")
            return

        pedido_id = valores[0]

        # Pede confirmação
        confirmar = messagebox.askyesno(
            "Confirmar Remoção",
            f"Tem certeza que deseja remover o Pedido ID: {pedido_id}? Esta ação não pode ser desfeita."
        )

        if confirmar:
            try:
                # Chama a função de exclusão no BD
                # OBS: Presume a existência da função delete_pedido no db.py
                delete_pedido(pedido_id)

                messagebox.showinfo("Sucesso", f"Pedido ID: {pedido_id} removido com sucesso.")
                self.carregar_pedidos()  # Recarrega a lista

                if callable(self.dashboard_callback):
                    self.dashboard_callback()  # Atualiza o dashboard, se houver

            except Exception as e:
                messagebox.showerror("Erro de BD", f"Falha ao remover o pedido: {e}")

    def novo_pedido(self):
        # Passa o 'self' (PedidosView Toplevel) como master para o PedidoForm
        PedidoForm(self, self.carregar_pedidos, self.dashboard_callback)

    def destroy(self):
        # Garante que o bloqueio seja liberado ao fechar
        self.grab_release()
        super().destroy()


class PedidoForm(ttk.Toplevel):
    # Recebe dois callbacks
    def __init__(self, master, pedidos_callback, dashboard_callback):
        # O master aqui é a PedidosView (o Toplevel)
        super().__init__(master)
        self.title("Novo Pedido")
        self.geometry("850x650")
        self.transient(master)
        self.grab_set()

        self.callback_pedidos = pedidos_callback
        self.callback_dashboard = dashboard_callback
        self.total = tk.DoubleVar(value=0.0)
        self.itens = []

        # --- DADOS INICIAIS (para Autocomplete) ---
        self.produtos = list_produtos()
        self.produto_dict = {p[1]: (p[0], p[2]) for p in self.produtos}
        self._todos_produtos_nomes = sorted(list(self.produto_dict.keys()))

        clientes = list_clientes()
        self.clientes_dict = {}
        for c in clientes:
            nome = (c[1] or "").strip()
            if nome:
                self.clientes_dict[nome] = c[0]
        self._todos_clientes_nomes = sorted(list(self.clientes_dict.keys()))

        # --- LAYOUT PRINCIPAL ---
        frame_info = ttk.Frame(self, padding=10)
        frame_info.pack(fill="x")

        # Cliente (Combobox com Autocomplete)
        ttk.Label(frame_info, text="Cliente:", width=10).grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.cliente_var = ttk.StringVar()
        self.combo_cliente = ttk.Combobox(frame_info, textvariable=self.cliente_var, width=40, bootstyle="info",
                                          values=self._todos_clientes_nomes)
        self.combo_cliente.grid(row=0, column=1, padx=5, pady=5)
        # Evento KeyRelease para filtrar
        self.combo_cliente.bind("<KeyRelease>", self._filtrar_clientes)

        # Data
        ttk.Label(frame_info, text="Data:").grid(row=0, column=2, sticky="w", padx=15, pady=5)
        self.entry_data = ttk.Entry(frame_info, width=15)
        self.entry_data.insert(0, date.today().strftime("%Y-%m-%d"))
        self.entry_data.grid(row=0, column=3, padx=5, pady=5)

        # --- ITENS DO PEDIDO (Treeview) ---
        frame_itens = ttk.Labelframe(self, text="Itens do Pedido", padding=10, bootstyle="dark")
        frame_itens.pack(fill="both", expand=True, padx=10, pady=10)

        col_itens = ("produto", "quantidade", "preco_unit", "subtotal")
        self.tree_itens = ttk.Treeview(frame_itens, columns=col_itens, show="headings", bootstyle="dark")
        self.tree_itens.heading("produto", text="Produto")
        self.tree_itens.column("produto", width=300, anchor="w")
        self.tree_itens.heading("quantidade", text="Qtd")
        self.tree_itens.column("quantidade", width=80, anchor="center")
        self.tree_itens.heading("preco_unit", text="Preço Unit (R$)")
        self.tree_itens.column("preco_unit", width=120, anchor="e")
        self.tree_itens.heading("subtotal", text="Subtotal (R$)")
        self.tree_itens.column("subtotal", width=120, anchor="e")

        scroll_itens = ttk.Scrollbar(frame_itens, command=self.tree_itens.yview)
        self.tree_itens.configure(yscrollcommand=scroll_itens.set)
        self.tree_itens.pack(side="left", fill="both", expand=True)
        scroll_itens.pack(side="right", fill="y")

        # --- ADICIONAR ITEM ---
        frame_add = ttk.Frame(self, padding=10)
        frame_add.pack(fill="x")

        ttk.Label(frame_add, text="Produto:").grid(row=0, column=0, padx=5, pady=5)
        self.produto_var = ttk.StringVar()
        self.combo_produto = ttk.Combobox(frame_add, textvariable=self.produto_var, width=30,
                                          values=self._todos_produtos_nomes)
        self.combo_produto.grid(row=0, column=1, padx=5, pady=5)
        # Evento KeyRelease para filtrar
        self.combo_produto.bind("<KeyRelease>", self._filtrar_produtos)
        self.combo_produto.bind("<<ComboboxSelected>>", self._on_produto_selected)

        ttk.Label(frame_add, text="Qtd:").grid(row=0, column=2, padx=5, pady=5)
        self.entry_qtd = ttk.Entry(frame_add, width=10)
        self.entry_qtd.grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(frame_add, text="Preço Unit:").grid(row=0, column=4, padx=5, pady=5)
        self.preco_var = ttk.StringVar()
        self.entry_preco = ttk.Entry(frame_add, textvariable=self.preco_var, width=10, state="readonly")
        self.entry_preco.grid(row=0, column=5, padx=5, pady=5)

        ttk.Button(frame_add, text="Adicionar", bootstyle="success", command=self.adicionar_item).grid(row=0, column=6,
                                                                                                       padx=5)
        ttk.Button(frame_add, text="Remover", bootstyle="danger", command=self.remover_item).grid(row=0, column=7,
                                                                                                  padx=5)

        # --- RODAPÉ (Total e Salvar) ---
        frame_bottom = ttk.Frame(self, padding=10)
        frame_bottom.pack(fill="x")

        ttk.Label(frame_bottom, text="Total: R$", font=("Segoe UI", 14, "bold"), bootstyle="primary").pack(side="left",
                                                                                                           padx=5)
        ttk.Label(frame_bottom, textvariable=self.total, font=("Segoe UI", 14, "bold"), bootstyle="primary").pack(
            side="left")

        ttk.Button(frame_bottom, text="Salvar Pedido", bootstyle="success", command=self.salvar_pedido).pack(
            side="right", padx=5)
        ttk.Button(frame_bottom, text="Cancelar", bootstyle="secondary", command=self.destroy).pack(side="right",
                                                                                                    padx=5)

        self.combo_cliente.focus_set()

    # --- LÓGICA DE AUTOCOMPLETAR ---
    def _abrir_dropdown_cliente(self):
        """Abre o dropdown do Combobox do cliente de forma não-bloqueante."""
        self.combo_cliente.event_generate('<Down>')
        # Garante que o texto digitado permaneça no campo
        self.combo_cliente.set(self.cliente_var.get())

    def _filtrar_clientes(self, event=None):
        texto_digitado = self.cliente_var.get().strip().lower()

        # Se não houver texto, volta a lista completa
        if not texto_digitado:
            self.combo_cliente['values'] = self._todos_clientes_nomes
            return

        # Filtra a lista
        sugestoes = [nome for nome in self._todos_clientes_nomes
                     if texto_digitado in nome.lower()]

        self.combo_cliente['values'] = sugestoes

        # Se houver sugestões, agenda a abertura do dropdown com um pequeno atraso (50ms).
        # Isso permite que a digitação termine antes de forçar a abertura, evitando o bug de interrupção.
        if len(sugestoes) > 0:
            self.after(50, self._abrir_dropdown_cliente)

    def _abrir_dropdown_produto(self):
        """Abre o dropdown do Combobox do produto de forma não-bloqueante."""
        self.combo_produto.event_generate('<Down>')
        # Garante que o texto digitado permaneça no campo
        self.combo_produto.set(self.produto_var.get())

    def _filtrar_produtos(self, event=None):
        texto_digitado = self.produto_var.get().strip().lower()

        # Se não houver texto, volta a lista completa
        if not texto_digitado:
            self.combo_produto['values'] = self._todos_produtos_nomes
            return

        # Filtra a lista
        sugestoes = [nome for nome in self._todos_produtos_nomes
                     if texto_digitado in nome.lower()]

        self.combo_produto['values'] = sugestoes

        # Agenda a abertura do dropdown
        if len(sugestoes) > 0:
            self.after(50, self._abrir_dropdown_produto)

        # Garante que o texto digitado permaneça no campo
        self.combo_produto.set(self.produto_var.get())

        if event and event.keysym == 'Return':
            self._on_produto_selected()

    def _on_produto_selected(self, event=None):
        nome = self.produto_var.get()
        if nome in self.produto_dict:
            preco = self.produto_dict[nome][1]
            self.preco_var.set(f"{preco:.2f}")
        else:
            self.preco_var.set("")

            # --- LÓGICA DE ITENS ---

    def remover_item(self):
        selecionado = self.tree_itens.selection()
        if not selecionado:
            messagebox.showwarning("Atenção", "Selecione um item para remover.")
            return

        for s in selecionado:
            self.tree_itens.delete(s)

        self.itens = [self.tree_itens.item(i)["values"][:3] for i in self.tree_itens.get_children()]
        self.atualizar_total()

    def adicionar_item(self):
        produto_nome = self.produto_var.get().strip()
        qtd_str = self.entry_qtd.get().strip()
        preco_str = self.preco_var.get().strip()

        if not produto_nome or not qtd_str or not preco_str:
            messagebox.showwarning("Atenção", "Preencha todos os campos do item.")
            return

        if produto_nome not in self.produto_dict:
            messagebox.showerror("Erro", f"Produto '{produto_nome}' não é válido.")
            return

        try:
            qtd = float(qtd_str.replace(',', '.'))
            preco = float(preco_str.replace(',', '.'))
            if qtd <= 0:
                messagebox.showerror("Erro", "A quantidade deve ser maior que zero.")
                return
        except ValueError:
            messagebox.showerror("Erro", "Quantidade e preço devem ser números válidos.")
            return

        subtotal = round(qtd * preco, 2)

        self.tree_itens.insert("", "end", values=(produto_nome, qtd, preco, subtotal))
        self.itens = [self.tree_itens.item(i)["values"][:3] for i in self.tree_itens.get_children()]

        self.atualizar_total()

        self.combo_produto.set("")
        self.entry_qtd.delete(0, "end")
        self.preco_var.set("")
        self.combo_produto.focus_set()
        self.combo_produto['values'] = self._todos_produtos_nomes

    def atualizar_total(self):
        total = 0.0
        for i in self.tree_itens.get_children():
            valores = self.tree_itens.item(i)["values"]
            try:
                total += float(valores[3])
            except Exception:
                try:
                    total += float(valores[1]) * float(valores[2])
                except Exception:
                    pass
        self.total.set(round(total, 2))

    # --- LÓGICA DE SALVAR ---

    def salvar_pedido(self):
        cliente_nome = self.cliente_var.get().strip()
        data_pedido = self.entry_data.get().strip()

        if not cliente_nome:
            messagebox.showerror("Erro", "O campo Cliente não pode estar vazio.")
            return
        if not self.itens:
            messagebox.showwarning("Aviso", "Adicione ao menos um item ao pedido.")
            return

        cliente_id = self.clientes_dict.get(cliente_nome)

        if cliente_id is None:
            messagebox.showerror("Erro", f"Cliente '{cliente_nome}' não encontrado na lista de clientes válidos.")
            return

        try:
            pedido_id = insert_pedido(cliente_id, data_pedido, self.total.get())

            for produto_nome, qtd, preco in self.itens:
                produto_info = self.produto_dict.get(produto_nome)
                if not produto_info:
                    print(f"Produto ID não encontrado para: {produto_nome}. Pulando item.")
                    continue

                produto_id = produto_info[0]

                insert_item_pedido(pedido_id, produto_id, qtd, preco)

            messagebox.showinfo("Sucesso", f"Pedido #{pedido_id} salvo com sucesso.")

            if callable(self.callback_pedidos):
                self.callback_pedidos()

            if callable(self.callback_dashboard):
                self.callback_dashboard()

            self.destroy()

        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao salvar pedido: {e}")

    def destroy(self):
        self.grab_release()
        super().destroy()