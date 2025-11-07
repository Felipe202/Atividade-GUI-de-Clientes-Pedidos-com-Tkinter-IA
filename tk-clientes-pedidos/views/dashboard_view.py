# views/dashboard_view.py
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import tkinter as tk
from tkinter import ttk, messagebox
from db import list_clientes, list_pedidos
from utils import show_info

class DashboardFrame(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.pack(fill="both", expand=True, padx=10, pady=10)
        self.create_widgets()
        self.refresh()

    def create_widgets(self):
        self.lbl_clients = ttk.Label(self, text="Clientes: --", font=("TkDefaultFont", 12))
        self.lbl_clients.grid(row=0, column=0, sticky="w", padx=4, pady=4)

        self.lbl_pedidos_mes = ttk.Label(self, text="Pedidos (mês): --", font=("TkDefaultFont", 12))
        self.lbl_pedidos_mes.grid(row=1, column=0, sticky="w", padx=4, pady=4)

        self.lbl_ticket = ttk.Label(self, text="Ticket médio: --", font=("TkDefaultFont", 12))
        self.lbl_ticket.grid(row=2, column=0, sticky="w", padx=4, pady=4)

        ttk.Button(self, text="Atualizar", command=self.refresh).grid(row=3, column=0, sticky="w", padx=4, pady=8)

    def refresh(self):
        try:
            clientes = list_clientes()
            pedidos = list_pedidos()
            total_clients = len(clientes)
            # pedidos do mês atual
            import datetime
            hoje = datetime.date.today()
            mes_atual = hoje.month
            ano_atual = hoje.year
            pedidos_mes = [p for p in pedidos if int(p[3].split("-")[0]) == ano_atual and int(p[3].split("-")[1]) == mes_atual] if pedidos else []
            total_pedidos_mes = len(pedidos_mes)
            soma = sum(float(p[4]) for p in pedidos_mes) if pedidos_mes else 0.0
            ticket_medio = (soma / total_pedidos_mes) if total_pedidos_mes else 0.0

            self.lbl_clients.config(text=f"Clientes: {total_clients}")
            self.lbl_pedidos_mes.config(text=f"Pedidos (mês): {total_pedidos_mes}")
            self.lbl_ticket.config(text=f"Ticket médio: R$ {ticket_medio:.2f}")
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível atualizar: {e}")
