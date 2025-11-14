import sys, os, csv

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox, filedialog
# Importa a nova função de detalhe
from db import list_clientes, list_produtos, list_pedidos, get_pedidos_detalhados
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


class ReportsView(ttk.Frame):
    def __init__(self, master):
        super().__init__(master, padding=20)
        self.pack(fill=BOTH, expand=True)
        self.dados_detalhados = []
        # Referência ao style para obter cores dinâmicas
        self.style = ttk.Style()

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
        ttk.Button(frame_top, text="Exportar CSV", bootstyle="success-outline", command=self.exportar_csv).pack(
            side=LEFT, padx=(10, 0))
        ttk.Button(frame_top, text="Exportar PDF", bootstyle="danger-outline", command=self.exportar_pdf).pack(
            side=LEFT, padx=(10, 0))

        # Treeview para mostrar os dados
        self.tree = ttk.Treeview(self, show="headings", bootstyle="dark", height=18)
        self.tree.pack(fill=BOTH, expand=True, pady=(15, 0))

        # Inicializa com o relatório de Clientes e configura o observador de tema
        self.gerar_relatorio()

        # Monitora a mudança de tema para atualizar as cores
        self.bind("<<ThemeChanged>>", self._on_theme_changed)

    def _on_theme_changed(self, event=None):
        """Atualiza as cores das tags do Treeview quando o tema muda."""
        if self.combo_tipo.get() == "Pedidos":
            # Cores dinâmicas
            fundo_padrao = self.style.lookup('TFrame', 'background')
            fundo_destaque = self.style.lookup('info.TLabel', 'background')

            # Reconfigura as tags com as novas cores do tema
            self.tree.tag_configure('pedido_header',
                                    font=('Segoe UI', 10, 'bold'),
                                    background=fundo_destaque,
                                    foreground=self.style.lookup('info.TLabel', 'foreground'))
            self.tree.tag_configure('item_detail',
                                    font=('Segoe UI', 9),
                                    background=fundo_padrao,
                                    foreground=self.style.lookup('Treeview', 'foreground'))
        # Garante que o Treeview seja re-desenhado para aplicar o novo estilo
        self.tree.update_idletasks()

    def gerar_relatorio(self):
        tipo = self.combo_tipo.get()
        # Limpa o Treeview e a variável de dados detalhados
        for i in self.tree.get_children():
            self.tree.delete(i)
        self.dados_detalhados = []

        dados_para_exibir = []

        if tipo == "Clientes":
            self.tree["columns"] = ("id", "nome", "email", "telefone")
            dados_para_exibir = list_clientes()

        elif tipo == "Produtos":
            self.tree["columns"] = ("id", "nome", "preco", "estoque")
            dados_para_exibir = list_produtos()

        else:  # Pedidos - AGORA DETALHADO
            # Novas colunas para exibir o detalhe
            self.tree["columns"] = (
            "pedido_id", "cliente", "data", "produto", "quantidade", "preco_unit", "subtotal", "total_pedido")

            # Usa a nova função que traz os detalhes do item
            self.dados_detalhados = get_pedidos_detalhados()

            # Chama a configuração de tema antes de inserir os dados
            self._on_theme_changed()

            for pedido in self.dados_detalhados:
                # Insere a linha do cabeçalho do pedido (com os itens vazios)

                # Formata o total do pedido para exibição
                total_formatado = f"R$ {float(pedido['total']):.2f}"

                # Linha de resumo do pedido (apenas campos principais preenchidos)
                pedido_row = (
                    pedido['id'],
                    pedido['cliente_nome'],
                    pedido['data'],
                    "",  # Produto
                    "",  # Quantidade
                    "",  # Preco Unit
                    "",  # Subtotal
                    total_formatado
                )
                # Adiciona o cabeçalho do pedido
                self.tree.insert("", "end", values=pedido_row, tags=("pedido_header",))

                # Adiciona os itens do pedido (campos principais vazios)
                for item in pedido['itens']:
                    item_row = (
                        "",  # Pedido ID
                        "",  # Cliente
                        "",  # Data
                        item['produto'],
                        item['quantidade'],
                        f"R$ {float(item['preco_unit']):.2f}",
                        f"R$ {float(item['subtotal']):.2f}",
                        ""  # Total Pedido
                    )
                    self.tree.insert("", "end", values=item_row, tags=("item_detail",))

        # Configura as colunas (se não for pedidos, usa a lógica antiga)
        if tipo != "Pedidos":
            for col in self.tree["columns"]:
                self.tree.heading(col, text=col.capitalize())
                self.tree.column(col, width=150, anchor="center")

            # Insere os dados processados para Clientes e Produtos
            for row in dados_para_exibir:
                self.tree.insert("", "end", values=row)
        else:
            # Configurações específicas para o relatório de Pedidos Detalhado
            self.tree.heading("pedido_id", text="Pedido ID")
            self.tree.heading("cliente", text="Cliente")
            self.tree.heading("data", text="Data")
            self.tree.heading("produto", text="Produto")
            self.tree.heading("quantidade", text="Qtd")
            self.tree.heading("preco_unit", text="Preço Unit.")
            self.tree.heading("subtotal", text="Subtotal")
            self.tree.heading("total_pedido", text="Total")

            self.tree.column("pedido_id", width=50, anchor="center")
            self.tree.column("cliente", width=120)
            self.tree.column("data", width=80, anchor="center")
            self.tree.column("produto", width=150)
            self.tree.column("quantidade", width=50, anchor="center")
            self.tree.column("preco_unit", width=80, anchor="center")
            self.tree.column("subtotal", width=80, anchor="center")
            self.tree.column("total_pedido", width=80, anchor="center")

        messagebox.showinfo("Relatório", f"Relatório de {tipo.lower()} gerado com sucesso!")

    def exportar_csv(self):
        tipo = self.combo_tipo.get()
        if tipo == "Pedidos":
            # Para CSV de Pedidos, vamos exportar o detalhe linha por linha
            colunas = (
            "ID Pedido", "Cliente", "Data", "Produto", "Quantidade", "Preço Unit.", "Subtotal", "Total Pedido")
            dados = []
            if not self.dados_detalhados:
                messagebox.showwarning("Aviso", "Gere um relatório antes de exportar.")
                return

            for pedido in self.dados_detalhados:
                # Linha de Resumo (só preenche os dados do pedido)
                dados_pedido = [
                    pedido['id'],
                    pedido['cliente_nome'],
                    pedido['data'],
                    "",  # Produto
                    "",  # Quantidade
                    "",  # Preço Unit.
                    "",  # Subtotal
                    f"{float(pedido['total']):.2f}"
                ]
                dados.append(dados_pedido)

                # Linhas de Item
                for item in pedido['itens']:
                    dados_item = [
                        "",  # ID Pedido
                        "",  # Cliente
                        "",  # Data
                        item['produto'],
                        item['quantidade'],
                        f"{float(item['preco_unit']):.2f}",
                        f"{float(item['subtotal']):.2f}",
                        ""  # Total Pedido
                    ]
                    dados.append(dados_item)
        else:
            # Lógica antiga para Clientes e Produtos
            dados = [self.tree.item(item)["values"] for item in self.tree.get_children()]
            if not dados:
                messagebox.showwarning("Aviso", "Gere um relatório antes de exportar.")
                return
            colunas = self.tree["columns"]

        arquivo = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("Arquivo CSV", "*.csv")],
            title="Salvar Relatório"
        )
        if not arquivo:
            return

        try:
            # CORREÇÃO: Usar 'delimiter=;'' para melhor compatibilidade com o Excel em Pt-Br
            with open(arquivo, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f, delimiter=';')
                writer.writerow(colunas)
                writer.writerows(dados)
            messagebox.showinfo("Sucesso", f"Relatório exportado para:\n{arquivo}")
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao exportar: {e}")

    def exportar_pdf(self):
        tipo = self.combo_tipo.get()

        if tipo == "Pedidos":
            # Usa a variável de dados detalhados
            if not self.dados_detalhados:
                messagebox.showwarning("Aviso", "Gere um relatório antes de exportar.")
                return

            # 1. CABEÇALHO ATUALIZADO (Subtotal removido)
            # Colunas: ID, Cliente, Data, Produto, Qtd, Preço Unit., Total
            colunas = ("ID", "Cliente", "Data", "Produto", "Qtd", "Preço Unit.", "Total")
            # 2. LARGURA ATUALIZADA (Largura do Subtotal 70 removida)
            # Larguras: [ID, Cliente, Data, Produto, Qtd, Preço Unit., Total]
            col_widths = [50, 100, 70, 130, 40, 70, 70]

        else:
            # Usa o conteúdo da Treeview para Clientes/Produtos
            dados = [self.tree.item(item)["values"] for item in self.tree.get_children()]
            if not dados:
                messagebox.showwarning("Aviso", "Gere um relatório antes de exportar.")
                return
            colunas = self.tree["columns"]
            col_widths = [100, 150, 150, 150]  # Padrão para Clientes/Produtos

        arquivo = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("Arquivo PDF", "*.pdf")],
            title="Salvar Relatório PDF"
        )
        if not arquivo:
            return

        try:
            c = canvas.Canvas(arquivo, pagesize=A4)
            largura, altura = A4
            y = altura - 80

            # Posições X onde cada coluna começa (após a margem de 50)
            col_starts = [50]
            for width in col_widths:
                col_starts.append(col_starts[-1] + width)

            # col_starts[0] é a margem de 50
            # col_starts[5] é o início do Preço Unit.
            # col_starts[6] é o início do Total

            def desenhar_cabecalho(y, titulo, col_nomes):
                c.setFont("Helvetica-Bold", 16)
                c.drawString(largura / 2 - c.stringWidth(titulo, "Helvetica-Bold", 16) / 2, altura - 50, titulo)

                y_pos = y
                c.setFont("Helvetica-Bold", 10)

                # Desenha o nome de cada coluna usando as posições de início
                for i, col in enumerate(col_nomes):
                    c.drawString(col_starts[i], y_pos, col)
                return y_pos - 20  # Retorna a posição y para começar a desenhar os dados

            y = desenhar_cabecalho(y, f"Relatório de {tipo}", colunas)
            c.setFont("Helvetica", 10)

            if tipo == "Pedidos":
                # LÓGICA DE DETALHE PARA PDF
                for pedido in self.dados_detalhados:

                    # Linha do Pedido Principal (Cabeçalho do Pedido)
                    c.setFont("Helvetica-Bold", 10)

                    # ID
                    c.drawString(col_starts[0], y, str(pedido['id']))
                    # Cliente
                    c.drawString(col_starts[1], y, pedido['cliente_nome'])
                    # Data
                    c.drawString(col_starts[2], y, pedido['data'])

                    # Total do Pedido (última coluna: Total -> índice 6)
                    total_formatado = f"R$ {float(pedido['total']):.2f}"
                    c.drawString(col_starts[6], y, total_formatado)

                    y -= 15

                    # Desenhar Itens (Detalhe)
                    c.setFont("Helvetica", 9)
                    for item in pedido['itens']:

                        # Produto (coluna 3)
                        c.drawString(col_starts[3], y, item['produto'])

                        # Quantidade (coluna 4)
                        c.drawString(col_starts[4], y, str(item['quantidade']))

                        # Preço Unitário (coluna 5)
                        preco_unit_formatado = f"R$ {float(item['preco_unit']):.2f}"
                        c.drawString(col_starts[5], y, preco_unit_formatado)

                        y -= 12  # Espaçamento menor para itens

                        if y < 50:
                            c.showPage()
                            y = altura - 80
                            y = desenhar_cabecalho(y, f"Relatório de {tipo} (Continuação)", colunas)
                            c.setFont("Helvetica", 9)  # Retorna a fonte do item

                    y -= 5  # Espaçamento após o pedido

                    if y < 50:
                        c.showPage()
                        y = altura - 80
                        y = desenhar_cabecalho(y, f"Relatório de {tipo} (Continuação)", colunas)
                        c.setFont("Helvetica", 9)  # Retorna a fonte do item

            else:
                # Lógica antiga para Clientes e Produtos
                col_starts = [50]
                col_widths = [100, 150, 150, 150]  # Padrão para Clientes/Produtos
                for width in col_widths:
                    col_starts.append(col_starts[-1] + width)

                for row in dados:
                    for i, valor in enumerate(row):
                        c.drawString(col_starts[i], y, str(valor))
                    y -= 15
                    if y < 50:
                        c.showPage()
                        y = altura - 80
                        y = desenhar_cabecalho(y, f"Relatório de {tipo} (Continuação)", colunas)

            c.save()
            messagebox.showinfo("Sucesso", f"PDF exportado para:\n{arquivo}")
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao exportar PDF: {e}")