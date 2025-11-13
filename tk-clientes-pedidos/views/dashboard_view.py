import sys, os

# O código abaixo é para garantir que a importação de 'db' funcione se o arquivo 'db.py' estiver em um diretório pai.
# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox
from db import list_clientes, list_pedidos
import datetime


def _is_pedido_deste_mes(pedido_data_str, ano, mes):
    """Função auxiliar para validar data do pedido com segurança."""
    # Ignora se não for string (ex: None ou outros tipos)
    if not isinstance(pedido_data_str, str):
        return False

    try:
        partes = pedido_data_str.split('-')
        if len(partes) >= 2:
            p_ano = int(partes[0])  # <--- Tenta converter o ano
            p_mes = int(partes[1])  # <--- Tenta converter o mês
            return p_ano == ano and p_mes == mes
    except (ValueError, TypeError):
        # Captura erros se int() falhar (ex: int('%f') ou int('abc'))
        return False
    return False


class DashboardView(ttk.Frame):
    def __init__(self, master):
        super().__init__(master, padding=20)
        self.pack(fill=BOTH, expand=True)
        self.create_widgets()
        self.refresh()

    def create_widgets(self):
        title = ttk.Label(
            self,
            text="📊 Dashboard",
            font=("Segoe UI", 18, "bold"),
            bootstyle="inverse-primary",
        )
        title.pack(anchor="w", pady=(0, 20))

        self.cards_frame = ttk.Frame(self)
        self.cards_frame.pack(fill=X, pady=10)

        self.card_clientes = self.create_card("Clientes", "--")
        self.card_pedidos = self.create_card("Pedidos (mês)", "--")
        self.card_ticket = self.create_card("Ticket médio", "--")

        self.card_clientes.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.card_pedidos.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        self.card_ticket.grid(row=0, column=2, padx=10, pady=10, sticky="nsew")

        for i in range(3):
            self.cards_frame.columnconfigure(i, weight=1)

        ttk.Button(
            self,
            text="Atualizar",
            bootstyle="success-outline",
            command=self.refresh,
        ).pack(anchor="e", pady=(10, 0))

    def create_card(self, title, value):
        card = ttk.Frame(self.cards_frame, padding=15, bootstyle="dark")
        label_title = ttk.Label(card, text=title, font=("Segoe UI", 11, "bold"))
        label_title.pack(anchor="w")
        label_value = ttk.Label(
            card, text=value, font=("Segoe UI", 16, "bold"), bootstyle="info"
        )
        label_value.pack(anchor="w", pady=(5, 0))
        card.value_label = label_value
        return card

    def refresh(self):
        print("--- [DIAGNÓSTICO] Método Dashboard.refresh iniciado ---")  # LOG DE INÍCIO
        try:
            clientes = list_clientes()
            pedidos = list_pedidos()
            total_clients = len(clientes)

            hoje = datetime.date.today()
            mes_atual, ano_atual = hoje.month, hoje.year

            # Filtra pedidos do mês atual
            pedidos_mes = [
                p
                for p in pedidos
                if _is_pedido_deste_mes(p[3], ano_atual, mes_atual)  # Usando p[3] que é o índice da data
            ]

            total_pedidos_mes = len(pedidos_mes)

            # Calcula a soma com segurança
            soma = 0.0
            for p in pedidos_mes:
                try:
                    # p[4] é o índice do total no retorno de list_pedidos (id, cliente_id, cliente_nome, data, total)
                    soma += float(p[4])
                except (ValueError, TypeError, IndexError):
                    # Ignora o pedido se o valor for inválido
                    pass

            ticket_medio = soma / total_pedidos_mes if total_pedidos_mes else 0.0

            # Atualiza os valores na interface
            self.card_clientes.value_label.config(text=str(total_clients))
            self.card_pedidos.value_label.config(text=str(total_pedidos_mes))
            self.card_ticket.value_label.config(text=f"R$ {ticket_medio:.2f}")

            print("--- [DIAGNÓSTICO] Dashboard.refresh concluído ---")  # LOG DE FIM

        except Exception as e:
            print(f"--- [ERRO DIAGNÓSTICO] Falha grave no Dashboard.refresh: {e} ---")  # LOG DE ERRO
            messagebox.showerror("Erro", f"Não foi possível atualizar o Dashboard: {e}")