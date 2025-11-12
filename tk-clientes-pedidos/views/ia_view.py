# views/ia_view.py
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox
from db import list_pedidos, get_itens_pedido
from utils import analyze_pedidos_summary, build_prompt_from_summary, call_llm_api, log_action

class IAView(ttk.Frame):
    """
    Tela de Análises com IA (ttkbootstrap).
    - Busca os 5 últimos pedidos do banco
    - Gera um resumo local (produtos mais vendidos, ticket médio, etc)
    - Constrói um prompt e chama call_llm_api(provider, api_key)
    - Mostra o resultado no Text com rolagem
    """

    def __init__(self, master):
        super().__init__(master, padding=16)
        self.pack(fill=BOTH, expand=True)
        self.create_widgets()

    def create_widgets(self):
        header = ttk.Frame(self)
        header.pack(fill=X, pady=(0, 12))

        title = ttk.Label(self, text="🤖 Análises com IA", font=("Segoe UI", 16, "bold"), bootstyle="inverse-primary")
        title.pack(side=LEFT)

        # Controls (provider + api key + analyze button)
        controls = ttk.Frame(self)
        controls.pack(fill=X, pady=(6, 12))

        ttk.Label(controls, text="Provider:", width=9).pack(side=LEFT, padx=(0,4))
        self.provider_var = tk.StringVar(value="none")
        self.provider_cb = ttk.Combobox(controls, values=["none", "openai", "ollama"], textvariable=self.provider_var, width=12, state="readonly")
        self.provider_cb.pack(side=LEFT, padx=(0,8))

        ttk.Label(controls, text="API Key:", width=8).pack(side=LEFT, padx=(4,4))
        self.key_var = tk.StringVar()
        ttk.Entry(controls, textvariable=self.key_var, width=36).pack(side=LEFT, padx=(0,8))

        ttk.Button(controls, text="Analisar últimos 5", bootstyle="primary", command=self.analyze_last_5).pack(side=LEFT, padx=(6,0))
        ttk.Button(controls, text="Limpar", bootstyle="secondary", command=self.clear_text).pack(side=LEFT, padx=(6,0))

        # Result area
        box = ttk.Frame(self)
        box.pack(fill=BOTH, expand=True)

        self.txt = tk.Text(box, wrap="word", height=20)
        self.txt.pack(side=LEFT, fill=BOTH, expand=True)
        scroll = ttk.Scrollbar(box, command=self.txt.yview)
        scroll.pack(side=RIGHT, fill=Y)
        self.txt.configure(yscrollcommand=scroll.set)

    def clear_text(self):
        self.txt.delete("1.0", tk.END)

    def analyze_last_5(self):
        try:
            pedidos = list_pedidos()
            if not pedidos:
                messagebox.showinfo("Sem dados", "Não há pedidos para analisar.")
                return

            # ordenar por data (assume formato YYYY-MM-DD), pegar últimos 5
            pedidos_sorted = sorted(pedidos, key=lambda r: r[3], reverse=True)[:5]

            # montar estrutura com itens
            pedidos_with_items = []
            for p in pedidos_sorted:
                pid, cliente_id, nome, data, total = p
                itens = get_itens_pedido(pid)  # retorna (id, produto, quantidade, preco_unit)
                itens_clean = [(it[1], it[2], it[3]) for it in itens]
                pedidos_with_items.append((pid, cliente_id, nome, data, total, itens_clean))

            # resumo local
            resumo = analyze_pedidos_summary([
                (pid, cid, nome, data, total, itens) for pid, cid, nome, data, total, itens in pedidos_with_items
            ])
            prompt = build_prompt_from_summary(resumo)

            provider = self.provider_var.get().strip() or "none"
            api_key = self.key_var.get().strip() or None

            # Chamada ao "gancho" de LLM — por padrão retorna resposta simulada
            resposta = call_llm_api(prompt, provider=provider, api_key=api_key)

            # Mostrar resultado
            self.txt.delete("1.0", tk.END)
            header = f"== Resumo local gerado ({len(pedidos_with_items)} pedidos) ==\n\n"
            self.txt.insert(tk.END, header)
            # inserir resumo legível
            self.txt.insert(tk.END, f"Total de pedidos analisados: {resumo.get('total_pedidos',0)}\n")
            self.txt.insert(tk.END, f"Soma total: R$ {resumo.get('soma_total',0):.2f}\n")
            self.txt.insert(tk.END, f"Ticket médio: R$ {resumo.get('ticket_medio',0):.2f}\n\n")
            self.txt.insert(tk.END, "Produtos mais vendidos:\n")
            for prod, qtd in resumo.get("produtos_mais_vendidos", []):
                self.txt.insert(tk.END, f" - {prod}: {qtd} unidades\n")
            self.txt.insert(tk.END, "\n=== Resposta da IA / Gancho ===\n\n")
            self.txt.insert(tk.END, resposta)

            # registrar ação
            try:
                log_action("Analyze", "Pedidos", note=f"provider={provider}")
            except Exception:
                # log_action pode não existir dependendo da utils — silenciar erro não crítico
                pass

        except Exception as e:
            messagebox.showerror("Erro", f"Falha na análise: {e}")
