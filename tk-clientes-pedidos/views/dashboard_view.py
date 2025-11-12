# views/dashboard_view.py
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox
from db import list_clientes, list_pedidos
import datetime


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
        try:
            clientes = list_clientes()
            pedidos = list_pedidos()
            total_clients = len(clientes)

            hoje = datetime.date.today()
            mes_atual, ano_atual = hoje.month, hoje.year

            pedidos_mes = [
                p
                for p in pedidos
                if int(p[2].split("-")[0]) == ano_atual
                   and int(p[2].split("-")[1]) == mes_atual
            ]
            total_pedidos_mes = len(pedidos_mes)
            soma = sum(float(p[3]) for p in pedidos_mes) if pedidos_mes else 0.0
            ticket_medio = soma / total_pedidos_mes if total_pedidos_mes else 0.0

            self.card_clientes.value_label.config(text=str(total_clients))
            self.card_pedidos.value_label.config(text=str(total_pedidos_mes))
            self.card_ticket.value_label.config(text=f"R$ {ticket_medio:.2f}")

        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível atualizar: {e}")
